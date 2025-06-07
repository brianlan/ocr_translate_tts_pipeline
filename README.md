# Book OCR to TTS Pipeline

A modular pipeline for processing images through OCR (Optical Character Recognition) and converting the extracted text to speech using TTS (Text-to-Speech).

## Recent Refactoring (v2.0.0)

The original `book_ocr_tts.py` script (892 lines) has been **completely refactored** into a modular, maintainable architecture:

### 🏗️ New Architecture

The monolithic script has been broken down into focused modules:

- **`config.py`** - Configuration management and settings
- **`ocr_service.py`** - OCR operations using GitHub Models
- **`tts_service.py`** - Text-to-speech conversion using Edge TTS
- **`text_processor.py`** - Text cleaning and processing
- **`progress_tracker.py`** - Session management and progress tracking
- **`file_manager.py`** - File operations and utilities
- **`retry_handler.py`** - Retry logic with exponential backoff
- **`pipeline.py`** - Main pipeline orchestration
- **`cli.py`** - Command-line interface
- **`main.py`** - Application entry point

### ✅ Benefits of Refactoring

1. **Single Responsibility Principle** - Each module has one clear purpose
2. **Improved Testability** - Modules can be unit tested independently
3. **Better Maintainability** - Changes are isolated to specific components
4. **Enhanced Readability** - Code is organized logically and easier to understand
5. **Reduced Coupling** - Components interact through well-defined interfaces
6. **Configuration Management** - Centralized settings using dataclasses
7. **Error Handling** - Dedicated retry handler with configurable policies

### 📁 File Structure

```
scripts/book_ocr_tts_pipeline/
├── __init__.py                    # Package initialization
├── book_ocr_tts.py               # Original script (deprecated, redirects to new version)
├── book_ocr_tts_refactored.py    # New entry point
├── main.py                       # Main application logic
├── config.py                     # Configuration management
├── ocr_service.py                # OCR functionality
├── tts_service.py                # TTS functionality
├── text_processor.py             # Text cleaning
├── progress_tracker.py           # Progress management
├── file_manager.py               # File operations
├── retry_handler.py              # Retry logic
├── cli.py                        # Command-line interface
└── README.md                     # This documentation
```

## Usage

### Using the Refactored Version (Recommended)

```bash
python book_ocr_tts_refactored.py --input_dir /path/to/images --output_audio /path/to/output.wav
```

### Using the Original Script (Backward Compatibility)

The original script now redirects to the refactored version:

```bash
python book_ocr_tts.py --input_dir /path/to/images --output_audio /path/to/output.wav
```

## Features

This pipeline processes a directory of images by:

1. **OCR Processing**: Extracting text from all images using GitHub Models
2. **Text Cleaning**: Removing OCR artifacts and improving formatting
3. **Translation**: Translating text between different languages (optional)
4. **Text Combination**: Combining processed text into a single document
5. **TTS Conversion**: Converting the final text to speech using Edge TTS

### Key Features

- **Resume Capability** - Continue processing from where you left off
- **Progress Tracking** - Detailed progress monitoring and session management
- **Error Handling** - Robust retry logic with exponential backoff
- **Flexible Processing** - Start from different stages (OCR, cleaning, TTS)
- **Multiple Output Formats** - Support for various audio formats
- **Automatic Text Saving** - Save raw and cleaned text automatically

## Command Line Options

### Input/Output
- `--input_dir` - Directory containing images
- `--input_text` - Text file for TTS-only processing
- `--output_audio` - Output audio file path
- `--output_text` - Save final processed text
- `--output_raw_text` - Save raw OCR text
- `--output_cleaned_text` - Save cleaned text

### Processing Control
- `--start_from` - Start from: ocr, cleaning, or tts
- `--skip_cleaning` - Skip text cleaning step
- `--no_resume` - Start fresh without resuming
- `--disable_auto_text_save` - Disable automatic text file saving

### OCR Configuration
- `--model_name` - OCR model (default: openai/o4-mini)
- `--token_path` - GitHub token file path
- `--endpoint` - API endpoint URL
- `--delay` - Delay between API calls
- `--max_retries` - Maximum retry attempts

### TTS Configuration
- `--voice` - TTS voice (default: en-US-JennyNeural)
- `--audio_bitrate` - Audio bitrate

### Progress Management
- `--progress_file` - Progress tracking file
- `--show_progress` - Display progress summary
- `--cleanup_progress DAYS` - Clean old sessions

## Examples

### Basic Usage
```bash
python book_ocr_tts_refactored.py --input_dir ./images --output_audio ./output.wav
```

### Resume Processing
```bash
python book_ocr_tts_refactored.py --input_dir ./images --output_audio ./output.wav
```

### TTS Only (from existing text file)
```bash
python book_ocr_tts_refactored.py --input_text ./book.txt --output_audio ./audiobook.wav --start_from tts
```

### Custom Voice and Settings
```bash
python book_ocr_tts_refactored.py \
  --input_dir ./images \
  --output_audio ./audiobook.mp3 \
  --voice "en-US-AriaNeural" \
  --audio_bitrate "64k" \
  --delay 2.0
```

### View Progress
```bash
python book_ocr_tts_refactored.py --show_progress
```

## Dependencies

- `openai` - For GitHub Models API
- `edge-tts` - For text-to-speech conversion
- `pydub` - For audio processing
- Standard library modules: `asyncio`, `argparse`, `json`, `hashlib`, etc.

## Error Handling

The refactored version includes comprehensive error handling:

