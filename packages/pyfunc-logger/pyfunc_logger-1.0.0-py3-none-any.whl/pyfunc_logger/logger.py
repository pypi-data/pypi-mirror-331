"""
Function call logger for Python.

This module provides logging capabilities for tracking function calls,
arguments, execution times, and return values. It is designed to be used 
as a decorator for easy integration with existing code.
"""

import csv
import datetime
import functools
import inspect
import os
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class FunctionLogger:
    """
    A logger that records function calls to a CSV file with detailed timing.
    """
    
    def __init__(self, log_dir: Optional[str] = None, max_arg_count: int = 9, 
                 truncate_length: int = 100):
        """
        Initialize the function logger.
        
        Args:
            log_dir: Directory to store log files. Defaults to 'func_logs' in current directory.
            max_arg_count: Maximum number of arguments to log (default: 9).
            truncate_length: Maximum length for string values before truncation (default: 100).
        """
        self.log_dir = log_dir or os.path.join(os.getcwd(), "func_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"func_log_{timestamp}.csv")
        self.csv_lock = threading.Lock()
        self.max_arg_count = max_arg_count
        self.truncate_length = truncate_length
        
        # Initialize with headers
        headers = [
            "call_id", "function_name", "relative_folder", "file_name", 
            "entry_timestamp", "exit_timestamp", "duration_ms",
            "is_start"
        ]
        
        # Add argument headers
        for i in range(1, self.max_arg_count + 1):
            headers.extend([f"arg{i}_type", f"arg{i}_value"])
        
        # Add return value headers
        headers.extend(["return_type", "return_value"])
        
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    def log(
        self, 
        call_id: str,
        function_name: str,
        relative_folder: str, 
        file_name: str, 
        entry_timestamp: str,
        exit_timestamp: str,
        duration_ms: float,
        is_start: bool, 
        args: Dict[str, Any] = None, 
        return_value: Any = None
    ):
        """
        Log a function call.
        
        Args:
            call_id: Unique identifier for matching entry/exit pairs
            function_name: Name of the function.
            relative_folder: Name of the folder containing the file.
            file_name: Name of the file containing the function.
            entry_timestamp: When the function was entered
            exit_timestamp: When the function exited (only for exit logs)
            duration_ms: Duration in milliseconds (only for exit logs)
            is_start: True if the function is starting, False if it's ending.
            args: Dictionary of function arguments.
            return_value: Return value of the function.
        """
        row = [
            call_id,
            function_name,
            relative_folder, 
            file_name, 
            entry_timestamp,
            exit_timestamp,
            duration_ms,
            is_start
        ]
        
        # Process arguments
        args = args or {}
        for i, (arg_name, arg_value) in enumerate(args.items(), 1):
            if i > self.max_arg_count:
                break
                
            arg_type = type(arg_value).__name__
            
            # Truncate large values
            if isinstance(arg_value, (str, list, dict, tuple)) and len(str(arg_value)) > self.truncate_length:
                arg_value = str(arg_value)[:self.truncate_length] + "..."
                
            row.extend([arg_type, str(arg_value)])
        
        # Fill empty arg slots
        for _ in range(self.max_arg_count - min(self.max_arg_count, len(args))):
            row.extend(["", ""])
        
        # Add return value if provided
        if return_value is not None:
            return_type = type(return_value).__name__
            return_str = str(return_value)
            if len(return_str) > self.truncate_length:
                return_str = return_str[:self.truncate_length] + "..."
            row.extend([return_type, return_str])
        else:
            row.extend(["", ""])
        
        # Write to CSV with lock to prevent race conditions
        with self.csv_lock:
            with open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(row)


# Global logger instance
_function_logger = None
# Dictionary to store function entry timestamps
_function_entry_times = {}


def get_logger(log_dir: Optional[str] = None, max_arg_count: int = 9, 
              truncate_length: int = 100):
    """
    Get or create the global function logger instance.
    
    Args:
        log_dir: Directory to store log files. Defaults to 'func_logs' in current directory.
        max_arg_count: Maximum number of arguments to log (default: 9).
        truncate_length: Maximum length for string values before truncation (default: 100).
    
    Returns:
        FunctionLogger: The global function logger instance.
    """
    global _function_logger
    if _function_logger is None:
        _function_logger = FunctionLogger(
            log_dir=log_dir, 
            max_arg_count=max_arg_count,
            truncate_length=truncate_length
        )
    return _function_logger


def log_function(func=None, *, log_dir=None, max_arg_count=9, truncate_length=100):
    """
    Decorator that logs function calls with precise entry and exit timestamps.
    
    Can be used as @log_function or with parameters @log_function(log_dir='logs')
    
    Args:
        func: The function to decorate.
        log_dir: Optional directory for log files.
        max_arg_count: Maximum number of arguments to log.
        truncate_length: Maximum length for string values.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create logger with specified parameters
            if log_dir or max_arg_count != 9 or truncate_length != 100:
                logger = get_logger(
                    log_dir=log_dir, 
                    max_arg_count=max_arg_count,
                    truncate_length=truncate_length
                )
            else:
                logger = get_logger()
            
            # Generate a unique call ID for matching entry and exit
            call_timestamp = datetime.datetime.now()
            call_id = f"{func.__name__}_{id(wrapper)}_{call_timestamp.timestamp()}"
            entry_timestamp = call_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
            
            # Store entry time for later calculation of duration
            _function_entry_times[call_id] = call_timestamp
            
            # Get file information
            frame = inspect.currentframe().f_back
            file_path = frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            relative_folder = os.path.dirname(file_path).split(os.sep)[-1]
            
            # Process arguments
            arg_dict = {}
            
            # Add positional arguments
            func_args = inspect.getfullargspec(func).args
            for i, arg_name in enumerate(func_args):
                if i < len(args):
                    arg_dict[arg_name] = args[i]
            
            # Add keyword arguments
            arg_dict.update(kwargs)
            
            # Log function start
            logger.log(
                call_id=call_id,
                function_name=func.__name__,
                relative_folder=relative_folder,
                file_name=file_name,
                entry_timestamp=entry_timestamp,
                exit_timestamp="",  # Empty for start
                duration_ms=0.0,    # Zero for start
                is_start=True,
                args=arg_dict
            )
            
            # Call function
            try:
                result = func(*args, **kwargs)
                
                # Log function end
                exit_timestamp = datetime.datetime.now()
                exit_timestamp_str = exit_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
                
                # Calculate duration
                entry_time = _function_entry_times.get(call_id)
                duration_ms = 0.0
                if entry_time:
                    duration_ms = (exit_timestamp - entry_time).total_seconds() * 1000
                    # Clean up entry time
                    del _function_entry_times[call_id]
                
                logger.log(
                    call_id=call_id,
                    function_name=func.__name__,
                    relative_folder=relative_folder,
                    file_name=file_name,
                    entry_timestamp=entry_timestamp,
                    exit_timestamp=exit_timestamp_str,
                    duration_ms=duration_ms,
                    is_start=False,
                    args=arg_dict,
                    return_value=result
                )
                
                return result
            except Exception as e:
                # Log function exception
                exit_timestamp = datetime.datetime.now()
                exit_timestamp_str = exit_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
                
                # Calculate duration
                entry_time = _function_entry_times.get(call_id)
                duration_ms = 0.0
                if entry_time:
                    duration_ms = (exit_timestamp - entry_time).total_seconds() * 1000
                    # Clean up entry time
                    del _function_entry_times[call_id]
                
                logger.log(
                    call_id=call_id,
                    function_name=func.__name__,
                    relative_folder=relative_folder,
                    file_name=file_name,
                    entry_timestamp=entry_timestamp,
                    exit_timestamp=exit_timestamp_str,
                    duration_ms=duration_ms,
                    is_start=False,
                    args=arg_dict,
                    return_value=f"Exception: {str(e)}"
                )
                
                raise
        
        return wrapper
    
    # Handle both @log_function and @log_function(log_dir='logs') syntax
    if func is None:
        return decorator
    else:
        return decorator(func)
