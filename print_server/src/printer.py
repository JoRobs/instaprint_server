import logging
from pyinstaxble import InstaxBLE
from io import BytesIO

PRINTER_CONNECT_TIMEOUT=3

logger = logging.getLogger(__name__)

class Printer:
  _interface: InstaxBLE

  def __init__(self, interface=InstaxBLE(print_enabled=False)):
     self._interface = interface

  def print(self, data:bytes):
    self._interface.connect(PRINTER_CONNECT_TIMEOUT)
    if self._interface.peripheral and self._interface.peripheral.is_connected():
      self._interface.print_image(BytesIO(data))
      return True
    else:
      logger.info("Could not connect to device")
      return False
