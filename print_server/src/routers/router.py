import logging
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
)
from fastapi.responses import RedirectResponse

from ..validators import ImageValidator
from ..job_queue import get_queue

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(get_queue)])

@router.get("/")
async def root():
    return RedirectResponse("/static/imageupload.html")

@router.post("/upload_images/")
async def upload_images(files: list[UploadFile]):

    validator = ImageValidator()

    results = [await validator.validate_file(file) for file in files]

    if all(r.valid for r in results):
        tasks = [await get_queue().add_job(await file.read()) for file in files]

        return {"message": f"Success! Added tasks: {','.join(tasks)}"}

    return {
        "message": f"Error: [{','.join([','.join(r.errors) for r in results])}]"
    }


