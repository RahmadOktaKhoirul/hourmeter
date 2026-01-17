import json
import os
from datetime import datetime
from config import DATA_FILE

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "total_seconds": 0,
            "raw": []
        }
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_raw(data, hm_on):
    raw = data.get("raw", [])
    raw.append({
        "timestamp": datetime.now().isoformat(),
        "hm": hm_on
    })
    data["raw"] = raw[-10:]  # simpan 10 terakhir
