import logging
from time import sleep
from uuid import uuid4

from anyio import create_task_group
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
)
from fastapi.responses import RedirectResponse

from ..validators import ImageValidator

logger = logging.getLogger(__name__)

from ..job_queue import Job, get_queue

router = APIRouter(dependencies=[Depends(get_queue)])


@router.get("/")
async def root():
    return RedirectResponse("/static/imageupload.html")


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
    job = Job(data=task_id.bytes, id=task_id)
    queue = get_queue()

    async with create_task_group():
        await queue.send_stream.send(job)

    length = queue.send_stream.statistics().current_buffer_used

    return {
        "message": f"Added {task_id}, queue length now {length}",
        "statistics": str(queue.send_stream.statistics()),
        "current_buffer_used": str(
            queue.send_stream.statistics().current_buffer_used
        ),
        "tasks_waiting_send": str(
            queue.send_stream.statistics().tasks_waiting_send
        ),
        "tasks_waiting_receive": str(
            queue.send_stream.statistics().tasks_waiting_receive
        ),
    }


@router.get("/take_one")
async def take_one():
    queue = get_queue()
    job = await queue.receive_stream.receive()
    length = queue.receive_stream.statistics().current_buffer_used

    return {
        "message": f"Taken {job}, queue length now {length}",
        "statistics": str(queue.receive_stream.statistics()),
        "current_buffer_used": str(
            queue.receive_stream.statistics().current_buffer_used
        ),
        "tasks_waiting_send": str(
            queue.receive_stream.statistics().tasks_waiting_send
        ),
        "tasks_waiting_receive": str(
            queue.receive_stream.statistics().tasks_waiting_receive
        ),
    }


@router.post("/upload_image/")
async def upload_image(file: UploadFile):

    validator = ImageValidator()

    result = await validator.validate_file(file)

    if result.valid:
        return {"message": "Success!"}

    return {"message": f"Error: [{','.join(result.errors)}]"}


@router.post("/upload_images/")
async def upload_images(files: list[UploadFile]):

    validator = ImageValidator()

    results = [await validator.validate_file(file) for file in files]

    if all(r.valid for r in results):
        tasks = [await add_data_task(await file.read()) for file in files]

        return {"message": f"Success! Added tasks: {','.join(tasks)}"}

    return {
        "message": f"Error: [{','.join([','.join(r.errors) for r in results])}]"
    }


async def add_data_task(data: bytes) -> str:
    task_id = uuid4()
    job = Job(data=data, id=str(task_id))
    queue = get_queue()
    await queue.send_stream.send(job)

    return str(task_id)
