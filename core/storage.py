import json, os, time
from config.settings import DATA_FILE

def load_state():
    if not os.path.exists(DATA_FILE):
        return {"total_seconds": 0, "raw": []}
    with open(DATA_FILE) as f:
        return json.load(f)

def save_state(total_seconds, raw):
    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_seconds": total_seconds,
        "last_hour": format_time(total_seconds),
        "raw": raw[-10:]
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def format_time(sec):
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02}:{m:02}:{s:02}"
