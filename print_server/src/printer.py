import logging
import os
from datetime import datetime
from io import BytesIO

from anyio import sleep as asleep, get_cancelled_exc_class
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
        if self.is_connected():
            await self._interface.print_image(BytesIO(data))
            return True

        else:
            logger.info("Not connected to device")
            return False

    async def check_connection(self):
        if not self.is_connected():
            logger.info("Printer not connected, attempting to connect")
            try:
                await self._interface.connect()
                if self.is_connected():
                    logger.info("Connected")
                else:
                    logger.error("Unable to connect")
            except get_cancelled_exc_class():
                raise
            except:
                logger.exception(f"Error connecting to printer")

    async def monitor_connection(self):
        logger.info("Starting connection monitor loop")
        try:
            while True:
                await self.check_connection()
                await asleep(self.delay_seconds)
        except get_cancelled_exc_class():
            logger.info("Disconnecting")
            await self._interface.disconnect()
            raise

    def is_connected(self):
        return self._interface.client and self._interface.client.is_connected

    async def cancel_print(self):
        await self._interface.cancel_print()
