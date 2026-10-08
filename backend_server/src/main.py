import logging
from contextlib import asynccontextmanager

from anyio import (
    create_task_group,
)
from fastapi import FastAPI

from . import router
from .job_queue import get_queue
from .printer import get_printer
from .types import Environment
from .utils import get_env

DUMMY_PRINTER = get_env("DUMMY_PRINTER", "False") == "True"
ENVIRONMENT = get_env("ENVIRONMENT", Environment.DEV)
JOB_TIME_BUFFER = int(get_env("JOB_TIME_BUFFER", 5))
LOG_LEVEL = get_env("LOG_LEVEL", logging.INFO)
LOG_LEVEL_BLEAK = get_env("LOG_LEVEL_BLEAK", logging.ERROR)
LOG_LEVEL_PYINSTAXBLE = get_env("LOG_LEVEL_PYINSTAXBLE", logging.INFO)
MONITOR_INFO_DELAY = int(get_env("MONITOR_INFO_DELAY", 5))
PRINT_TIME_BUFFER = int(get_env("PRINT_TIME_BUFFER", 20))
PRINTER_ADDRESS = get_env("PRINTER_ADDRESS", None)
PRINTER_NAME = get_env("PRINTER_NAME", None)
PRINTING_ENABLED = get_env("PRINTING_ENABLED", "False") == "True"
PRINTING_TIMEOUT = int(get_env("PRINTING_TIMEOUT", 60))

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
    logger.info(f"""
Running with environment
    DUMMY_PRINTER: {DUMMY_PRINTER}
    ENVIRONMENT: {ENVIRONMENT}
Printer interface config
    MONITOR_INFO_DELAY: {MONITOR_INFO_DELAY}
    PRINT_TIME_BUFFER: {PRINT_TIME_BUFFER}
    PRINTER_ADDRESS: {PRINTER_ADDRESS}
    PRINTER_NAME: {PRINTER_NAME}
    PRINTING_ENABLED: {PRINTING_ENABLED}
    PRINTING_TIMEOUT: {PRINTING_TIMEOUT}
JobQueue config
    JOB_TIME_BUFFER: {JOB_TIME_BUFFER}
""")
    logger.info("Creating job queue")
    queue = get_queue(
        delay_seconds=5,
        job_max_retry=256,
    )
    logger.info(get_queue())
    logger.info("Creating printer")
    printer = get_printer(
        device_address=PRINTER_ADDRESS,
        device_name=PRINTER_NAME,
        print_enabled=PRINTING_ENABLED,
        print_time_buffer=PRINT_TIME_BUFFER,
        print_timeout=PRINTING_TIMEOUT,
    )
    logger.info(get_printer())

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
