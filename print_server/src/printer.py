import logging
from pyinstaxble import InstaxBLE
from io import BytesIO
from PIL import Image
from datetime import datetime

PRINTER_CONNECT_TIMEOUT=60

logger = logging.getLogger(__name__)

class Printer:
  _interface: InstaxBLE

  def __init__(self, interface=InstaxBLE(print_enabled=True)):
     self._interface = interface

  def print(self, data:bytes):
    img_path = f"./data/temp_job_image_{int(datetime.now().timestamp())}.jpeg"
    img = Image.open(BytesIO(data))
    img.convert("RGB").save(img_path)
    # return True
    self._interface.connect(PRINTER_CONNECT_TIMEOUT)
    if self._interface.peripheral and self._interface.peripheral.is_connected():
      self._interface.print_image(img_path)
      return True

    else:
      logger.info("Could not connect to device")
      return False
