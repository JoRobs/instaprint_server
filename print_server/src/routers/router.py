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
