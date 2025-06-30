#!/usr/bin/env python3
"""
Simple Text-to-Speech Script

This script takes a text file as input and produces an audio file using existing TTS services.
It supports optional text cleaning and translation steps.

Usage:
    python run_tts.py input.txt output.wav
    python run_tts.py input.txt output.wav --skip-cleaning
    python run_tts.py input.txt output.wav --skip-translation
    python run_tts.py input.txt output.wav --source-lang Chinese --target-lang English
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path

# Import existing services
from config import PipelineConfig, OCRConfig, TTSConfig, ProcessingConfig, TranslationConfig
from file_manager import FileManager
from tts_service import TTSService
from text_processor import TextProcessor
from translation_service import TranslationService
from ocr_service import OCRService


class SimpleTTSRunner:
    """Simple wrapper for text-to-speech conversion with optional processing."""
    
    def __init__(self, skip_cleaning: bool = False, skip_translation: bool = False,
                 source_lang: str = "auto", target_lang: str = "English",
                 voice: str = "en-US-JennyNeural", 
                 model_name: str = "openai/o4-mini",
                 endpoint: str = "https://models.github.ai/inference",
                 token_path: str = "access_token/github_pat"):
        """
        Initialize the TTS runner.
        
        Args:
            skip_cleaning: Skip text cleaning step
            skip_translation: Skip translation step
            source_lang: Source language for translation
            target_lang: Target language for translation
            voice: TTS voice to use
            model_name: Model name for text processing and translation
            endpoint: API endpoint for the model
            token_path: Path to the authentication token file
        """
        # Create configuration
        self.config = PipelineConfig(
            ocr=OCRConfig(
                model_name=model_name,
                endpoint=endpoint,
                github_token_path=token_path
            ),
            tts=TTSConfig(voice=voice),
            processing=ProcessingConfig(skip_cleaning=skip_cleaning),
            translation=TranslationConfig(
                source_language=source_lang,
                target_language=target_lang,
                skip_translation=skip_translation
            )
        )
        
        # Initialize services (lazy loading for efficiency)
        self._ocr_service = None
        self._text_processor = None
        self._translation_service = None
        self.tts_service = TTSService(self.config.tts)
        
        self.skip_cleaning = skip_cleaning
        self.skip_translation = skip_translation
    
    @property
    def ocr_service(self):
        """Lazy initialization of OCR service (needed for text processing and translation)."""
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
            # Ensure OCR service client is initialized
            if self.ocr_service.client is None:
                raise RuntimeError("OCR service client not initialized. Cannot create translation service.")
            self._translation_service = TranslationService(self.ocr_service.client, self.config.ocr)
        return self._translation_service
    
    def clean_text(self, text: str) -> str:
        """
        Clean the input text using the existing text processor.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if self.skip_cleaning:
            print("⏭️  Skipping text cleaning")
            return text
        
        print("🧹 Cleaning text...")
        return self.text_processor.clean_extracted_text(text)
    
    def translate_text(self, text: str) -> str:
        """
        Translate text if translation is enabled.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text (or original if translation is skipped)
        """
        if self.skip_translation:
            print("⏭️  Skipping translation")
            return text
        
        source_lang = self.config.translation.source_language
        target_lang = self.config.translation.target_language
        
        print(f"🌐 Translating from {source_lang} to {target_lang}...")
        
        if source_lang == "auto":
            # Auto-detect source language
            detected_language = self.translation_service.detect_language(text)
            print(f"🔍 Auto-detected source language: {detected_language}")
            
            # Skip translation if already in target language
            if detected_language.lower() == target_lang.lower():
                print(f"✅ Text is already in {target_lang}, skipping translation")
                return text
            
            source_lang = detected_language
        
        return self.translation_service.translate_text(text, source_lang, target_lang)
    
    async def convert_to_speech(self, text: str, output_path: str) -> None:
        """
        Convert text to speech.
        
        Args:
            text: Text to convert
            output_path: Output audio file path
        """
        print(f"🎤 Converting text to speech using voice: {self.config.tts.voice}")
        await self.tts_service.text_to_speech(text, output_path)
    
    async def process_text_to_audio(self, input_text_file: str, output_audio_file: str) -> None:
        """
        Main processing pipeline: load text -> clean -> translate -> convert to speech.
        
        Args:
            input_text_file: Path to input text file
            output_audio_file: Path to output audio file
        """
        # Step 1: Load text
        print(f"📖 Loading text from: {input_text_file}")
        text = FileManager.load_text(input_text_file)
        
        if not text.strip():
            raise ValueError("Input text file is empty")
        
        print(f"📊 Loaded {len(text):,} characters")
        
        # Step 2: Clean text (optional)
        cleaned_text = self.clean_text(text)
        with open(Path(input_text_file).with_suffix('.cleaned.txt'), 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        # Step 3: Translate text (optional)
        final_text = self.translate_text(cleaned_text)
        
        # Step 4: Convert to speech
        # Ensure output directory exists
        FileManager.ensure_directory_exists(output_audio_file)
        
        await self.convert_to_speech(final_text, output_audio_file)
        
        print(f"✅ Audio output saved to: {output_audio_file}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert text file to speech with optional cleaning and translation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tts.py input.txt output.wav
  python run_tts.py input.txt output.wav --skip-cleaning
  python run_tts.py input.txt output.wav --skip-translation
  python run_tts.py input.txt output.wav --source-lang Chinese --target-lang English --voice en-US-AriaNeural
  python run_tts.py input.txt output.wav --model-name gemini-2.5-pro-preview-03-25 --endpoint https://openai.newbotai.cn/v1 --token-path ./access_token/gemini_2
        """
    )
    
    # Required arguments
    parser.add_argument("input_text", help="Input text file path")
    parser.add_argument("output_audio", help="Output audio file path")
    
    # Optional processing flags
    parser.add_argument("--skip-cleaning", action="store_true",
                        help="Skip text cleaning step")
    parser.add_argument("--skip-translation", action="store_true", 
                        help="Skip translation step")
    
    # Translation options
    parser.add_argument("--source-lang", default="auto",
                        help="Source language for translation (default: auto-detect)")
    parser.add_argument("--target-lang", default="English",
                        help="Target language for translation (default: English)")
    
    # TTS options
    parser.add_argument("--voice", default="en-US-JennyNeural",
                        help="TTS voice to use (default: en-US-JennyNeural)")
    
    # Model configuration options
    parser.add_argument("--model-name", default="openai/o4-mini",
                        help="Model name for text processing and translation (default: openai/o4-mini)")
    parser.add_argument("--endpoint", default="https://models.github.ai/inference",
                        help="API endpoint for the model (default: https://models.github.ai/inference)")
    parser.add_argument("--token-path", default="access_token/github_pat",
                        help="Path to the authentication token file (default: access_token/github_pat)")
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    try:
        args = parse_arguments()
        
        # Validate input file exists
        if not os.path.exists(args.input_text):
            print(f"Error: Input text file not found: {args.input_text}")
            sys.exit(1)
        
        # Create TTS runner
        runner = SimpleTTSRunner(
            skip_cleaning=args.skip_cleaning,
            skip_translation=args.skip_translation,
            source_lang=args.source_lang,
            target_lang=args.target_lang,
            voice=args.voice,
            model_name=args.model_name,
            endpoint=args.endpoint,
            token_path=args.token_path
        )
        
        # Process text to audio
        print("🚀 Starting text-to-speech conversion...")
        await runner.process_text_to_audio(args.input_text, args.output_audio)
        
        print("🎉 Text-to-speech conversion completed successfully!")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
