"""
Thread pool executor for handling CPU-intensive tasks and sync operations in async context.
"""
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

logger = logging.getLogger(__name__)


class ThreadPoolManager:
    """Manages thread pool executors for different use cases."""
    
    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize thread pool manager.
        
        Args:
            max_workers: Maximum number of worker threads. 
                        If None, uses min(32, os.cpu_count() + 4)
        """
        if max_workers is None:
            # Default to min(32, os.cpu_count() + 4) as recommended by Python docs
            max_workers = min(32, (os.cpu_count() or 1) + 4)
        
        self.max_workers = max_workers
        self._executor: Optional[ThreadPoolExecutor] = None
        logger.info(f"ThreadPoolManager initialized with {max_workers} max workers")

    @property
    def executor(self) -> ThreadPoolExecutor:
        """Get or create the thread pool executor."""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=self.max_workers,
                thread_name_prefix="db_adapter_worker"
            )
            logger.info("ThreadPoolExecutor created")
        return self._executor

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the thread pool executor."""
        if self._executor is not None:
            self._executor.shutdown(wait=wait)
            self._executor = None
            logger.info("ThreadPoolExecutor shutdown")


# Global thread pool manager instance
# Use a reasonable default for database operations
thread_pool_manager = ThreadPoolManager(max_workers=20)

# Convenience access to the executor
thread_pool = thread_pool_manager.executor


def get_thread_pool() -> ThreadPoolExecutor:
    """Get the global thread pool executor."""
    return thread_pool


def shutdown_thread_pool(wait: bool = True) -> None:
    """Shutdown the global thread pool executor."""
    thread_pool_manager.shutdown(wait=wait) 