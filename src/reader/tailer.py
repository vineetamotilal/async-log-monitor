import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

@asynccontextmanager
async def open_log_file(file_path: str) -> AsyncGenerator:
    """
    An asynchronous context manager for safely opening and closing log files.
    Ensures that the file handle is properly closed even if exceptions occur.
    
    Args:
        file_path: Path to the log file.
        
    Yields:
        An open file object.
    """
    f = None
    try:
        f = open(file_path, "r", encoding="utf-8")
        yield f
    finally:
        if f is not None:
            f.close()

async def tail_file(file_path: str) -> AsyncGenerator[str, None]:
    """
    Asynchronous generator to 'tail' a log file.
    It reads new lines as they are appended to the file.
    Memory efficient: yields one line at a time.
    
    Args:
        file_path: Path to the log file.
        
    Yields:
        New lines appended to the file as strings.
    """
    async with open_log_file(file_path) as f:
        # Seek to the end of the file to start tailing "live" logs
        f.seek(0, os.SEEK_END)
        
        while True:
            line = f.readline()
            if not line:
                # If no new line, wait briefly before checking again
                # This prevents a tight loop that consumes 100% CPU
                await asyncio.sleep(0.1)
                continue
            
            # Yield the line if it's not empty, stripping newline characters
            stripped_line = line.strip()
            if stripped_line:
                yield stripped_line
