#!/usr/bin/env python3
"""
Command-line interface for the Book OCR to TTS Pipeline.
"""

import argparse
import os
import sys
from typing import Optional

from .config import PipelineConfig


class CLIArgumentParser:
    """Handles command-line argument parsing."""
    
    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(description="OCR images and convert to speech")
        
        # Input/Output arguments
        parser.add_argument("--input_dir", help="Directory containing images")
        parser.add_argument("--input_text", help="Text file to use as input (for TTS-only processing)")
        parser.add_argument("--output_audio", help="Output audio file path (.wav)")
        parser.add_argument("--output_text", help="Optional: Save final processed text to file")
        parser.add_argument("--output_raw_text", help="Optional: Save raw OCR text to file (auto-generated if not specified)")
        parser.add_argument("--output_cleaned_text", help="Optional: Save cleaned text to file (auto-generated if not specified)")
        
        # Processing options
        parser.add_argument("--disable_auto_text_save", action="store_true",
                           help="Disable automatic saving of raw and cleaned text files")
        parser.add_argument("--skip_cleaning", action="store_true",
                           help="Skip text cleaning step and use raw OCR output")
        parser.add_argument("--start_from", choices=["ocr", "cleaning", "translation", "tts"], default="ocr",
                           help="Start processing from specific step: ocr, cleaning, translation, or tts (default: ocr)")
        parser.add_argument("--no_resume", action="store_true",
                           help="Start fresh without resuming from previous progress")
        
        # OCR configuration
        parser.add_argument("--token_path", default="access_token/github_pat",
                           help="Path to GitHub token file")
        parser.add_argument("--model_name", default="openai/o4-mini",
                           help="OCR model name. Options: openai/o4-mini, openai/gpt-4o, openai/gpt-4o-mini, etc. (default: openai/o4-mini)")
        parser.add_argument("--endpoint", default="https://models.github.ai/inference",
                           help="API endpoint URL (default: https://models.github.ai/inference)")
        parser.add_argument("--delay", type=float, default=1.0,
                           help="Delay between API calls in seconds (default: 1.0)")
        parser.add_argument("--max_retries", type=int, default=3,
                           help="Maximum number of retries for API calls (default: 3)")
        
        # TTS configuration
        parser.add_argument("--voice", default="en-US-JennyNeural", 
                           help="TTS voice (default: en-US-JennyNeural)")
        parser.add_argument("--audio_bitrate", default="48k",
                           help="Audio bitrate for compressed output (default: 48k)")
        
        # Translation configuration
        parser.add_argument("--source_language", default="auto",
                           help="Source language for translation ('auto' for automatic detection, default: auto)")
        parser.add_argument("--target_language", default="English",
                           help="Target language for translation (default: English)")
        parser.add_argument("--skip_translation", action="store_true",
                           help="Skip translation step (default: skip)")
        parser.add_argument("--output_translated_text",
                           help="Optional: Save translated text to file (auto-generated if not specified)")
        parser.add_argument("--disable_auto_translation_save", action="store_true",
                           help="Disable automatic saving of translated text file")
        
        # Progress management
        parser.add_argument("--progress_file", default="ocr_progress.json",
                           help="Path to progress tracking file (default: ocr_progress.json)")
        parser.add_argument("--show_progress", action="store_true",
                           help="Show summary of saved progress sessions and exit")
        parser.add_argument("--cleanup_progress", type=int, metavar="DAYS",
                           help="Clean up progress sessions older than DAYS and exit")
        
        return parser
    
    @staticmethod
    def validate_arguments(args) -> None:
        """
        Validate command-line arguments.
        
        Args:
            args: Parsed command-line arguments
            
        Raises:
            SystemExit: If validation fails
        """
        # Handle special commands that don't require full processing
        if args.show_progress or args.cleanup_progress is not None:
            return
        
        # Validate required arguments for normal processing
        if not args.output_audio:
            print("Error: --output_audio is required for processing")
            sys.exit(1)
        
        # Validate input sources
        if args.start_from == "tts" and args.input_text:
            # TTS-only mode with text file input
            if not os.path.isfile(args.input_text):
                print(f"Error: Input text file does not exist: {args.input_text}")
                sys.exit(1)
        elif args.start_from in ["ocr", "cleaning"] or not args.input_text:
            # OCR-based processing - need input directory
            if not args.input_dir:
                print("Error: --input_dir is required when starting from OCR or cleaning steps")
                sys.exit(1)
            if not os.path.isdir(args.input_dir):
                print(f"Error: Input directory does not exist: {args.input_dir}")
                sys.exit(1)


class CLIInterface:
    """Main command-line interface controller."""
    
    def __init__(self):
        """Initialize CLI interface."""
        self.parser = CLIArgumentParser.create_parser()
    
    def parse_arguments(self, argv: Optional[list] = None) -> argparse.Namespace:
        """
        Parse command-line arguments.
        
        Args:
            argv: Optional argument list (defaults to sys.argv)
            
        Returns:
            Parsed arguments
        """
        args = self.parser.parse_args(argv)
        CLIArgumentParser.validate_arguments(args)
        return args
    
    def create_config_from_args(self, args: argparse.Namespace) -> PipelineConfig:
        """
        Create pipeline configuration from command-line arguments.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            Pipeline configuration
        """
        return PipelineConfig.from_args(args)
