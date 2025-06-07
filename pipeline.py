#!/usr/bin/env python3
"""
Main pipeline orchestration for Book OCR to TTS processing.
"""

import os
import time
from typing import List, Optional

from .config import PipelineConfig
from .ocr_service import OCRService
from .tts_service import TTSService
from .text_processor import TextProcessor
from .translation_service import TranslationService
from .progress_tracker import ProgressTracker, ProcessingStats
from .file_manager import FileManager


class BookOCRTTSPipeline:
    """Main pipeline for processing images through OCR and converting to speech."""
    
    def __init__(self, config: PipelineConfig):
        """
        Initialize the pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config
        self._ocr_service = None
        self._text_processor = None
        self._translation_service = None
        self.tts_service = TTSService(config.tts)
        self.progress_tracker = ProgressTracker(config.processing.progress_file)
    
    @property
    def ocr_service(self):
        """Lazy initialization of OCR service."""
        if self._ocr_service is None:
            self._ocr_service = OCRService(self.config.ocr)
        return self._ocr_service
    
    @property
    def text_processor(self):
        """Lazy initialization of text processor."""
        if self._text_processor is None:
            self._text_processor = TextProcessor(self.ocr_service.client, self.config.ocr)
        return self._text_processor
    
    @property
    def translation_service(self):
        """Lazy initialization of translation service."""
        if self._translation_service is None:
            # Ensure OCR service is initialized to get the client
            if self.ocr_service.client is None:
                raise RuntimeError("OCR service client not initialized. Cannot create translation service.")
            self._translation_service = TranslationService(self.ocr_service.client, self.config.ocr)
        return self._translation_service
    
    def process_images_to_text(self, input_dir: str, resume: bool = True) -> str:
        """
        Process all images in directory and combine extracted text with resume capability.
        
        Args:
            input_dir: Directory containing images
            resume: Whether to resume from previous progress
            
        Returns:
            Combined extracted text
            
        Raises:
            ValueError: If input directory issues or no images found
        """
        # Get image files
        image_files = FileManager.get_image_files(input_dir)
        
        # Load existing progress if resuming
        progress_data = self.progress_tracker.load_progress() if resume else {}
        
        # Create session ID
        session_id = self.progress_tracker.create_session_id(
            input_dir, self.config.ocr.model_name, len(image_files)
        )
        
        # Initialize or load session data
        if session_id in progress_data and resume:
            print(f"📁 Resuming previous session {session_id}...")
            session_data = progress_data[session_id]
            processed_files = session_data.get('processed_files', {})
            combined_texts = session_data.get('texts', [])
            
            # Calculate current stats
            completed_count = len([f for f in processed_files.values() if f.get('success', True)])
            failed_count = len([f for f in processed_files.values() if not f.get('success', True)])
            
            print(f"📊 Found {completed_count} successful, {failed_count} failed from {len(image_files)} total images")
            
            # Validate session parameters
            if (session_data.get('input_dir') != input_dir or 
                session_data.get('model_name') != self.config.ocr.model_name or
                session_data.get('total_files') != len(image_files)):
                print("⚠️  Session parameters don't match. Starting fresh session...")
                processed_files = {}
                combined_texts = []
                completed_count = 0
                failed_count = 0
        else:
            print(f"🆕 Starting new session {session_id}...")
            processed_files = {}
            combined_texts = []
            completed_count = 0
            failed_count = 0
            
            # Initialize new session
            progress_data[session_id] = self.progress_tracker.initialize_session(
                session_id, input_dir, self.config.ocr.model_name, len(image_files)
            )
        
        # Process images
        start_time = time.time()
        stats = ProcessingStats(completed=completed_count, failed=failed_count, total=len(image_files))
        
        try:
            for i, image_path in enumerate(image_files):
                # Check if already processed
                file_hash = FileManager.create_file_hash(image_path)
                if file_hash in processed_files and processed_files[file_hash].get('success', False):
                    print(f"[{i+1}/{len(image_files)}] ✅ Skipping {os.path.basename(image_path)} (already processed)")
                    continue
                
                # Show progress
                self._show_processing_progress(i, len(image_files), stats, start_time)
                
                # Process image
                self._process_single_image(image_path, file_hash, processed_files, combined_texts, stats)
                
                # Update progress
                self.progress_tracker.update_session_progress(
                    progress_data, session_id, processed_files, combined_texts, stats
                )
                self.progress_tracker.save_progress(progress_data)
                
                # Add delay between API calls (skip for last image)
                if i < len(image_files) - 1:
                    time.sleep(self.config.ocr.delay_seconds)
            
            # Complete processing
            full_text = "".join(combined_texts)
            total_time = time.time() - start_time
            
            print("\n🎉 Processing completed!")
            print(f"📊 Results: {stats.completed} successful, {stats.failed} failed out of {stats.total} total")
            print(f"📝 Combined text contains {len(full_text):,} characters")
            print(f"⏱️  Total time: {total_time/60:.1f} minutes")
            
            if stats.failed > 0:
                print(f"⚠️  {stats.failed} files failed processing. Check the progress file for details.")
            
            # Mark session as completed
            self.progress_tracker.complete_session(progress_data, session_id, full_text, stats, total_time)
            self.progress_tracker.save_progress(progress_data)
            
            return full_text
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Processing interrupted by user")
            self.progress_tracker.interrupt_session(progress_data, session_id, stats)
            self.progress_tracker.save_progress(progress_data)
            print(f"💾 Progress saved. Processed {stats.completed}/{stats.total} images successfully.")
            print("🔄 You can resume later with the same parameters.")
            raise
        except Exception as e:
            print(f"\n❌ Error during processing: {str(e)}")
            self.progress_tracker.error_session(progress_data, session_id, str(e), stats)
            self.progress_tracker.save_progress(progress_data)
            raise
    
    def _process_single_image(
        self, 
        image_path: str, 
        file_hash: str, 
        processed_files: dict, 
        combined_texts: List[str], 
        stats: ProcessingStats
    ) -> None:
        """Process a single image and update tracking data."""
        try:
            extracted_text = self.ocr_service.extract_text_from_image(image_path)
            
            if extracted_text and not extracted_text.startswith("[Error"):
                combined_texts.append(extracted_text)
                processed_files[file_hash] = {
                    'file_path': image_path,
                    'file_name': os.path.basename(image_path),
                    'text_length': len(extracted_text),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'success': True
                }
                stats.completed += 1
                print(f"✅ Successfully processed {os.path.basename(image_path)} ({len(extracted_text)} chars)")
            else:
                processed_files[file_hash] = {
                    'file_path': image_path,
                    'file_name': os.path.basename(image_path),
                    'error': extracted_text if extracted_text.startswith("[Error") else "Unknown error",
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'success': False
                }
                stats.failed += 1
                print(f"❌ Failed to process {os.path.basename(image_path)}")
        
        except Exception as e:
            processed_files[file_hash] = {
                'file_path': image_path,
                'file_name': os.path.basename(image_path),
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'success': False
            }
            stats.failed += 1
            print(f"❌ Exception processing {os.path.basename(image_path)}: {str(e)}")
    
    def _show_processing_progress(
        self, 
        current_index: int, 
        total_files: int, 
        stats: ProcessingStats, 
        start_time: float
    ) -> None:
        """Display detailed processing progress."""
        # Calculate ETA
        elapsed_time = time.time() - start_time
        if stats.completed > 0:
            avg_time_per_image = elapsed_time / stats.completed
            estimated_remaining = avg_time_per_image * (total_files - stats.completed)
            eta_str = f", ETA: {estimated_remaining/60:.1f}m" if estimated_remaining > 60 else f", ETA: {estimated_remaining:.0f}s"
        else:
            eta_str = ""
        
        print(f"\n[{current_index+1}/{total_files}] 🔄 Processing...")
        print(f"📈 Progress: {stats.percentage:.1f}% ({stats.completed} successful, {stats.failed} failed{eta_str})")
    
    def clean_text(self, raw_text: str) -> str:
        """
        Clean extracted text.
        
        Args:
            raw_text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        return self.text_processor.clean_extracted_text(raw_text)
    
    def translate_text(self, text: str, source_language: str, target_language: str) -> str:
        """
        Translate text from source to target language.
        
        Args:
            text: Text to translate
            source_language: Source language (e.g., "English", "Chinese", "auto")
            target_language: Target language (e.g., "English", "Chinese")
            
        Returns:
            Translated text
        """
        if source_language == "auto":
            # Auto-detect source language
            detected_language = self.translation_service.detect_language(text)
            print(f"🔍 Auto-detected source language: {detected_language}")
            
            # Skip translation if already in target language
            if detected_language.lower() == target_language.lower():
                print(f"✅ Text is already in {target_language}, skipping translation")
                return text
            
            source_language = detected_language
        
        return self.translation_service.translate_text(text, source_language, target_language)
    
    async def convert_to_speech(self, text: str, output_path: str) -> None:
        """
        Convert text to speech.
        
        Args:
            text: Text to convert
            output_path: Output audio file path
        """
        await self.tts_service.text_to_speech(text, output_path)
    
    def load_previous_session_text(self, input_dir: str) -> Optional[str]:
        """
        Load text from a previous completed session.
        
        Args:
            input_dir: Input directory used in the session
            
        Returns:
            Previously extracted text if found, None otherwise
        """
        image_files = FileManager.get_image_files(input_dir)
        return self.progress_tracker.get_completed_session_text(
            input_dir, self.config.ocr.model_name, len(image_files)
        )
