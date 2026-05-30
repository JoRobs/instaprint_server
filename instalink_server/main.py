import logging

from fastapi import FastAPI
from anyio import (
    create_task_group,
)
from contextlib import asynccontextmanager

from .print_queue import PrintQueue
from .routers import router

MAX_JOB_BUFFER_SIZE = 256

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before fastapi starts
    logger.info("Creating job queue")
    queue = PrintQueue(MAX_JOB_BUFFER_SIZE)

    async with create_task_group() as tg:
        # Start job processor
        logger.info("Start queue monitoring")
        tg.start_soon(queue.monitor_queue)
        logger.info("Monitoring queue")
        yield # during
        # after
        logger.info("Stopping queue monitoring")
        tg.cancel_scope.cancel()
        logger.info("Stopped queue monitoring")


app = FastAPI(lifespan=lifespan, logger=logger)
app.include_router(router.router)
