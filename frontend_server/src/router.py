import logging
import requests
from os.path import join

from fastapi import (
    APIRouter,
    UploadFile
)

from fastapi.responses import FileResponse, RedirectResponse, JSONResponse


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def root():
    return RedirectResponse("/static/index.html")

@router.get("/favicon.ico")
async def get_favicon():
    return FileResponse("../resources/favicon.svg")

server_uri="http://print_server_backend:80"

@router.post("/upload_images")
async def upload_images(files: list[UploadFile]):
    res = requests.post(join(server_uri, "/upload_files"), files={"files": open(files[0], "rb")})
    return JSONResponse(res.json())

@router.get("/status")
async def get_status():
    res = requests.get(join(server_uri, "/status"))
    return JSONResponse(res.json())