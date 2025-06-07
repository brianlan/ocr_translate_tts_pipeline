#!/usr/bin/env python3
"""
Retry handler with exponential backoff for API calls.
"""

import time
from typing import Callable, TypeVar
from functools import wraps

T = TypeVar('T')


class RetryHandler:
    """Handles retry logic with exponential backoff."""
    
    # Error types that shouldn't be retried
    NON_RETRYABLE_ERRORS = [
        'invalid_request_error', 'authentication_failed', 'permission_denied',
        'quota_exceeded', 'model_not_found', 'invalid_api_key'
    ]
    
    @staticmethod
    def is_retryable_error(error: Exception) -> bool:
        """Check if an error should be retried."""
        error_message = str(error).lower()
        return not any(
            non_retry_error in error_message 
            for non_retry_error in RetryHandler.NON_RETRYABLE_ERRORS
        )
    
    @staticmethod
    def retry_with_backoff(
        func: Callable[..., T], 
        max_retries: int = 3, 
        delay_factor: float = 2.0,
        *args, 
        **kwargs
    ) -> T:
        """
        Retry a function with exponential backoff.
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retry attempts
            delay_factor: Exponential backoff factor
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Result of the function call
            
        Raises:
            The last exception encountered if all retries fail
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # Check if error should be retried
                if not RetryHandler.is_retryable_error(e):
                    print(f"Non-retryable error: {str(e)}")
                    raise e
                
                if attempt < max_retries - 1:
                    wait_time = delay_factor ** attempt
                    print(f"API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    print(f"Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"API call failed after {max_retries} attempts: {str(e)}")
        
        if last_exception:
            raise last_exception
        else:
            raise Exception("API call failed with unknown error")


def with_retry(max_retries: int = 3, delay_factor: float = 2.0):
    """
    Decorator for automatic retry with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay_factor: Exponential backoff factor
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return RetryHandler.retry_with_backoff(
                func, max_retries, delay_factor, *args, **kwargs
            )
        return wrapper
    return decorator
