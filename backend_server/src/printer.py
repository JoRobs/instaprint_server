import logging
import os
from dataclasses import dataclass
from io import BytesIO

from anyio import get_cancelled_exc_class
from anyio import sleep as asleep
from pyinstaxble.instax_bleak import InstaxBLEAK, PrinterTimeoutError
from pytz import timezone

from .types import Dictify

PRINTER_CONNECT_TIMEOUT = 60
DEFAULT_DELAY_SECONDS = 10

logger = logging.getLogger(__name__)
tz = timezone(os.environ.get("TZ", "Australia/Melbourne"))


@dataclass
class PrinterInfo(Dictify):
    battery_percentage: int
    battery_state: str
    film_remaining: int
    is_charging: bool
    is_connected: bool
    is_printing: bool


class Printer:
    _interface: InstaxBLEAK
    device_address: str
    device_name: str
    initialised: bool = False
    instance = None
    print_enabled: bool = False
    print_timeout: int
    printer_info: PrinterInfo = PrinterInfo(
        battery_percentage=-1,
        battery_state="",
        film_remaining=-1,
        is_charging=False,
        is_connected=False,
        is_printing=False,
    )

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(
        self,
        device_name=None,
        device_address=None,
        print_enabled=False,
        print_timeout=60,
        print_time_buffer=20,
    ):
        if self.initialised:
            return

        self.print_enabled = print_enabled
        self.device_name = device_name
        self.device_address = device_address
        self.print_timeout = print_timeout
        self._interface = InstaxBLEAK(
            device_name=device_name,
            device_address=device_address,
            print_enabled=self.print_enabled,
            print_time_buffer=print_time_buffer,
        )
        self.initialised = True

    def __str__(self):
        return (
            f"Printer("
            f"device_name={self.device_name}, "
            f"device_address={self.device_address}, "
            f"print_enabled={self.print_enabled}, "
            f"print_timeout={self.print_timeout}, "
            f"initialised={self.initialised}"
            f")"
        )

    async def init_connection(self):
        await self._interface.connect()

    async def print(self, data: bytes) -> bool:
        print_success = False
        self.printer_info.is_printing = True
        if self.is_connected():
            try:
                await self._interface.print_image(
                    BytesIO(data), timeout=self.print_timeout
                )
                self.printer_info.film_remaining -= 1
                print_success = True
            except PrinterTimeoutError:
                logger.warning("Print command timed out.")
                print_success = False
        else:
            logger.info("Not connected to device")
            print_success = False

        return print_success

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
                logger.exception("Error connecting to printer")

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
        return self._interface.is_connected()

    def is_uploading_image(self):
        """
        Check if the awaiting_print Event is not `set` indicating it is waiting
        for something to `set` it. Confirming the print is done. Only returns
        true while an image is being uploaded for printing
        """

        return not self._interface.awaiting_print.is_set()

    async def cancel_print(self):
        await self._interface.cancel_print()

    async def get_printer_info(self) -> PrinterInfo:
        try:
            await self._interface.get_printer_info()
        except PrinterTimeoutError:
            raise
        printer_info = PrinterInfo(
            battery_percentage=self._interface.battery_percentage,
            battery_state=self._interface.battery_state,
            film_remaining=self._interface.photos_left,
            is_charging=self._interface.is_charging,
            is_connected=self.is_connected(),
            is_printing=self.is_uploading_image(),
        )
        return printer_info

    async def monitor_info(self, delay_seconds=DEFAULT_DELAY_SECONDS):
        logger.info("Starting printer info monitor loop")
        try:
            while True:
                if self.is_uploading_image():
                    logger.debug("Printer is printing, will not refresh info.")
                elif self.is_connected():
                    try:
                        logger.debug("Getting print info...")
                        self.printer_info = await self.get_printer_info()
                        logger.debug("Refreshed printer info")
                    except PrinterTimeoutError as e:
                        logger.warning(f"Get printer info timed out: {e}")

                # Always update
                self.printer_info.is_printing = self.is_uploading_image()
                self.printer_info.is_connected = self.is_connected()

                await asleep(delay_seconds)
        except get_cancelled_exc_class():
            logger.info("Stopping info monitoring")
            raise


class DummyPrinter:
    instance = None
    initialised: bool = False
    print_enabled: bool = False
    printer_info: PrinterInfo = PrinterInfo(
        battery_percentage=100,
        battery_state="charging",
        film_remaining=1,
        is_charging=True,
        is_connected=True,
        is_printing=False,
    )

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(
        self,
        device_name=None,
        device_address=None,
        print_enabled=False,
        print_time_buffer=20,
    ):
        if self.initialised:
            return

        self.print_enabled = print_enabled
        self.device_name = device_name
        self.device_address = device_address
        self.initialised = True

    async def init_connection(self):
        return

    async def print(self, data: bytes) -> bool:
        self.printer_info.is_printing = True
        await asleep(5)
        self.printer_info.is_printing = False
        return True

    async def check_connection(self):
        await asleep(5)

    async def monitor_connection(self, delay_seconds=DEFAULT_DELAY_SECONDS):
        logger.info("Starting connection monitor loop")
        try:
            while True:
                await self.check_connection()
                await asleep(delay_seconds)
        except get_cancelled_exc_class():
            raise

    def is_connected(self):
        return True

    async def cancel_print(self):
        await asleep(5)

    async def get_printer_info(self) -> PrinterInfo:
        await asleep(5)
        return self.printer_info

    async def monitor_info(self, delay_seconds=DEFAULT_DELAY_SECONDS):
        logger.info("Starting printer info monitor loop")
        try:
            while True:
                if self.is_connected():
                    try:
                        logger.debug("Getting print info...")
                        self.printer_info = await self.get_printer_info()
                        logger.debug("Refreshed printer info")
                    except PrinterTimeoutError as e:
                        logger.warning(f"Get printer info timed out: {e}")

                # Always update
                self.printer_info.is_printing = False
                self.printer_info.is_connected = self.is_connected()
                await asleep(delay_seconds)
        except get_cancelled_exc_class():
            logger.info("Stopping info monitoring")
            raise


def get_printer():
    if os.environ.get("DUMMY_PRINTER", "False") == "True":
        return DummyPrinter()
    else:
        return Printer()
