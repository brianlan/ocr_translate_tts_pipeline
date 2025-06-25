#!/usr/bin/env python3
"""
Book OCR to TTS Pipeline - Main Entry Point

This script processes a directory of images by:
1. Applying OCR to extract text from all images using GitHub Models
2. Combining the extracted text into a single document
3. Converting the combined text to speech using TTS

Usage:
    python main.py --input_dir /path/to/images --output_audio /path/to/output.wav
"""

import asyncio
import sys
import os

# Handle both direct execution and module import
if __name__ == "__main__":
    # Add current directory to path for direct execution
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from cli import CLIInterface
    from pipeline import BookOCRTTSPipeline
    from progress_tracker import ProgressTracker
    from file_manager import FileManager
else:
    from .cli import CLIInterface
    from .pipeline import BookOCRTTSPipeline
    from .progress_tracker import ProgressTracker
    from .file_manager import FileManager


async def main():
    """Main application entry point."""
    try:
        # Parse command-line arguments
        cli = CLIInterface()
        args = cli.parse_arguments()
        
        # Handle special commands that don't require full processing
        if args.show_progress or args.cleanup_progress is not None:
            # Create a minimal progress tracker for these operations
            progress_tracker = ProgressTracker(args.progress_file)
            
            if args.show_progress:
                progress_tracker.show_progress_summary()
            
            if args.cleanup_progress is not None:
                progress_tracker.cleanup_old_sessions(args.cleanup_progress)
            
            return
        
        # Ensure output directory exists
        FileManager.ensure_directory_exists(args.output_audio)
        
        # Create pipeline configuration
        config = cli.create_config_from_args(args)
        
        # Initialize pipeline
        print("Initializing OCR to TTS pipeline...")
        pipeline = BookOCRTTSPipeline(config)
        
        combined_text = None
        
        # Handle TTS-only mode with text file input
        if args.start_from == "tts" and args.input_text:
            print(f"\nLoading text from file: {args.input_text}")
            combined_text = FileManager.load_text(args.input_text)
        
        # Step 1: Extract text from images (if starting from OCR or no existing text found)
        elif args.start_from == "ocr":
            print(f"\nStep 1: Extracting text from images in {args.input_dir}")
            if args.no_resume:
                print("🔄 Starting fresh (resume disabled)")
            
            combined_text = pipeline.process_images_to_text(
                input_dir=args.input_dir,
                resume=not args.no_resume
            )
        
        # Try to load existing text if starting from cleaning or translation
        elif args.start_from in ["cleaning", "translation"]:
            print("\nAttempting to load previously extracted text...")
            combined_text = pipeline.load_previous_session_text(args.input_dir)
            
            if not combined_text:
                print("❌ No completed OCR session found. Running OCR step first...")
                print(f"\nStep 1: Extracting text from images in {args.input_dir}")
                combined_text = pipeline.process_images_to_text(
                    input_dir=args.input_dir,
                    resume=not args.no_resume
                )
        
        if not combined_text or not combined_text.strip():
            print("Error: No text was extracted from images")
            sys.exit(1)
        
        # Auto-save raw OCR text (unless disabled)
        if (config.processing.enable_auto_text_save and 
            args.start_from in ["ocr", "cleaning", "translation"]):
            raw_text_path = args.output_raw_text
            if not raw_text_path:
                raw_text_path, _ = FileManager.generate_text_output_paths(args.output_audio)
            
            print(f"💾 Saving raw OCR text to: {raw_text_path}")
            FileManager.save_text(combined_text, raw_text_path)
        
        cleaned_text = combined_text
        
        # Step 2: Clean the extracted text (if not skipped and not starting from TTS)
        if args.start_from not in ["tts"] and not config.processing.skip_cleaning:
            print("\nStep 2: Cleaning extracted text...")
            cleaned_text = pipeline.clean_text(combined_text)
            
            # Auto-save cleaned text (unless disabled)
            if config.processing.enable_auto_text_save:
                cleaned_text_path = args.output_cleaned_text
                if not cleaned_text_path:
                    _, cleaned_text_path = FileManager.generate_text_output_paths(args.output_audio)
                
                print(f"💾 Saving cleaned text to: {cleaned_text_path}")
                FileManager.save_text(cleaned_text, cleaned_text_path)
                
        elif config.processing.skip_cleaning:
            print("\nStep 2: Skipping text cleaning (using raw OCR output)")
        elif args.start_from == "tts":
            print("\nStep 2: Skipping text cleaning (starting from TTS)")
        
        # Step 3: Translate text (if not skipped and not starting from TTS)
        translated_text = cleaned_text
        if args.start_from not in ["tts"] and not config.translation.skip_translation:
            print(f"\nStep 3: Translating text from {config.translation.source_language} to {config.translation.target_language}...")
            translated_text = pipeline.translate_text(
                cleaned_text, 
                config.translation.source_language, 
                config.translation.target_language
            )
            
            # Auto-save translated text (unless disabled)
            if config.translation.enable_auto_translation_save:
                translated_text_path = args.output_translated_text
                if not translated_text_path:
                    translated_text_path = FileManager.generate_translation_text_path(
                        args.output_audio, config.translation.target_language
                    )
                
                print(f"💾 Saving translated text to: {translated_text_path}")
                FileManager.save_text(translated_text, translated_text_path)
                
        elif config.translation.skip_translation:
            print("\nStep 3: Skipping translation (using cleaned text)")
        elif args.start_from == "tts":
            print("\nStep 3: Skipping translation (starting from TTS)")
        
        # Step 4: Save text if requested
        if args.output_text:
            FileManager.save_text(translated_text, args.output_text)
        
        # Step 5: Convert to speech
        if args.start_from in ["ocr", "cleaning", "translation", "tts"]:
            print("\nStep 4: Converting text to speech...")
            await pipeline.convert_to_speech(translated_text, args.output_audio)
        
        print("\nPipeline completed successfully!")
        print(f"🎵 Audio output: {args.output_audio}")
        
        # Report saved text files
        if (config.processing.enable_auto_text_save and 
            args.start_from in ["ocr", "cleaning"]):
            raw_text_path = args.output_raw_text
            if not raw_text_path:
                raw_text_path, _ = FileManager.generate_text_output_paths(args.output_audio)
            print(f"📄 Raw OCR text: {raw_text_path}")
            
            if args.start_from != "tts" and not config.processing.skip_cleaning:
                cleaned_text_path = args.output_cleaned_text
                if not cleaned_text_path:
                    _, cleaned_text_path = FileManager.generate_text_output_paths(args.output_audio)
                print(f"✨ Cleaned text: {cleaned_text_path}")
        
        if args.output_text:
            print(f"📝 Final text output: {args.output_text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
