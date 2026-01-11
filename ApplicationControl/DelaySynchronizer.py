# DelaySynchronizer.py
import time


class DelaySynchronizer:

    def __init__(self, delay_seconds: int):
        self._delay = delay_seconds

    def wait(self):
        time.sleep(self._delay)
