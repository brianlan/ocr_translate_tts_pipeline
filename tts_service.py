#!/usr/bin/env python3
"""
Text-to-Speech service using Edge TTS.
"""

import os
import tempfile
from typing import List

import edge_tts
from pydub import AudioSegment

from config import TTSConfig


class TTSService:
    """Handles text-to-speech conversion using Edge TTS."""
    
    def __init__(self, config: TTSConfig):
        """
        Initialize TTS service.
        
        Args:
            config: TTS configuration
        """
        self.config = config
    
    async def text_to_speech(self, text: str, output_path: str) -> None:
        """
        Convert text to speech using Edge TTS.
        
        Args:
            text: Text to convert to speech
            output_path: Path where to save the audio file
        """
        print(f"Converting text to speech using voice: {self.config.voice}")
        
        # Split text into chunks if it's too long (Edge TTS has limits)
        chunks = [text[i:i+self.config.max_chunk_size] 
                 for i in range(0, len(text), self.config.max_chunk_size)]
        
        if len(chunks) > 1:
            print(f"Text split into {len(chunks)} chunks for processing")
            
            # Try chunked processing first
            try:
                await self._process_chunks_and_combine(chunks, output_path)
                return
            except Exception as e:
                print(f"❌ Chunked processing failed: {str(e)}")
                print("🔄 Falling back to single-chunk processing...")
                # Fall through to single chunk processing
        
        # Single chunk processing (fallback or original)
        print("Processing as single chunk...")
        communicate = edge_tts.Communicate(text, self.config.voice)
        await communicate.save(output_path)
        print(f"Audio saved to: {output_path}")
    
    async def _process_chunks_and_combine(self, chunks: List[str], output_path: str) -> None:
        """
        Process text chunks and combine into single audio file.
        
        Args:
            chunks: List of text chunks to process
            output_path: Path where to save the combined audio
        """
        temp_files = []
        audio_segments = []
        
        try:
            # First, generate a small sample to detect Edge TTS audio format
            sample_communicate = edge_tts.Communicate("test", self.config.voice)
            sample_fd, sample_path = tempfile.mkstemp(suffix='.mp3')
            os.close(sample_fd)
            await sample_communicate.save(sample_path)
            
            # Load sample to detect audio parameters
            sample_audio = AudioSegment.from_file(sample_path)
            sample_rate = sample_audio.frame_rate
            channels = sample_audio.channels
            sample_format = sample_audio.sample_width * 8  # bits per sample
            
            print(f"📊 Detected audio format: {sample_rate}Hz, {channels} channel(s), {sample_format}-bit")
            
            # Clean up sample
            os.unlink(sample_path)
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)} ({len(chunk)} characters)...")
                
                # Create temporary file for this chunk
                temp_fd, temp_path = tempfile.mkstemp(suffix='.mp3')
                os.close(temp_fd)
                temp_files.append(temp_path)
                
                # Generate audio for this chunk
                communicate = edge_tts.Communicate(chunk, self.config.voice)
                await communicate.save(temp_path)
                
                # Load audio segment
                try:
                    audio_segment = AudioSegment.from_file(temp_path)
                    audio_segments.append(audio_segment)
                except Exception as e:
                    print(f"Error loading audio chunk {i+1}: {str(e)}")
                    # Try to read as different formats
                    for fmt in ['mp3', 'wav', 'webm']:
                        try:
                            audio_segment = AudioSegment.from_file(temp_path, format=fmt)
                            audio_segments.append(audio_segment)
                            print(f"Successfully loaded chunk {i+1} as {fmt}")
                            break
                        except Exception:
                            continue
                    else:
                        raise Exception(f"Could not load audio chunk {i+1} in any supported format")
            
            # Combine all audio segments
            print("Combining audio chunks...")
            combined_audio = audio_segments[0]
            for segment in audio_segments[1:]:
                combined_audio += segment
            
            # Export with optimized settings
            print("Exporting optimized audio...")
            await self._export_combined_audio(
                combined_audio, output_path, sample_rate, channels
            )
            
            print(f"Audio saved to: {output_path}")
            
        finally:
            # Clean up temporary files
            for temp_path in temp_files:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
    
    async def _export_combined_audio(
        self, 
        combined_audio: AudioSegment, 
        output_path: str, 
        sample_rate: int, 
        channels: int
    ) -> None:
        """
        Export combined audio with format-specific optimizations.
        
        Args:
            combined_audio: Combined audio segment
            output_path: Output file path
            sample_rate: Audio sample rate
            channels: Number of audio channels
        """
        if output_path.lower().endswith('.wav'):
            # For WAV output, export as compressed MP3 first, then save as .wav for compatibility
            temp_mp3_fd, temp_mp3_path = tempfile.mkstemp(suffix='.mp3')
            os.close(temp_mp3_fd)
            
            try:
                combined_audio.export(
                    temp_mp3_path, 
                    format="mp3",
                    bitrate=self.config.audio_bitrate,
                    parameters=["-ar", str(sample_rate), "-ac", str(channels)]
                )
                
                # For better compatibility, keep it compressed with .wav extension
                if self.config.audio_bitrate != "uncompressed":
                    import shutil
                    shutil.copy2(temp_mp3_path, output_path)
                    print("💡 Note: File saved as compressed audio with .wav extension (actual format: MP3)")
                    print(f"    Compressed size: {os.path.getsize(output_path):,} bytes")
                else:
                    # Convert to actual WAV if explicitly requested
                    final_audio = AudioSegment.from_mp3(temp_mp3_path)
                    final_audio.export(
                        output_path, 
                        format="wav",
                        parameters=["-acodec", "pcm_s16le", "-ar", str(sample_rate), "-ac", str(channels)]
                    )
            finally:
                try:
                    os.unlink(temp_mp3_path)
                except OSError:
                    pass
                    
        elif output_path.lower().endswith('.mp3'):
            # For MP3, use similar bitrate and quality as Edge TTS
            combined_audio.export(
                output_path, 
                format="mp3",
                bitrate=self.config.audio_bitrate,
                parameters=["-ar", str(sample_rate), "-ac", str(channels)]
            )
        else:
            # Default: export as MP3 with Edge TTS-like settings
            combined_audio.export(
                output_path, 
                format="mp3",
                bitrate=self.config.audio_bitrate,
                parameters=["-ar", str(sample_rate), "-ac", str(channels)]
            )
