#!/usr/bin/env python3
"""
Text processing and cleaning service.
"""

from typing import Optional
from openai import OpenAI

from config import OCRConfig
from retry_handler import RetryHandler


class TextProcessor:
    """Handles text cleaning and processing operations."""
    
    def __init__(self, client: Optional[OpenAI], config: OCRConfig):
        """
        Initialize text processor.
        
        Args:
            client: OpenAI client for text cleaning
            config: OCR configuration (for retry settings and model)
        """
        self.client = client
        self.config = config
    
    def clean_extracted_text(self, raw_text: str) -> str:
        """
        Clean extracted text by removing unnecessary characters and LLM-generated separators.
        
        Args:
            raw_text: Raw OCR extracted text
            
        Returns:
            Cleaned text
            
        Raises:
            RuntimeError: If client is not initialized
        """
        if not self.client:
            raise RuntimeError("GitHub client not initialized. Cannot perform text cleaning.")
            
        print("Cleaning extracted text...")
        
        if not raw_text.strip():
            return raw_text
        
        def _make_cleaning_api_call():
            # Type assertion - caller ensures client is not None
            assert self.client is not None
            return self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a text cleaning assistant. "
                                   "Your job is to clean up OCR-extracted text by removing unnecessary elements while preserving the actual content. "
                                   "Follow these rules strictly:\n\n"
                                   "1. Remove any OCR artifacts like '--- OCR Start ---', '--- OCR End ---', '--- Page X ---', or similar separators\n"
                                   "2. Remove excessive newline characters (more than 2 consecutive \\n)\n"
                                   "3. Remove any metadata or processing comments added by OCR systems\n"
                                   "4. Remove any emoji characters\n"
                                   "5. Remove inline references such as superscript numbers, footnote markers (e.g., [1], (1), or ^1), and any other common citation indicators embedded within the text.\n"
                                   "6. Fix obvious OCR errors in spacing (like 'w o r d s' -> 'words')\n"
                                   "7. Preserve original paragraph structure and remove unnecessary line breaks\n"
                                   "8. Keep all actual content text intact\n"
                                   "9. Do not add any commentary, explanations, or your own text\n"
                                   "10. Return only the cleaned text content"
                    },
                    {
                        "role": "user", 
                        "content": f"Please clean the following OCR-extracted text:\n\n{raw_text}"
                    }
                ],
                model=self.config.model_name,
                temperature=0.1  # Low temperature for consistent cleaning
            )
        
        try:
            response = RetryHandler.retry_with_backoff(_make_cleaning_api_call, self.config.max_retries)
            assert response.choices, "No choices returned from API response"
            cleaned_text = response.choices[0].message.content
            if cleaned_text:
                cleaned_text = cleaned_text.strip()
                print(f"Text cleaned: {len(raw_text)} -> {len(cleaned_text)} characters")
                return cleaned_text
            else:
                print("Warning: Text cleaning returned empty result, using original text")
                return raw_text
                
        except Exception as e:
            print(f"Error cleaning text after {self.config.max_retries} retries: {str(e)}")
            print("Using original text without cleaning")
            return raw_text
