import logging
from collections.abc import Callable
from dataclasses import dataclass
from time import sleep
from typing import Coroutine

from anyio import create_memory_object_stream, get_cancelled_exc_class
from anyio import sleep as asleep

logger = logging.getLogger(__name__)

DEFAULT_JOB_BUFFER_SIZE = 256
DEFAULT_JOB_MAX_RETRY = 3


@dataclass
class Job:
    data: bytes
    id: str
    retry: int = 0


class JobQueue:
    job_buffer: int
    job_max_retry: int
    instance = None
    open: bool = True
    delay_seconds: int = 2
    processor: Callable[[bytes], Coroutine]
    canceller: Callable[[bytes], Coroutine]

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(
        self,
        job_buffer: int = DEFAULT_JOB_BUFFER_SIZE,
        job_max_retry: int = DEFAULT_JOB_MAX_RETRY,
    ):
        self.job_buffer = job_buffer
        self.job_max_retry = job_max_retry
        self.send_stream, self.receive_stream = create_memory_object_stream[
            Job
        ](job_buffer)

    async def process_job(self, job: Job):
        logger.info(f"Processing job {job.id}")
        if await self.processor(job.data):
            logger.info(f"Finished processing job {job.id}")
        elif job.retry < self.job_max_retry:
            logger.info(f"Could not process {job.id}, requeuing...")
            job.retry += 1
            await self.send_stream.send(job)
        else:
            logger.error(
                f"Could not process {job.id}, max retry reached, dropping."
            )

    async def monitor_queue(self):
        logger.info("Starting queue monitor")
        if not (self.processor and self.canceller):
            logger.error("Processor and canceller must be set, use set_processor and set_canceller before starting monitor")
            raise Exception("Cannot start monitor without processor and canceller")

        while True:
            try:
                job = await self.receive_stream.receive()
                await self.process_job(job)
            except get_cancelled_exc_class():
                logger.error("Stopping queue monitor")
                await self.canceller()
                raise
            except:
                logger.exception(f"Error receiving or processing job from queue")

            await asleep(self.delay_seconds)



    def set_processor(self, processor: Callable[[bytes], Coroutine]):
        self.processor = processor

    def set_canceller(self, canceller: Callable[[bytes], Coroutine]):
        self.canceller = canceller

def get_queue():
    return JobQueue()