- **Automatic Retry** - Failed API calls are retried with exponential backoff
- **Non-retryable Errors** - Authentication and quota errors are not retried
- **Progress Preservation** - Progress is saved even if processing is interrupted
- **Graceful Degradation** - Fallback strategies for various failure scenarios

## Migration from Original Script

The refactored version is fully backward compatible. Simply replace calls to `book_ocr_tts.py` with `book_ocr_tts_refactored.py`. All command-line arguments remain the same.

### Benefits of Migration

1. **Better Performance** - Optimized processing and resource management
2. **Improved Reliability** - Enhanced error handling and recovery
3. **Future-Proof** - Modular architecture allows for easy updates
4. **Better Debugging** - Clear separation of concerns simplifies troubleshooting

```bash
pip install openai edge-tts
```

## Setup

1. Ensure you have a GitHub Personal Access Token with appropriate permissions
2. Place the token in `../../access_token/github_pat` or specify a custom path
3. Prepare a directory with images (supports common formats: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp)

## Usage

### Basic Usage

```bash
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav
```

### Text File Output

By default, the script automatically saves both raw OCR text and cleaned text to files:

```bash
# Automatic text saving (enabled by default)
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav
# Creates:
# - output_raw.txt (raw OCR text before cleaning)
# - output_cleaned.txt (text after cleaning)
```

```bash
# Custom text output paths
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav \
    --output_raw_text my_raw_text.txt --output_cleaned_text my_cleaned_text.txt
```

```bash
# Disable automatic text saving
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --disable_auto_text_save
```

```bash
# Legacy: Save final processed text (for compatibility)
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --output_text final_text.txt
```

### With Resume Support (Default)

```bash
# First run - processes some images then gets interrupted
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav

# Second run - automatically resumes from where it left off
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav
```

### Start Fresh Without Resume

```bash
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --no_resume
```

### Resume from Different Steps

```bash
# Resume from text cleaning step (if OCR is already completed)
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --start_from cleaning

# Start only from TTS using previously saved text file
python book_ocr_tts.py --input_text extracted_text.txt --output_audio output.wav --start_from tts

# Resume from TTS step using completed OCR session
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --start_from tts
```

### Configure Retry Behavior

```bash
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --max_retries 5
```

### Progress Management

```bash
# View all saved progress sessions
python book_ocr_tts.py --show_progress

# Clean up sessions older than 7 days
python book_ocr_tts.py --cleanup_progress 7
```

### Use Different Voice

```bash
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --voice en-US-AriaNeural
```

### Use Different OCR Model

```bash
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --model_name openai/gpt-4o
```

### Use Different API Endpoint

```bash
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --endpoint https://api.openai.com/v1
```

### Skip Text Cleaning

```bash
python book_ocr_tts.py --input_dir /path/to/images --output_audio output.wav --skip_cleaning
```

### Custom Configuration

```bash
python book_ocr_tts.py \
  --input_dir /path/to/images \
  --output_audio output.wav \
  --output_text extracted_text.txt \
  --voice en-GB-SoniaNeural \
  --delay 2.0 \
  --token_path /custom/path/to/token \
  --model_name openai/gpt-4o-mini \
  --endpoint https://your-custom-api.com/v1
```

## Supported API Endpoints

- **https://models.github.ai/inference** (default) - GitHub Models API
- **https://api.openai.com/v1** - OpenAI direct API
- **https://api.anthropic.com/v1** - Anthropic Claude API
- **https://your-local-server:8000/v1** - Local API deployment
- **https://your-azure-endpoint.openai.azure.com/** - Azure OpenAI Service

## Supported OCR Models

- **openai/o4-mini** (default) - Fast and efficient for most use cases
- **openai/gpt-4o** - Higher accuracy, better for complex layouts
- **openai/gpt-4o-mini** - Good balance of speed and accuracy
- **openai/gpt-4-turbo** - Alternative high-quality option

## Supported TTS Voices

- **English (US)**: en-US-JennyNeural, en-US-AriaNeural, en-US-GuyNeural, en-US-DavisNeural
- **English (UK)**: en-GB-SoniaNeural, en-GB-RyanNeural
- **Chinese**: zh-CN-XiaoxiaoNeural, zh-CN-YunxiNeural
- And many more supported by Microsoft Edge TTS

## How It Works

1. **Image Discovery**: Scans the input directory for image files
2. **OCR Processing**: 
   - Converts each image to base64
   - Sends to GitHub Models API (GPT-4o-mini) for text extraction
   - Includes retry logic for failed requests
3. **Text Combination**: Combines extracted text with proper spacing and formatting
4. **Text Cleaning**: Removes OCR artifacts, unnecessary separators (like '--- OCR Start ---'), excessive newlines, and fixes common OCR spacing errors
5. **TTS Conversion**: Uses Edge TTS to convert the cleaned text to speech
6. **Output**: Saves the audio file and optionally the extracted/cleaned text

## Error Handling

- Skips corrupted or unreadable images
- Retries failed API calls up to 3 times
- Continues processing even if some images fail
- Provides detailed error messages and progress updates

## Rate Limiting

- Configurable delay between API calls (default: 1 second)
- Helps avoid hitting GitHub API rate limits
- Adjust `--delay` parameter based on your usage needs

## Examples

Run the examples script to see usage patterns:

```bash
python example_usage.py
```

## Tips

- For better OCR results, use high-resolution, clear images
- Adjust the delay if you encounter rate limiting issues
- Use different voices to find the one that suits your content best
- Save extracted text for review and editing before TTS conversion
- When using different endpoints, ensure your token/API key is compatible with the chosen endpoint
- For local deployments, make sure the endpoint is accessible and the model supports vision capabilities
