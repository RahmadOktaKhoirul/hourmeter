from datetime import timedelta
from storage import load_data, save_data, add_raw

class HourMeter:
    def __init__(self):
        self.data = load_data()
        self.running_seconds = 0

    def tick(self, hm_on):
        add_raw(self.data, hm_on)

        if hm_on:
            self.running_seconds += 1
            self.data["total_seconds"] += 1
        else:
            self.running_seconds = 0

        save_data(self.data)

    def get_display(self):
        total = self.data["total_seconds"]
        td = timedelta(seconds=total)
        h, m, s = td.seconds // 3600, (td.seconds % 3600) // 60, td.seconds % 60

        return {
            "total_seconds": total,
            "last_hour": f"{h:02}:{m:02}:{s:02}",
            "hm_display": f"{h}.{m:02}"
        }
