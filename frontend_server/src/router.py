import logging
from os.path import join

import requests
from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def root():
    return RedirectResponse("/static/index.html")

@router.get("/favicon.ico")
async def get_favicon():
    return FileResponse("../resources/favicon.svg")

server_uri="http://instaprint_backend:80"

@router.post("/upload_images")
async def upload_images(files: list[UploadFile]):
    res = requests.post(join(server_uri, "upload_images"), files={"files": (files[0].filename, files[0].file)})
    return JSONResponse(res.json())

@router.get("/status")
async def get_status():
    res = requests.get(join(server_uri, "status"))
    return JSONResponse(res.json())