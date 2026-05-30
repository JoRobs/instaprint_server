import logging
from dataclasses import dataclass
from anyio import (
    create_memory_object_stream,
    sleep
)

logger = logging.getLogger(__name__)

DEFAULT_JOB_BUFFER_SIZE = 256

@dataclass
class PrintJob:
    data: bytes
    id: str

class PrintQueue:
    job_buffer: int
    instance = None
    open: bool = True
    delay_seconds: int = 2

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, job_buffer=DEFAULT_JOB_BUFFER_SIZE):
        self.job_buffer = job_buffer
        self.send_stream, self.receive_stream = create_memory_object_stream[PrintJob](job_buffer)

    async def process_job(self, job: PrintJob):
        logger.info(f"Processing job {job.id}")
        await sleep(3)
        logger.info(f"Finished processing job {job.id}")

    async def monitor_queue(self):
        while True:
            job = await self.receive_stream.receive()
            await self.process_job(job)
            await sleep(self.delay_seconds)

queue = PrintQueue()

def get_queue():
    return queue
