#!/usr/bin/env python3
"""
Progress tracking and session management for the pipeline.
"""

import os
import json
import time
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ProcessingStats:
    """Statistics for processing operations."""
    completed: int = 0
    failed: int = 0
    total: int = 0
    
    @property
    def percentage(self) -> float:
        """Calculate completion percentage."""
        return (self.completed / self.total * 100) if self.total > 0 else 0.0


class ProgressTracker:
    """Manages progress tracking and session persistence."""
    
    def __init__(self, progress_file: str = "ocr_progress.json"):
        """
        Initialize progress tracker.
        
        Args:
            progress_file: Path to the progress tracking file
        """
        self.progress_file = progress_file
    
    def create_session_id(self, input_dir: str, model_name: str, total_files: int) -> str:
        """
        Create a unique session ID based on input parameters.
        
        Args:
            input_dir: Input directory path
            model_name: Model name used for processing
            total_files: Total number of files to process
            
        Returns:
            8-character session ID
        """
        session_data = f"{input_dir}_{model_name}_{total_files}"
        return hashlib.md5(session_data.encode()).hexdigest()[:8]
    
    def save_progress(self, progress_data: Dict[str, Any]) -> None:
        """
        Save processing progress to file.
        
        Args:
            progress_data: Progress data to save
        """
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save progress: {e}")
    
    def load_progress(self) -> Dict[str, Any]:
        """
        Load processing progress from file.
        
        Returns:
            Progress data dictionary, empty if file doesn't exist or can't be loaded
        """
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load progress: {e}")
        return {}
    
    def initialize_session(
        self, 
        session_id: str, 
        input_dir: str, 
        model_name: str, 
        total_files: int
    ) -> Dict[str, Any]:
        """
        Initialize a new processing session.
        
        Args:
            session_id: Unique session identifier
            input_dir: Input directory path
            model_name: Model name for processing
            total_files: Total number of files to process
            
        Returns:
            Initial session data dictionary
        """
        return {
            'input_dir': input_dir,
            'model_name': model_name,
            'total_files': total_files,
            'processed_files': {},
            'texts': [],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'running'
        }
    
    def update_session_progress(
        self, 
        progress_data: Dict[str, Any], 
        session_id: str, 
        processed_files: Dict[str, Any], 
        texts: List[str], 
        stats: ProcessingStats
    ) -> None:
        """
        Update session progress data.
        
        Args:
            progress_data: Main progress data dictionary
            session_id: Session identifier
            processed_files: Dictionary of processed file information
            texts: List of extracted texts
            stats: Processing statistics
        """
        progress_data[session_id]['processed_files'] = processed_files
        progress_data[session_id]['texts'] = texts
        progress_data[session_id]['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        progress_data[session_id]['stats'] = {
            'completed': stats.completed,
            'failed': stats.failed,
            'total': stats.total,
            'percentage': stats.percentage
        }
    
    def complete_session(
        self, 
        progress_data: Dict[str, Any], 
        session_id: str, 
        full_text: str, 
        stats: ProcessingStats, 
        total_time: float
    ) -> None:
        """
        Mark a session as completed and save final results.
        
        Args:
            progress_data: Main progress data dictionary
            session_id: Session identifier
            full_text: Complete extracted text
            stats: Final processing statistics
            total_time: Total processing time in seconds
        """
        progress_data[session_id]['status'] = 'completed'
        progress_data[session_id]['completion_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        progress_data[session_id]['extracted_text'] = full_text
        progress_data[session_id]['final_stats'] = {
            'completed': stats.completed,
            'failed': stats.failed,
            'total': stats.total,
            'percentage': stats.percentage,
            'total_time_minutes': total_time / 60,
            'total_characters': len(full_text)
        }
    
    def interrupt_session(
        self, 
        progress_data: Dict[str, Any], 
        session_id: str, 
        stats: ProcessingStats
    ) -> None:
        """
        Mark a session as interrupted.
        
        Args:
            progress_data: Main progress data dictionary
            session_id: Session identifier
            stats: Current processing statistics
        """
        progress_data[session_id]['status'] = 'interrupted'
        progress_data[session_id]['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        progress_data[session_id]['interruption_stats'] = {
            'completed': stats.completed,
            'failed': stats.failed,
            'total': stats.total,
            'percentage': stats.percentage
        }
    
    def error_session(
        self, 
        progress_data: Dict[str, Any], 
        session_id: str, 
        error_message: str, 
        stats: ProcessingStats
    ) -> None:
        """
        Mark a session as having an error.
        
        Args:
            progress_data: Main progress data dictionary
            session_id: Session identifier
            error_message: Error description
            stats: Current processing statistics
        """
        progress_data[session_id]['status'] = 'error'
        progress_data[session_id]['error'] = error_message
        progress_data[session_id]['error_stats'] = {
            'completed': stats.completed,
            'failed': stats.failed,
            'total': stats.total,
            'percentage': stats.percentage
        }
        progress_data[session_id]['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    def show_progress_summary(self) -> None:
        """Display a summary of all saved progress sessions."""
        progress_data = self.load_progress()
        
        if not progress_data:
            print("No saved progress sessions found.")
            return
        
        print(f"📊 Found {len(progress_data)} saved session(s):")
        print("-" * 80)
        
        for session_id, session_data in progress_data.items():
            status = session_data.get('status', 'unknown')
            total_files = session_data.get('total_files', 0)
            
            # Get statistics from appropriate location
            if 'stats' in session_data:
                stats_data = session_data['stats']
            elif 'final_stats' in session_data:
                stats_data = session_data['final_stats']
            else:
                completed = len(session_data.get('processed_files', {}))
                stats_data = {
                    'completed': completed,
                    'failed': 0,
                    'percentage': (completed / total_files * 100) if total_files > 0 else 0
                }
            
            completed = stats_data.get('completed', 0)
            failed = stats_data.get('failed', 0)
            percentage = stats_data.get('percentage', 0)
            
            print(f"Session {session_id}:")
            print(f"  Directory: {session_data.get('input_dir', 'unknown')}")
            print(f"  Model: {session_data.get('model_name', 'unknown')}")
            print(f"  Status: {status}")
            print(f"  Progress: {completed}/{total_files} ({percentage:.1f}%) successful, {failed} failed")
            print(f"  Started: {session_data.get('timestamp', 'unknown')}")
            if 'last_updated' in session_data:
                print(f"  Last updated: {session_data['last_updated']}")
            print()
    
    def cleanup_old_sessions(self, days_old: int = 7) -> None:
        """
        Remove progress sessions older than specified days.
        
        Args:
            days_old: Number of days after which sessions are considered old
        """
        progress_data = self.load_progress()
        
        if not progress_data:
            print("No progress sessions to clean up.")
            return
        
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        sessions_to_remove = []
        
        for session_id, session_data in progress_data.items():
            timestamp_str = session_data.get('timestamp', '')
            try:
                # Parse timestamp
                session_time = time.mktime(time.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S'))
                if session_time < cutoff_time:
                    sessions_to_remove.append(session_id)
            except (ValueError, TypeError):
                # If we can't parse the timestamp, consider it for removal
                sessions_to_remove.append(session_id)
        
        if sessions_to_remove:
            for session_id in sessions_to_remove:
                del progress_data[session_id]
            
            self.save_progress(progress_data)
            print(f"🧹 Cleaned up {len(sessions_to_remove)} old session(s)")
        else:
            print("No old sessions found to clean up.")
    
    def get_completed_session_text(
        self, 
        input_dir: str, 
        model_name: str, 
        total_files: int
    ) -> Optional[str]:
        """
        Get extracted text from a completed session.
        
        Args:
            input_dir: Input directory path
            model_name: Model name used
            total_files: Total number of files
            
        Returns:
            Extracted text if found, None otherwise
        """
        progress_data = self.load_progress()
        session_id = self.create_session_id(input_dir, model_name, total_files)
        
        if session_id in progress_data:
            session_data = progress_data[session_id]
            if (session_data.get('status') == 'completed' and 
                'extracted_text' in session_data):
                
                extracted_text = session_data['extracted_text']
                stats = session_data.get('final_stats', {})
                completed = stats.get('completed', 0)
                total = stats.get('total', 0)
                
                print(f"✅ Found completed OCR session {session_id}")
                print(f"📊 Previously processed: {completed}/{total} images successfully")
                print(f"📝 Extracted text: {len(extracted_text):,} characters")
                return extracted_text
        
        return None
