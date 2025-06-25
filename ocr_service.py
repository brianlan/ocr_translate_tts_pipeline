#!/usr/bin/env python3
"""
OCR service for extracting text from images using GitHub Models.
"""

import os
import base64
from typing import Optional
from openai import OpenAI

from config import OCRConfig
from retry_handler import RetryHandler


class OCRService:
    """Handles OCR operations using GitHub Models."""
    
    def __init__(self, config: OCRConfig):
        """
        Initialize OCR service.
        
        Args:
            config: OCR configuration
        """
        self.config = config
        self.client: Optional[OpenAI] = None
        self._setup_client()
    
    def _setup_client(self) -> None:
        """Setup GitHub Models client for OCR."""
        try:
            with open(self.config.github_token_path, "r") as file:
                token = file.read().strip()
            
            if not token:
                raise ValueError("GitHub token is empty")
                
        except FileNotFoundError:
            raise FileNotFoundError(f"GitHub token not found at {self.config.github_token_path}")
        except Exception as e:
            raise Exception(f"Error reading GitHub token: {str(e)}")
        
        # Create client
        self.client = OpenAI(base_url=self.config.endpoint, api_key=token)
        
        # Test the connection
        try:
            models = self.client.models.list()
            print(f"✓ Successfully connected to {self.config.endpoint}. Models available: {len(models.data)}")
        except Exception as e:
            print(f"⚠️  Warning: Could not validate API connection: {str(e)}")
            print("Proceeding anyway, but you may encounter errors during processing.")
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode image file to base64 string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
        return base64.b64encode(image_bytes).decode("utf-8")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from a single image using GitHub Models OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text content
            
        Raises:
            RuntimeError: If client is not initialized
        """
        if not self.client:
            raise RuntimeError("GitHub client not initialized. Cannot perform OCR.")
            
        print(f"Processing: {os.path.basename(image_path)}")
        
        def _make_api_call():
            b64_image = self._encode_image_to_base64(image_path)
            
            # Type assertion - we've already checked self.client is not None above
            assert self.client is not None
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "developer",
                        "content": "You are a helpful assistant that specializes in optical character recognition (OCR). Extract all text from images accurately, maintaining the original structure and formatting as much as possible."
                    },
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{b64_image}"
                                }
                            },
                            {
                                "type": "text",
                                "text": "Please extract all text from this image. Maintain the original structure, paragraph breaks, and formatting. If there are multiple columns, read from left to right, top to bottom. Only return the extracted text without any additional commentary."
                            }
                        ]
                    }
                ],
                model=self.config.model_name
            )
            return response
        
        try:
            response = RetryHandler.retry_with_backoff(_make_api_call, self.config.max_retries)
            
            extracted_text = response.choices[0].message.content
            if extracted_text:
                extracted_text = extracted_text.strip()
            else:
                extracted_text = ""
            
            print(f"Extracted {len(extracted_text)} characters from {os.path.basename(image_path)}")
            return extracted_text
            
        except Exception as e:
            print(f"Error processing {image_path} after {self.config.max_retries} retries: {str(e)}")
            return f"[Error processing {os.path.basename(image_path)}]"
