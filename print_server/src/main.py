import logging
from contextlib import asynccontextmanager
from os import environ

from anyio import (
    create_task_group,
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import router
from .job_queue import get_queue
from .printer import get_printer
from .types import Environment

ENVIRONMENT = environ.get("ENVIRONMENT", Environment.DEV)
LOG_LEVEL = environ.get("LOG_LEVEL", logging.INFO)
LOG_LEVEL_BLEAK = environ.get("LOG_LEVEL_BLEAK", logging.ERROR)
LOG_LEVEL_PYINSTAXBLE = environ.get("LOG_LEVEL_PYINSTAXBLE", logging.INFO)
PRINTER_ADDRESS = environ.get("PRINTER_ADDRESS", None)
PRINTER_NAME = environ.get("PRINTER_NAME", None)
PRINTING_ENABLED = environ.get("PRINTING_ENABLED", "False") == "True"
DUMMY_PRINTER = environ.get("DUMMY_PRINTER", "False") == "True"
MONITOR_INFO_DELAY = 5

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
logging.getLogger("pyinstaxble").setLevel(LOG_LEVEL_PYINSTAXBLE)
logging.getLogger("bleak").setLevel(LOG_LEVEL_BLEAK)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before fastapi starts
    logger.info("Creating job queue")
    queue = get_queue()
    logger.info(f"""
Running as environment
    DUMMY_PRINTER: {DUMMY_PRINTER}
    ENVIRONMENT: {ENVIRONMENT}
Creating printer interface
    PRINTER_ADDRESS: {PRINTER_ADDRESS}
    PRINTER_NAME: {PRINTER_NAME}
    PRINTING_ENABLED: {PRINTING_ENABLED}
""")

    printer = get_printer()

    queue.set_processor(printer.print)
    queue.set_canceller(printer.cancel_print)

    async with create_task_group() as tg:
        # before
        tg.start_soon(printer.monitor_connection)
        tg.start_soon(printer.monitor_info, MONITOR_INFO_DELAY)
        tg.start_soon(queue.monitor_queue)
        yield  # during
        # after
        logger.info("Stopping monitors")
        tg.cancel_scope.cancel()
        logger.info("Stopped monitors")


app = FastAPI(lifespan=lifespan, logger=logger)

app.include_router(router.router)