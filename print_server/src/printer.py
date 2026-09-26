import logging
import os
from datetime import datetime
from io import BytesIO

from anyio import sleep as asleep
from PIL import Image
from pyinstaxble.instax_bleak import InstaxBLEAK
from pytz import timezone


PRINTER_CONNECT_TIMEOUT = 60

logger = logging.getLogger(__name__)
tz = timezone(os.environ.get("TZ", "Australia/Melbourne"))


class Printer:
    _interface: InstaxBLEAK
    print_enabled: bool = False
    delay_seconds: int = 2

    def __init__(self, device_name=None, device_address=None, print_enabled=False):
        self.print_enabled = print_enabled
        self.device_name = device_name
        self.device_address = device_address
        self._interface = InstaxBLEAK(
            device_name=device_name,
            device_address=device_address,
            print_enabled=self.print_enabled
        )

    async def init_connection(self):
        await self._interface.connect()

    async def print(self, data: bytes):
        img_path = (
            f"./data/temp_job_image_{int(datetime.now(tz).timestamp())}.jpeg"
        )
        img = Image.open(BytesIO(data))
        img.convert("RGB").save(img_path)

        if self.is_connected():
            await self._interface.print_image(img_path)
            return True

        else:
            logger.info("Could not connect to device")
            return False

    async def monitor_connection(self):
        logger.info("Starting connection monitor")
        while True:
            if not self.is_connected():
                logger.info("Printer not connected, attempting to connect")
                try:
                    await self._interface.connect()
                    if self.is_connected():
                        logger.info("Connected")
                    else:
                        logger.error("Unable to connect")

                except:
                    logger.exception(f"Error connecting to printer")

            await asleep(self.delay_seconds)

    def is_connected(self):
        return self._interface.client and self._interface.client.is_connected
