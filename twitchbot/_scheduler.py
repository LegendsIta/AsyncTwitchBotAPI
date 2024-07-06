#!/usr/bin/env python
"""
AsyncTwitchBotApi is a library that enables you to create Twitch chatbots with customizable commands,
filters for execution, and scheduled automatic messages using IRC integration.

Author: LegendsIta <https://github.com/LegendsIta>

This module provides a Scheduler class for managing and executing asynchronous tasks at specified intervals.
Tasks can be scheduled to run repeatedly or a set number of times. The Scheduler uses asyncio to handle
concurrent execution of tasks.
"""

from functools import wraps
import asyncio
import logging

logger = logging.getLogger("TaskScheduler")


class Scheduler:
    """
    A Scheduler class that manages and runs asynchronous tasks at specified intervals.

    Attributes:
        _scheduled_tasks (list): A list of scheduled tasks (coroutines) to be run.
        _running (bool): A flag indicating whether the scheduler is currently running.

    Methods:
        schedule_task(time: float, repeat: int = 0):
            Decorator to schedule a function to run at a specified interval.

        run():
            Start running all scheduled tasks asynchronously.

        stop():
            Stop all running tasks.
    """
    def __init__(self):
        self._scheduled_tasks = []
        self._running = False

    def schedule_task(self, time: float, repeat: int = 0):
        """
        Decorator to schedule a task to be executed at a specified interval.

        Args:
            time (float): The interval time in seconds between each task execution.
            repeat (int): The number of times to repeat the task.
                          -1 for indefinite repetition, 0 for no repetition (default), and any positive integer
                          for specific repetitions.

        Returns:
            function: The wrapped function that will be scheduled.
        """

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
        """
        Start running all scheduled tasks concurrently.

        This method sets the running flag to True and uses asyncio.gather to run all tasks concurrently.
        """
        self._running = True
        tasks = [task() for task in self._scheduled_tasks]
        await asyncio.gather(*tasks)

    def stop(self):
        """
        Stop all scheduled tasks.

        This method sets the running flag to False, signaling all running tasks to stop after their current iteration.
        """
        logger.info("Stopping all scheduled tasks...")
        self._running = False
