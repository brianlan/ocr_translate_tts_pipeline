#!/usr/bin/env python3
"""
Configuration management for the Book OCR to TTS Pipeline.
"""

from dataclasses import dataclass


@dataclass
class OCRConfig:
    """Configuration for OCR operations."""
    github_token_path: str = "access_token/github_pat"
    endpoint: str = "https://models.github.ai/inference"
    model_name: str = "openai/o4-mini"
    max_retries: int = 3
    delay_seconds: float = 1.0


@dataclass
class TTSConfig:
    """Configuration for Text-to-Speech operations."""
    voice: str = "en-US-JennyNeural"
    audio_bitrate: str = "48k"
    max_chunk_size: int = 5000


@dataclass
class ProcessingConfig:
    """Configuration for text processing."""
    skip_cleaning: bool = False
    enable_auto_text_save: bool = True
    progress_file: str = "ocr_progress.json"


@dataclass
class TranslationConfig:
    """Configuration for translation operations."""
    source_language: str = "auto"  # "auto" for automatic detection
    target_language: str = "English"
    skip_translation: bool = True  # Skip translation by default
    enable_auto_translation_save: bool = True


@dataclass
class PipelineConfig:
    """Main configuration container for the pipeline."""
    ocr: OCRConfig
    tts: TTSConfig
    processing: ProcessingConfig
    translation: TranslationConfig
    
    @classmethod
    def create_default(cls) -> 'PipelineConfig':
        """Create a default configuration."""
        return cls(
            ocr=OCRConfig(),
            tts=TTSConfig(),
            processing=ProcessingConfig(),
            translation=TranslationConfig()
        )
    
    @classmethod
    def from_args(cls, args) -> 'PipelineConfig':
        """Create configuration from command line arguments."""
        return cls(
            ocr=OCRConfig(
                github_token_path=args.token_path,
                endpoint=args.endpoint,
                model_name=args.model_name,
                max_retries=args.max_retries,
                delay_seconds=args.delay
            ),
            tts=TTSConfig(
                voice=args.voice,
                audio_bitrate=args.audio_bitrate
            ),
            processing=ProcessingConfig(
                skip_cleaning=args.skip_cleaning,
                enable_auto_text_save=not args.disable_auto_text_save,
                progress_file=args.progress_file
            ),
            translation=TranslationConfig(
                source_language=getattr(args, 'source_language', 'auto'),
                target_language=getattr(args, 'target_language', 'English'),
                skip_translation=getattr(args, 'skip_translation', True),
                enable_auto_translation_save=not getattr(args, 'disable_auto_translation_save', False)
            )
        )
