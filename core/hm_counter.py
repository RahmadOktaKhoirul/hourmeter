import time

class HourMeter:
    def __init__(self, total_seconds=0):
        self.total_seconds = total_seconds
        self.run_seconds = 0

    def tick(self, running):
        if running:
            self.total_seconds += 1
            self.run_seconds += 1
        else:
            self.run_seconds = 0

    def format_hm(self):
        h = self.total_seconds // 3600
        m = (self.total_seconds % 3600) // 60
        s = self.total_seconds % 60
        return h, m, s
