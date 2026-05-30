import logging
import subprocess
from time import sleep
from uuid import uuid4
from anyio import (
    create_task_group,
)
from fastapi import (
    APIRouter,
    Depends,
)

logger = logging.getLogger(__name__)

from ..print_queue import get_queue, PrintJob

router = APIRouter(dependencies=[Depends(get_queue)])

@router.get("/")
async def root():
    out = subprocess.run(["bash", "-c", "instantlink"], capture_output=True)
    return {"message": out.stderr.decode("utf-8")}

def dummy_task(task_id: str):
    logger.info(f"Task {task_id} running")
    sleep(5)
    logger.info(f"Task {task_id} finished")

@router.get("/dummy_task")
async def dummy_task_endpoint():
    task_id = uuid4()
    async with create_task_group() as tg:
        tg.start(dummy_task, task_id)

    return {"message": f"Task {task_id} started"}

@router.get("/add_one")
async def add_one():
    task_id = uuid4()
    job = PrintJob(data=task_id.bytes, id=task_id)
    queue = get_queue()

    async with create_task_group() as tg:
      await queue.send_stream.send(job)

    length = queue.send_stream.statistics().current_buffer_used

    return({
        "message":f"Added {task_id}, queue length now {length}",
        "statistics": str(queue.send_stream.statistics()),
        "current_buffer_used": str(queue.send_stream.statistics().current_buffer_used),
        "tasks_waiting_send": str(queue.send_stream.statistics().tasks_waiting_send),
        "tasks_waiting_receive": str(queue.send_stream.statistics().tasks_waiting_receive),
        })

@router.get("/take_one")
async def take_one():
    queue = get_queue()
    job = await queue.receive_stream.receive()
    length = queue.receive_stream.statistics().current_buffer_used

    return({
        "message":f"Taken {job}, queue length now {length}",
        "statistics": str(queue.receive_stream.statistics()),
        "current_buffer_used": str(queue.receive_stream.statistics().current_buffer_used),
        "tasks_waiting_send": str(queue.receive_stream.statistics().tasks_waiting_send),
        "tasks_waiting_receive": str(queue.receive_stream.statistics().tasks_waiting_receive),
        })

