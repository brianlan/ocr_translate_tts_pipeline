#!/usr/bin/env python3
"""
Example usage of the book_ocr_tts.py script

This script demonstrates how to use the OCR to TTS pipeline.
"""

def main():
    # Example usage of the book_ocr_tts.py script
    print("Example usage of book_ocr_tts.py:")
    print()
    
    # Basic usage
    print("1. Basic usage:")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav")
    print()
    
    # Text output options
    print("2. Save text files (automatic save enabled by default):")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav")
    print("   # Automatically saves:")
    print("   # - output_raw.txt (raw OCR text)")
    print("   # - output_cleaned.txt (cleaned text)")
    print()
    
    # Custom text output paths
    print("3. Custom text output paths:")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav \\")
    print("    --output_raw_text my_raw_text.txt --output_cleaned_text my_cleaned_text.txt")
    print()
    
    # Disable automatic text saving
    print("4. Disable automatic text saving:")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --disable_auto_text_save")
    print()
    
    # Legacy text output (final processed text)
    print("5. Save final processed text (legacy option):")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --output_text final_text.txt")
    print()
    
    # With custom voice
    print("6. Use different TTS voice:")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --voice en-US-AriaNeural")
    print()
    
    # With different OCR model
    print("7. Use different OCR model:")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --model_name openai/gpt-4o")
    print()
    
    # With different API endpoint
    print("8. Use different API endpoint:")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --endpoint https://api.openai.com/v1")
    print()
    
    # Skip text cleaning
    print("9. Skip text cleaning (use raw OCR output):")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --skip_cleaning")
    print()
    
    # Compressed audio output
    print("10. Use compressed audio output:")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --audio_bitrate 32k")
    print()
    
    # Full custom configuration
    print("11. Full custom configuration:")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --delay 2.0 --token_path /path/to/token --model_name openai/gpt-4o-mini --endpoint https://your-custom-api.com/v1")
    print()
    
    # With retry configuration and progress management
    print("12. Configure retry behavior and progress tracking:")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --max_retries 5 --progress_file my_progress.json")
    print()
    
    # Resume processing
    print("13. Resume interrupted processing:")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav")
    print("# The script will automatically resume from where it left off")
    print()
    
    # Start fresh without resuming
    print("14. Start fresh without resuming:")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --no_resume")
    print()
    
    # Resume from specific steps
    print("14. Resume from text cleaning step:")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --start_from cleaning")
    print()
    
    print("15. TTS-only processing from text file:")
    print("python book_ocr_tts.py --input_text extracted_text.txt --output_audio output.wav --start_from tts")
    print()
    
    print("16. Resume from TTS step using completed OCR session:")
    print("python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --start_from tts")
    print()

    # Show progress summary
    print("17. View saved progress sessions:")
    print("python book_ocr_tts.py --show_progress")
    print()
    
    # Clean up old progress sessions
    print("18. Clean up old progress sessions (older than 7 days):")
    print("python book_ocr_tts.py --cleanup_progress 7")
    print()
    
    # Common API endpoints
    print("Common API endpoints:")
    endpoints = [
        "https://models.github.ai/inference (default, GitHub Models)",
        "https://api.openai.com/v1 (OpenAI direct)",
        "https://api.anthropic.com/v1 (Anthropic Claude)",
        "https://your-local-server:8000/v1 (local deployment)",
        "https://your-azure-endpoint.openai.azure.com/ (Azure OpenAI)"
    ]
    for endpoint in endpoints:
        print(f"  - {endpoint}")
    print()
    
    # Common OCR models
    print("Common OCR models:")
    models = [
        "openai/o4-mini (default, fast and efficient)",
        "openai/gpt-4o (higher accuracy, slower)",
        "openai/gpt-4o-mini (good balance of speed and accuracy)",
        "openai/gpt-4-turbo (alternative option)"
    ]
    for model in models:
        print(f"  - {model}")
    print()
    
    # Common TTS voices
    print("Common TTS voices:")
    voices = [
        "en-US-JennyNeural (default)",
        "en-US-AriaNeural",
        "en-US-GuyNeural", 
        "en-US-DavisNeural",
        "en-GB-SoniaNeural",
        "en-GB-RyanNeural",
        "zh-CN-XiaoxiaoNeural",
        "zh-CN-YunxiNeural"
    ]
    for voice in voices:
        print(f"  - {voice}")
    print()
    
    print("Note: Make sure you have the GitHub PAT token in access_token/github_pat")
    print("or specify a custom path with --token_path")
    print("When using different endpoints, ensure your token/API key is compatible")

if __name__ == "__main__":
    main()
