from functools import wraps
import asyncio
import logging

logger = logging.getLogger("TaskScheduler")


class Scheduler:
    def __init__(self):
        self._scheduled_tasks = []

    def schedule_task(self, time: float, repeat: int = 0):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                count = 0
                while repeat == -1 or count < repeat:
                    await asyncio.sleep(time)
                    logger.info(f"Task {func.__name__} executed!")
                    await func(*args, **kwargs)
                    count += 1
            self._scheduled_tasks.append(wrapper)
            return wrapper
        return decorator

    async def run(self):
        tasks = [task() for task in self._scheduled_tasks]
        await asyncio.gather(*tasks)
