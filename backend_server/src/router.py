import logging

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
)
from fastapi.responses import JSONResponse

from .job_queue import get_queue
from .printer import get_printer
from .validators import ImageValidator

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(get_queue)])


@router.post("/upload_images")
async def upload_images(files: list[UploadFile]):

    validator = ImageValidator()

    results = [await validator.validate_file(file) for file in files]
    logger.info(f"Image uploaded, validation results: {results}")

    if all(r.valid for r in results):
        tasks = [
            await get_queue().add_job(await file.read()) for file in files
        ]
        logger.info("Image added to queue")

        return {"message": f"Success! Added tasks: {','.join(tasks)}"}

    return JSONResponse(
        {
            "message": f"Error: [{','.join([','.join(r.errors) for r in results])}]"
        },
        status_code=400,
    )


@router.get("/status")
async def get_status():
    printer_info = get_printer().printer_info.to_dict()
    queue_info = get_queue().get_status().to_dict()
    status = {**printer_info, **queue_info}
    return JSONResponse(status, status_code=200)
