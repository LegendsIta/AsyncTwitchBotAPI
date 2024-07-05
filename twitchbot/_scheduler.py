from functools import wraps
import asyncio
import logging

logger = logging.getLogger("TaskScheduler")


class Scheduler:
    def __init__(self):
        self._scheduled_tasks = []
        self._running = False

    def schedule_task(self, time: float, repeat: int = 0):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                count = 0
                while self._running and (repeat == -1 or count < repeat):
                    await asyncio.sleep(time)
                    if not self._running:
                        break
                    logger.info(f"Task {func.__name__} executed!")
                    await func(*args, **kwargs)
                    count += 1
            self._scheduled_tasks.append(wrapper)
            return wrapper
        return decorator

    async def run(self):
        self._running = True
        tasks = [task() for task in self._scheduled_tasks]
        await asyncio.gather(*tasks)

    def stop(self):
        logger.info("Stopping all scheduled tasks...")
        self._running = False
