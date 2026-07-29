import logging

from collections.abc import Callable
from dataclasses import dataclass
from io import BytesIO
from typing import Any
from time import sleep

from anyio import (
    create_memory_object_stream,
    sleep as asleep
)
from anyio.to_thread import run_sync

logger = logging.getLogger(__name__)

DEFAULT_JOB_BUFFER_SIZE = 256
DEFAULT_JOB_MAX_RETRY = 3

@dataclass
class PrintJob:
    data: bytes
    id: str
    retry: int = 0

class PrintQueue:
    job_buffer: int
    job_max_retry: int
    instance = None
    open: bool = True
    delay_seconds: int = 2
    processor: Callable[[bytes], bool] = lambda _ : sleep(3) or True

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(
        self,
        job_buffer:int=DEFAULT_JOB_BUFFER_SIZE,
        job_max_retry:int=DEFAULT_JOB_MAX_RETRY
    ):
        self.job_buffer = job_buffer
        self.job_max_retry = job_max_retry
        self.send_stream, self.receive_stream = create_memory_object_stream[PrintJob](job_buffer)

    async def process_job(self, job: PrintJob):
        logger.info(f"Processing job {job.id}")
        if await run_sync(self.processor, job.data):
            logger.info(f"Finished processing job {job.id}")
        elif job.retry < self.job_max_retry:
            logger.info(f"Could not process {job.id}, requeuing...")
            job.retry += 1
            await self.send_stream.send(job)
        else:
            logger.error(f"Could not process {job.id}, max retry reached, dropping.")


    async def monitor_queue(self):
        while True:
            job = await self.receive_stream.receive()
            await self.process_job(job)
            await asleep(self.delay_seconds)

    def set_processor(self, processor:Callable[[bytes], Any]):
        self.processor = processor

queue = PrintQueue()

def get_queue():
    return queue
