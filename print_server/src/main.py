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

from .job_queue import get_queue
from .printer import Printer
from .routers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
logging.getLogger("pyinstaxble").setLevel(logging.DEBUG)
logging.getLogger("bleak").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

PRINTER_ADDRESS=environ.get("PRINTER_ADDRESS", None)
PRINTER_NAME=environ.get("PRINTER_NAME", None)
PRINTING_ENABLED=environ.get("PRINTING_ENABLED", None) == "True"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before fastapi starts
    logger.info("Creating job queue")
    printer = Printer(
        device_address=PRINTER_ADDRESS,
        device_name=PRINTER_NAME,
        print_enabled=PRINTING_ENABLED,
    )
    queue = get_queue()
    queue.set_processor(printer.print)
    queue.set_canceller(printer.cancel_print)

    async with create_task_group() as tg:
        # Start job processor
        tg.start_soon(printer.monitor_connection)
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

app.mount(
    path="/static", app=StaticFiles(directory="./static"), name="static"
)
app.mount(
    path="/plugins", app=StaticFiles(directory="./plugins"), name="plugins"
)
