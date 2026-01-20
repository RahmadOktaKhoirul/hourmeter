import json
import os

DATA_FILE = "/home/pi/hourmeter/data/hm_state.json"
COMMAND_FILE = "/home/pi/hourmeter/data/command.txt"

def load_state():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE) as f:
        return json.load(f)

def save_state(total_seconds, raw, events):
    data = load_state()
    data["total_seconds"] = total_seconds
    data["raw"] = raw[-1000:]      # batasi biar file tidak membengkak
    data["events"] = events[-100:] # simpan histori reset
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ==============================
# COMMAND HANDLING (INI KUNCI)
# ==============================

def send_command(cmd):
    with open(COMMAND_FILE, "w") as f:
        f.write(cmd)

def check_command():
    if not os.path.exists(COMMAND_FILE):
        return None

    with open(COMMAND_FILE) as f:
        cmd = f.read().strip()

    os.remove(COMMAND_FILE)
    return cmd
