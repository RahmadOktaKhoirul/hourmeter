import json
import os

DATA_FILE = "/home/pi/hourmeter/data/hm_state.json"

def load_state():
    if not os.path.exists(DATA_FILE):
        return {
            "total_seconds": 0,
            "raw": [],
            "events": []
        }

    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except Exception:
        return {
            "total_seconds": 0,
            "raw": [],
            "events": []
        }

def save_state(total_seconds, raw, events):
    data = {
        "total_seconds": round(total_seconds, 2),
        "raw": raw[-1000:],
        "events": events[-200:]
    }

    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)

    os.replace(tmp, DATA_FILE)
