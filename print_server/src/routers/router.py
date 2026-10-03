import logging

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
)
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse

from ..validators import ImageValidator
from ..job_queue import get_queue
from ..printer import get_printer

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(get_queue)])

@router.get("/")
async def root():
    return RedirectResponse("/index.html")

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

@router.get("/status/")
async def get_status():
    info = get_printer().printer_info
    if info:
        return  JSONResponse(get_printer().printer_info.to_dict(), status_code=200)
    else:
        return JSONResponse({"message": "No status info available"}, status_code=404)

@router.get("/favicon.ico")
async def get_favicon():
    return FileResponse("../../resources/favicon.svg")