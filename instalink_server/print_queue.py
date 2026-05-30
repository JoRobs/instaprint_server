from dataclasses import dataclass
from time import sleep
from anyio import (
    create_memory_object_stream,
)


DEFAULT_JOB_BUFFER_SIZE = 256

@dataclass
class PrintJob:
    data: bytes
    id: str

class PrintQueue:
    job_buffer: int
    instance = None
    open: bool = True
    delay_seconds: 5

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, job_buffer=DEFAULT_JOB_BUFFER_SIZE):
        self.job_buffer = job_buffer
        self.send_stream, self.recieve_stream = create_memory_object_stream[PrintJob](job_buffer)

    def process_job(job: PrintJob):
        print(f"Processing job {job.id}")
        sleep(5)
        print(f"Finished processing job {job.id}")

    async def monitor_queue(self):
        while True:
            job = await self.receive_stream.receive()
            self.process_job(job)






