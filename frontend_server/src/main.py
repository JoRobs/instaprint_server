import logging
from contextlib import asynccontextmanager
from os import environ

from anyio import (
    create_task_group,
)
from fastapi import (
    FastAPI,
)
from fastapi.staticfiles import StaticFiles

from . import router
from .types import Environment

ENVIRONMENT = environ.get("ENVIRONMENT", Environment.DEV)
LOG_LEVEL = environ.get("LOG_LEVEL", logging.INFO)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before fastapi starts
    logger.info("Creating job queue")
    logger.info(f"""
Running as environment
    ENVIRONMENT: {ENVIRONMENT}
""")

    # If DEV, monkey patch to disable caching for static files
    if ENVIRONMENT == Environment.DEV:
        StaticFiles.is_not_modified = lambda self, *args, **kwargs: False

    async with create_task_group() as tg:
        # before
        yield  # during
        # after
        tg.cancel_scope.cancel()

app = FastAPI(
    lifespan=lifespan, logger=logger
)
app.include_router(router.router)

app.mount(path="/static", app=StaticFiles(directory="./static"), name="static")
app.mount(
    path="/plugins", app=StaticFiles(directory="./plugins"), name="plugins"
)
app.mount(
    path="/resources",
    app=StaticFiles(directory="./resources"),
    name="resources",
)
