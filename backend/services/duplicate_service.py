# coding=utf-8
"""
Service module for concurrent duplicate detection processing.
This module provides high-level APIs that support concurrent operations.
"""

import asyncio
import concurrent.futures
from typing import Optional, List
from backend.core import duplicate


class DuplicateService:
    """Service class for handling duplicate detection with concurrent processing support."""
    
    def __init__(self, max_workers: int = 1000):
        """
        Initialize the DuplicateService.
        
        Args:
            max_workers (int): Maximum number of concurrent workers
        """
        self.max_workers = max_workers
    
    def process_file_sync(self, file_path: str, output_path: Optional[str] = None):
        """
        Process a file for duplicate detection synchronously.
        
        Args:
            file_path (str): Path to the input file
            output_path (Optional[str]): Path for the output file
        """
        duplicate(file_path=file_path, output_path=output_path)

    
    async def process_file_async(self, file_path: str, output_path: Optional[str] = None):
        """
        Process a file for duplicate detection asynchronously with concurrent operations.
        
        Args:
            file_path (str): Path to the input file
            output_path (Optional[str]): Path for the output file
        """
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            await loop.run_in_executor(executor, duplicate, file_path, output_path)

