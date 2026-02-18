import json
import time
import os
import paho.mqtt.client as mqtt

DATA_FILE = "/home/pi/hourmeter/data/hm_state.json"

BROKER = "192.168.100.107"
TOPIC = "sensor/hm/slave01"
CLIENT_ID = "hm_slave01"

client = mqtt.Client(client_id=CLIENT_ID)
client.connect(BROKER, 1883, 60)
client.loop_start()

print("Slave MQTT started (hm_state forwarder)")

last_ts = None

while True:
    try:
        if not os.path.exists(DATA_FILE):
            time.sleep(1)
            continue

        with open(DATA_FILE) as f:
            data = json.load(f)

        raw = data.get("raw", [])
        if not raw:
            time.sleep(0.2)
            continue

        last = raw[-1]

        # publish hanya jika data baru
        if last.get("ts") == last_ts:
            time.sleep(0.1)
            continue

        last_ts = last["ts"]

        payload = {
            "device": "slave01",
            "ts": last["ts"],
            "state": last["state"],
            "hms": last["hms"],
            "hm": last["hm"],
            "total_seconds": last.get("total_seconds")
        }

        client.publish(TOPIC, json.dumps(payload), qos=1)
        print("MQTT SENT:", payload)

    except Exception as e:
        print("Slave error:", e)

    time.sleep(0.1)
