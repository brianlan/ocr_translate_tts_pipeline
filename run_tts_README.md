# run_tts.py - Simple Text-to-Speech Converter

A focused script for converting text files to audio using the existing TTS pipeline services.

## Features

- **Text-to-Speech Conversion**: Convert any text file to high-quality audio
- **Optional Text Cleaning**: Use LLM-powered cleaning to improve text quality
- **Optional Translation**: Translate text between languages before TTS
- **Voice Selection**: Choose from available Azure TTS voices
- **Reuses Existing Services**: Built on top of the existing pipeline components

## Usage

### Basic Usage
```bash
python run_tts.py input.txt output.wav
```

### Skip Text Cleaning
```bash
python run_tts.py input.txt output.wav --skip-cleaning
```

### Skip Translation
```bash
python run_tts.py input.txt output.wav --skip-translation
```

### Translate Text
```bash
python run_tts.py input.txt output.wav --source-lang Chinese --target-lang English
```

### Custom Voice
```bash
python run_tts.py input.txt output.wav --voice en-US-AriaNeural
```

### Custom Model Configuration
```bash
python run_tts.py input.txt output.wav --model-name gemini-2.5-pro-preview-03-25 --endpoint https://openai.newbotai.cn/v1 --token-path ./access_token/gemini_2
```

### Combined Options
```bash
python run_tts.py input.txt output.wav --skip-cleaning --source-lang auto --target-lang Spanish --voice es-ES-ElviraNeural --model-name gemini-2.5-pro-preview-03-25
```

## Command Line Arguments

### Required Arguments
- `input_text`: Path to the input text file
- `output_audio`: Path for the output audio file

### Optional Arguments
- `--skip-cleaning`: Skip the text cleaning step (uses raw input text)
- `--skip-translation`: Skip the translation step (uses original language)
- `--source-lang SOURCE_LANG`: Source language for translation (default: auto-detect)
- `--target-lang TARGET_LANG`: Target language for translation (default: English)
- `--voice VOICE`: TTS voice to use (default: en-US-JennyNeural)
- `--model-name MODEL_NAME`: Model name for text processing and translation (default: openai/o4-mini)
- `--endpoint ENDPOINT`: API endpoint for the model (default: https://models.github.ai/inference)
- `--token-path TOKEN_PATH`: Path to the authentication token file (default: access_token/github_pat)

## Processing Pipeline

The script follows this processing pipeline:

1. **Load Text**: Read the input text file
2. **Clean Text** (optional): Use LLM to clean and improve text quality
3. **Translate Text** (optional): Translate to target language
4. **Convert to Speech**: Generate audio using Azure TTS

## Dependencies

This script reuses existing services from the main pipeline:
- `OCRService`: For LLM client initialization
- `TextProcessor`: For text cleaning
- `TranslationService`: For language translation
- `TTSService`: For text-to-speech conversion
- `FileManager`: For file operations

## Error Handling

The script includes comprehensive error handling for:
- Missing input files
- Empty text files
- Service initialization failures
- Network connectivity issues

## Examples

### Process a book chapter
```bash
python run_tts.py chapter1.txt chapter1_audio.wav
```

### Quick conversion without processing
```bash
python run_tts.py notes.txt notes_audio.wav --skip-cleaning --skip-translation
```

### Translate and convert Chinese text
```bash
python run_tts.py chinese_text.txt english_audio.wav --source-lang Chinese --target-lang English --voice en-US-JennyNeural
```
