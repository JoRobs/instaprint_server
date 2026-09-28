from dataclasses import dataclass
import logging
import os
from datetime import datetime
from io import BytesIO

from anyio import sleep as asleep, get_cancelled_exc_class
from PIL import Image
from pyinstaxble.instax_bleak import InstaxBLEAK
from pytz import timezone


PRINTER_CONNECT_TIMEOUT = 60
DEFAULT_DELAY_SECONDS = 10

logger = logging.getLogger(__name__)
tz = timezone(os.environ.get("TZ", "Australia/Melbourne"))

@dataclass
class PrinterInfo:
    film_remaining: int
    battery_percentage: int
    battery_state: str
    is_charging: bool
    is_printing: None

class Printer:
    _interface: InstaxBLEAK
    print_enabled: bool = False
    printer_info: PrinterInfo

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

    async def monitor_connection(self, delay_seconds=DEFAULT_DELAY_SECONDS):
        logger.info("Starting connection monitor loop")
        try:
            while True:
                await self.check_connection()
                await asleep(delay_seconds)
        except get_cancelled_exc_class():
            logger.info("Disconnecting")
            await self._interface.disconnect()
            raise

    def is_connected(self):
        return self._interface.client and self._interface.client.is_connected

    async def cancel_print(self):
        await self._interface.cancel_print()

    async def get_printer_info(self)->PrinterInfo:
        await self._interface.get_printer_info()
        printer_info = PrinterInfo(**{
            "film_remaining": self._interface.photos_left,
            "battery_percentage": self._interface.battery_percentage,
            "battery_state": self._interface.battery_state,
            "is_charging": self._interface.is_charging,
            "is_printing": None
        })
        return printer_info

    async def monitor_info(self, delay_seconds=DEFAULT_DELAY_SECONDS):
        logger.info("Starting printer info monitor loop")
        try:
            while True:
                self.printer_info = await self.get_printer_info()
                await asleep(delay_seconds)
        except get_cancelled_exc_class():
            logger.info("Stopping info monitoring")
            await self._interface.disconnect()
            raise

def get_printer():
    return Printer()