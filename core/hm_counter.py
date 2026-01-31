import time

class HourMeter:
    def __init__(self, total_seconds=0, factor=1.0):
        self.total_seconds = float(total_seconds)
        self.factor = factor
        self._last_time = time.monotonic()

    def tick(self, hm_on):
        now = time.monotonic()
        delta = now - self._last_time
        self._last_time = now

        if hm_on and delta > 0:
            self.total_seconds += delta * self.factor
