#!/usr/bin/env python3
"""
File management utilities for the pipeline.
"""

import os
import glob
import hashlib
from typing import List, Tuple


class FileManager:
    """Handles file operations for the pipeline."""
    
    IMAGE_EXTENSIONS = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']
    
    @staticmethod
    def get_image_files(directory: str) -> List[str]:
        """
        Get all image files from the directory, sorted by name.
        
        Args:
            directory: Directory to search for images
            
        Returns:
            List of image file paths
            
        Raises:
            ValueError: If directory doesn't exist or no images found
        """
        if not os.path.isdir(directory):
            raise ValueError(f"Directory does not exist: {directory}")
        
        image_files = []
        
        for ext in FileManager.IMAGE_EXTENSIONS:
            image_files.extend(glob.glob(os.path.join(directory, ext), recursive=False))
            image_files.extend(glob.glob(os.path.join(directory, ext.upper()), recursive=False))
        
        if not image_files:
            raise ValueError(f"No image files found in {directory}")
        
        # Sort files to maintain order
        image_files.sort()
        print(f"Found {len(image_files)} image files")
        return image_files
    
    @staticmethod
    def create_file_hash(filepath: str) -> str:
        """
        Create a hash of the file for tracking purposes.
        
        Args:
            filepath: Path to the file
            
        Returns:
            MD5 hash of the file content
        """
        with open(filepath, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash
    
    @staticmethod
    def save_text(text: str, output_path: str) -> None:
        """
        Save text to file.
        
        Args:
            text: Text content to save
            output_path: Path where to save the file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Text saved to: {output_path}")
    
    @staticmethod
    def load_text(file_path: str) -> str:
        """
        Load text from file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Text content from the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If there's an error reading the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"✅ Loaded text from {file_path} ({len(text):,} characters)")
            return text
        except FileNotFoundError:
            raise FileNotFoundError(f"Text file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")
    
    @staticmethod
    def generate_text_output_paths(output_audio: str) -> Tuple[str, str]:
        """
        Generate automatic paths for raw and cleaned text files based on audio output path.
        
        Args:
            output_audio: Path to the output audio file
            
        Returns:
            Tuple of (raw_text_path, cleaned_text_path)
        """
        base_path = os.path.splitext(output_audio)[0]  # Remove extension
        raw_text_path = f"{base_path}_raw.txt"
        cleaned_text_path = f"{base_path}_cleaned.txt"
        return raw_text_path, cleaned_text_path
    
    @staticmethod
    def ensure_directory_exists(file_path: str) -> None:
        """
        Ensure that the directory for the given file path exists.
        
        Args:
            file_path: Path to a file (directory will be created if needed)
        """
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def generate_translation_text_path(output_audio: str, target_language: str) -> str:
        """
        Generate automatic path for translated text file based on audio output path.
        
        Args:
            output_audio: Path to the output audio file
            target_language: Target language for translation
            
        Returns:
            Path for translated text file
        """
        base_path = os.path.splitext(output_audio)[0]  # Remove extension
        # Create a safe filename for the language
        safe_language = target_language.lower().replace(" ", "_").replace("-", "_")
        translated_text_path = f"{base_path}_translated_{safe_language}.txt"
        return translated_text_path
