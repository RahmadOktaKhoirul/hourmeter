#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import json
import os
from datetime import datetime

with open("/home/pi/hour-meter/config.json", "r") as f:
    config = json.load(f)

GPIO_PIN = config["gpio_pin"]
DATA_FILE = config["data_file"]
SAVE_INTERVAL = config["save_interval"]

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def save_to_json(total_sec):
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_seconds": int(total_sec)
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

total_seconds = 0
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        total_seconds = json.load(f).get("total_seconds", 0)

hm_running = False
start_time = 0
last_save = time.time()

try:
    while True:
        state = GPIO.input(GPIO_PIN)
        now = time.time()
        if state == 0 and not hm_running:
            hm_running = True
            start_time = now
        elif state == 1 and hm_running:
            hm_running = False
            total_seconds += (now - start_time)
            save_to_json(total_seconds)
        if hm_running and (now - last_save >= SAVE_INTERVAL):
            current_total = total_seconds + (now - start_time)
            save_to_json(current_total)
            last_save = now
        time.sleep(0.5)
finally:
    GPIO.cleanup()