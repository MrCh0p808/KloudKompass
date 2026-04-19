# kloudkompass/core/scheduler.py
# ------------------------------
# Global Task Scheduler for the Management OS.
# Prevents 'Subprocess Storming' by staggering cloud refreshes across tabs.

import asyncio
from typing import Callable, Coroutine, Any, List
from kloudkompass.utils.logger import debug

class SmartScheduler:
    """
    Priority-based task queue for cloud background operations.
    Enforces concurrency limits to prevent rate-limiting and CPU spikes.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, concurrency_limit: int = 2):
        if self._initialized:
            return
        self.queue: asyncio.Queue = asyncio.Queue()
        self.concurrency_limit = concurrency_limit
        self._workers: List[asyncio.Task] = []
        self._initialized = True

    async def start(self):
        """Start background workers to process the queue."""
        if self._workers:
            return
            
        debug(f"Starting SmartScheduler with concurrency limit: {self.concurrency_limit}")
        for _ in range(self.concurrency_limit):
            worker = asyncio.create_task(self._worker_loop())
            self._workers.append(worker)

    async def stop(self):
        """Cancel all workers."""
        for worker in self._workers:
            worker.cancel()
        self._workers = []

    async def _worker_loop(self):
        """The core loop that pulls tasks from the queue."""
        while True:
            try:
                # Each task is a tuple: (coroutine_func, args, kwargs, callback)
                task_func, args, kwargs, future = await self.queue.get()
                
                try:
                    result = await task_func(*args, **kwargs)
                    if future:
                        future.set_result(result)
                except Exception as e:
                    if future:
                        future.set_exception(e)
                finally:
                    self.queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                debug(f"Scheduler worker error: {e}")

    def submit(self, coroutine_func: Callable[..., Coroutine[Any, Any, Any]], *args, **kwargs) -> asyncio.Future:
        """
        Schedule a background cloud task. 
        Returns an asyncio.Future that will eventually contain the result.
        """
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self.queue.put_nowait((coroutine_func, args, kwargs, future))
        return future

    def submit_fire_and_forget(self, coroutine_func: Callable[..., Coroutine[Any, Any, Any]], *args, **kwargs):
        """Schedule a task without caring about the result."""
        self.queue.put_nowait((coroutine_func, args, kwargs, None))
