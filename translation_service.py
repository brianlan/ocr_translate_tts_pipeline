#!/usr/bin/env python3
"""
Translation service for the Book OCR to TTS Pipeline.
Handles text translation using LLM.
"""

from openai import OpenAI

from config import OCRConfig
from retry_handler import RetryHandler


class TranslationService:
    """Service for translating text using LLM."""
    
    def __init__(self, client: OpenAI, config: OCRConfig):
        """
        Initialize the translation service.
        
        Args:
            client: OpenAI client instance
            config: OCR configuration (reused for LLM settings)
        """
        self.client = client
        self.config = config
    
    def translate_text(
        self, 
        text: str, 
        source_language: str, 
        target_language: str
    ) -> str:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_language: Source language (e.g., "English", "Chinese", "Spanish")
            target_language: Target language (e.g., "English", "Chinese", "Spanish")
            
        Returns:
            Translated text
            
        Raises:
            Exception: If translation fails after all retries
        """
        if not text or not text.strip():
            return ""
        
        print(f"🌐 Translating from {source_language} to {target_language}...")
        print(f"📝 Input text length: {len(text):,} characters")
        
        # Create translation prompt
        prompt = self._create_translation_prompt(text, source_language, target_language)
        
        # Perform translation with retry
        def _translate():
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator with expertise in multiple languages. Your task is to provide accurate, natural, and culturally appropriate translations while preserving the original meaning, tone, and style."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=len(text) * 3,  # Allow for expansion during translation
                temperature=0.1  # Low temperature for consistent translations
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        
        try:
            translated_text = RetryHandler.retry_with_backoff(
                _translate,
                max_retries=self.config.max_retries
            )
            
            print("✅ Translation completed")
            print(f"📄 Output text length: {len(translated_text):,} characters")
            
            return translated_text
            
        except Exception as e:
            error_msg = f"[Error] Translation failed: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def _create_translation_prompt(
        self, 
        text: str, 
        source_language: str, 
        target_language: str
    ) -> str:
        """
        Create a detailed translation prompt for the LLM.
        
        Args:
            text: Text to translate
            source_language: Source language
            target_language: Target language
            
        Returns:
            Translation prompt
        """
        prompt = f"""Please translate the following text from {source_language} to {target_language}.

TRANSLATION GUIDELINES:
1. Maintain the original meaning and context
2. Use natural, fluent language in the target language
3. Preserve the tone and style of the original text
4. Keep proper nouns, names, and technical terms appropriate for the target language
5. Maintain paragraph structure and formatting
6. If certain phrases don't have direct translations, provide the most appropriate equivalent
7. For technical or specialized content, prioritize accuracy over literal translation
8. If the source language is incorrect or the text contains multiple languages, please translate the predominant language content

IMPORTANT:
- Provide ONLY the translated text in your response
- Do not include explanations, notes, or meta-commentary
- Do not add prefixes like "Translation:" or "Here is the translation:"
- Maintain the original text structure including line breaks and paragraphs

TEXT TO TRANSLATE:
---
{text}
---

Please provide the {target_language} translation:"""
        
        return prompt
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language name
        """
        if not text or not text.strip():
            return "Unknown"
        
        # Use a sample of the text for detection (first 1000 characters)
        sample_text = text[:1000]
        
        prompt = f"""Please identify the primary language of the following text.

INSTRUCTIONS:
- Provide only the language name in English (e.g., "English", "Traditional Chinese", "Simplified Chinese", "Spanish", "French", "German", etc.)
- If the text contains multiple languages, identify the predominant one
- If the language cannot be determined, respond with "Unknown"
- Do not provide explanations or additional information

TEXT TO ANALYZE:
---
{sample_text}
---

Language:"""
        
        def _detect():
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a language detection expert. Identify the primary language of the given text accurately."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=50,
                temperature=0.1
            )
            content = response.choices[0].message.content
            return content.strip() if content else "Unknown"
        
        try:
            detected_language = RetryHandler.retry_with_backoff(
                _detect,
                max_retries=self.config.max_retries
            )
            
            print(f"🔍 Detected language: {detected_language}")
            return detected_language
            
        except Exception as e:
            print(f"❌ Language detection failed: {str(e)}")
            return "Unknown"
