import subprocess

from dataclasses import dataclass
from uuid import uuid4
from fastapi import FastAPI
from anyio import (
    create_task_group,
    sleep,
)
from contextlib import asynccontextmanager

from .print_queue import PrintQueue, PrintJob

MAX_JOB_BUFFER_SIZE = 256

app = FastAPI()
queue = PrintQueue(MAX_JOB_BUFFER_SIZE)

@app.get("/")
async def root():
    out = subprocess.run(["bash", "-c", "instantlink"], capture_output=True)
    return {"message": out.stderr.decode("utf-8")}

@app.get("/dummy_task")
async def dummy_task_endpoint():
    task_id = uuid4()
    async with create_task_group() as tg:
        tg.start(dummy_task, task_id)

    return {"message": f"Task {task_id} started"}

@app.get("/add_one")
async def add_one():
    task_id = uuid4()
    job = PrintJob(data=task_id.bytes, id=task_id)
    await queue.send_stream.send(job)
    length = queue.send_stream.statistics().current_buffer_used

    return({
        "message":f"Added {task_id}, queue length now {length}",
        "statistics": str(queue.send_stream.statistics()),
        "current_buffer_used": str(queue.send_stream.statistics().current_buffer_used),
        "tasks_waiting_send": str(queue.send_stream.statistics().tasks_waiting_send),
        "tasks_waiting_receive": str(queue.send_stream.statistics().tasks_waiting_receive),
        })

@app.get("/take_one")
async def take_one():
    job = await queue.recieve_stream.receive()

    length = queue.recieve_stream.statistics().current_buffer_used

    return({
        "message":f"Taken {job}, queue length now {length}",
        "statistics": str(queue.recieve_stream.statistics()),
        "current_buffer_used": str(queue.recieve_stream.statistics().current_buffer_used),
        "tasks_waiting_send": str(queue.recieve_stream.statistics().tasks_waiting_send),
        "tasks_waiting_receive": str(queue.recieve_stream.statistics().tasks_waiting_receive),
        })

@app.get("/dummy")
async def dummy_task(task_id: str):
    print(f"Task {task_id} running")
    await sleep(5)
    print(f"Task {task_id} finished")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start job processor
    async with create_task_group() as tg:
        tg.start_soon(queue.monitor_queue)

        print("Monitoring queue")

        yield # during
    # after
