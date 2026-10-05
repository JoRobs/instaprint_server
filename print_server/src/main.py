import logging
from contextlib import asynccontextmanager
from os import environ

from anyio import (
    create_task_group,
)
from fastapi import (
    Depends,
    FastAPI,
)
from fastapi.staticfiles import StaticFiles

from .job_queue import JobQueue, get_queue
from .printer import Printer
from . import router
from .types import Environment

ENVIRONMENT = environ.get("ENVIRONMENT", Environment.DEV)
LOG_LEVEL = environ.get("LOG_LEVEL", logging.INFO)
LOG_LEVEL_BLEAK = environ.get("LOG_LEVEL_BLEAK", logging.ERROR)
LOG_LEVEL_PYINSTAXBLE = environ.get("LOG_LEVEL_PYINSTAXBLE", logging.INFO)
PRINTER_ADDRESS = environ.get("PRINTER_ADDRESS", None)
PRINTER_NAME = environ.get("PRINTER_NAME", None)
PRINTING_ENABLED = environ.get("PRINTING_ENABLED", "False") == "True"

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
    queue = JobQueue()
    logger.info(f"""
Running as environment
    ENVIRONMENT: {ENVIRONMENT}
""")
    logger.info(f"""
Creating printer interface
    PRINTER_ADDRESS: {PRINTER_ADDRESS}
    PRINTER_NAME: {PRINTER_NAME}
    PRINTING_ENABLED: {PRINTING_ENABLED}
""")
    printer = Printer(
        device_address=PRINTER_ADDRESS,
        device_name=PRINTER_NAME,
        print_enabled=PRINTING_ENABLED,
    )
    queue.set_processor(printer.print)
    queue.set_canceller(printer.cancel_print)

    # If DEV, monkey patch to disable caching for static files
    if ENVIRONMENT == Environment.DEV:
        logger.info("It is DEV")
    else:
        logger.info("It is not DEV")

    StaticFiles.is_not_modified = lambda self, *args, **kwargs: False

    async with create_task_group() as tg:
        # before
        tg.start_soon(printer.monitor_connection)
        tg.start_soon(printer.monitor_info)
        tg.start_soon(queue.monitor_queue)
        yield  # during
        # after
        logger.info("Stopping monitors")
        tg.cancel_scope.cancel()
        logger.info("Stopped monitors")


app = FastAPI(
    lifespan=lifespan, logger=logger, dependencies=[Depends(get_queue)]
)
app.include_router(router.router, dependencies=[Depends(get_queue)])

app.mount(path="/static", app=StaticFiles(directory="./static"), name="static")
app.mount(
    path="/plugins", app=StaticFiles(directory="./plugins"), name="plugins"
)
app.mount(
    path="/resources",
    app=StaticFiles(directory="./resources"),
    name="resources",
)
