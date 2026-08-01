import logging
import os
from datetime import datetime
from io import BytesIO

from PIL import Image
from pyinstaxble import InstaxBLE
from pytz import timezone

PRINTER_CONNECT_TIMEOUT = 60

logger = logging.getLogger(__name__)
tz = timezone(os.environ.get("TZ", "Australia/Melbourne"))


class Printer:
    _interface: InstaxBLE
    print_enabled: bool

    def __init__(self, print_enabled=False):
        self.print_enabled = print_enabled
        self._interface = InstaxBLE(print_enabled=self.print_enabled)

    def print(self, data: bytes):
        img_path = (
            f"./data/temp_job_image_{int(datetime.now(tz).timestamp())}.jpeg"
        )
        img = Image.open(BytesIO(data))
        img.convert("RGB").save(img_path)
        # return True
        self._interface.connect(PRINTER_CONNECT_TIMEOUT)
        if (
            self._interface.peripheral
            and self._interface.peripheral.is_connected()
        ):
            self._interface.print_image(img_path)
            return True

        else:
            logger.info("Could not connect to device")
            return False
