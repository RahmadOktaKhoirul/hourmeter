import json
import os

DATA_FILE = "/home/pi/hourmeter/data/hm_state.json"
SESSION_FILE = "/home/pi/hourmeter/data/hm_sessions.json"

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

def load_sessions():
    if not os.path.exists(SESSION_FILE):
        return []
    try:
        with open(SESSION_FILE) as f:
            return json.load(f)
    except Exception:
        return []

def save_session(session):
    sessions = load_sessions()
    sessions.append(session)

    tmp = SESSION_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(sessions[-500:], f, indent=2)

    os.replace(tmp, SESSION_FILE)
