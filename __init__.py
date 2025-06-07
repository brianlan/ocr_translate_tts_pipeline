#!/usr/bin/env python3
"""
Book OCR to TTS Pipeline Package

A modular pipeline for processing images through OCR and converting to speech.
"""

from .config import PipelineConfig, OCRConfig, TTSConfig, ProcessingConfig, TranslationConfig
from .pipeline import BookOCRTTSPipeline
from .ocr_service import OCRService
from .tts_service import TTSService
from .text_processor import TextProcessor
from .translation_service import TranslationService
from .progress_tracker import ProgressTracker, ProcessingStats
from .file_manager import FileManager
from .retry_handler import RetryHandler
from .cli import CLIInterface

__version__ = "2.0.0"
__author__ = "Pipeline Development Team"

__all__ = [
    "PipelineConfig",
    "OCRConfig", 
    "TTSConfig",
    "ProcessingConfig",
    "TranslationConfig",
    "BookOCRTTSPipeline",
    "OCRService",
    "TTSService", 
    "TextProcessor",
    "TranslationService",
    "ProgressTracker",
    "ProcessingStats",
    "FileManager",
    "RetryHandler",
    "CLIInterface"
]
