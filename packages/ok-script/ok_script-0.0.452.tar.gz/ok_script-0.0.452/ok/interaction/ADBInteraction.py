import time

from ok import Logger
from ok.interaction.BaseInteraction import BaseInteraction

logger = Logger.get_logger(__name__)


class ADBBaseInteraction(BaseInteraction):

    def __init__(self, device_manager, capture, device_width, device_height):
        super().__init__(capture)
        self.device_manager = device_manager
        self.width = device_width
        self.height = device_height
        logger.info(f"width: {self.width}, height: {self.height}")
        if self.width == 0 or self.height == 0:
            logger.warning(f"Could not parse screen resolution.")
            # raise RuntimeError(f"ADBBaseInteraction: Could not parse screen resolution.")

    def send_key(self, key, down_time=0.02, after_sleep=0):
        self.device_manager.device.shell(f"input keyevent {key}")
        if after_sleep > 0:
            time.sleep(after_sleep)

    def input_text(self, text):
        # Convert each character to its Unicode code point
        # unicode_code_points = [ord(char) for char in text]
        #
        # # Iterate over the Unicode code points and send input key events
        # for code_point in unicode_code_points:
        self.device_manager.shell(f"input text {text}")

    def swipe(self, from_x, from_y, to_x, to_y, duration, settle_time=0.1):
        self.device_manager.device.shell(f"input swipe {from_x} {from_y} {to_x} {to_y} {duration}")
        if settle_time > 0:
            time.sleep(settle_time)

    def click(self, x=-1, y=-1, move_back=False, name=None, down_time=0.01, move=True):
        super().click(x, y, name=name)
        x = int(x * self.width / self.capture.width)
        y = int(y * self.height / self.capture.height)
        self.device_manager.shell(f"input tap {x} {y}")

    def back(self, after_sleep=0):
        self.send_key('KEYCODE_BACK', after_sleep=after_sleep)
