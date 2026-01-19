#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import json
import os
import threading
from datetime import datetime
from pymodbus.server import StartSerialServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer

# --- LOAD CONFIG ---
BASE_DIR = "/home/pi/hour-meter"
with open(f"{BASE_DIR}/config.json", "r") as f:
    config = json.load(f)

# --- MODBUS SETUP ---
# Menyiapkan 10 Holding Registers. Register 0 & 1 digunakan untuk total_seconds (32-bit)
store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [0]*10))
context = ModbusServerContext(slaves=store, single=True)

def update_modbus_registers(sec):
    """Memasukkan data detik ke register Modbus (32-bit split)"""
    high_16 = (int(sec) >> 16) & 0xFFFF
    low_16 = int(sec) & 0xFFFF
    context[0].setValues(3, 0, [high_16, low_16])

def save_to_json(total_sec):
    """Menyimpan data ke file JSON sebagai cadangan"""
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_seconds": int(total_sec),
        "hm_decimal": round(total_sec / 3600, 2)
    }
    with open(config["data_file"], "w") as f:
        json.dump(data, f, indent=2)

# --- THREAD 1: LOGIC SENSOR ---
def logic_sensor_thread():
    print("LOGIC: Sensor thread started.")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config["gpio_pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Load data awal
    total_seconds = 0
    if os.path.exists(config["data_file"]):
        try:
            with open(config["data_file"], "r") as f:
                total_seconds = json.load(f).get("total_seconds", 0)
        except: pass

    hm_running = False
    start_time = 0
    last_save = time.time()

    while True:
        state = GPIO.input(config["gpio_pin"]) # 0 = ON
        now = time.time()

        if state == 0 and not hm_running:
            hm_running = True
            start_time = now
            print(f"[{datetime.now()}] STATUS: Mesin ON")

        elif state == 1 and hm_running:
            hm_running = False
            total_seconds += (now - start_time)
            save_to_json(total_seconds)
            print(f"[{datetime.now()}] STATUS: Mesin OFF | Total: {int(total_seconds)}s")

        # Hitung angka berjalan (real-time)
        current_val = total_seconds + (now - start_time) if hm_running else total_seconds
        
        # Update ke Modbus setiap loop agar Master mendapat data paling baru
        update_modbus_registers(current_val)

        # Auto-save ke JSON setiap interval tertentu
        if hm_running and (now - last_save >= config["save_interval"]):
            save_to_json(current_val)
            last_save = now
        
        time.sleep(0.2) # Respon cepat

# --- MAIN: MODBUS SERVER ---
if __name__ == "__main__":
    # Jalankan perhitungan jam di background
    t = threading.Thread(target=logic_sensor_thread, daemon=True)
    t.start()

    print(f"MODBUS: Server started on {config['port_rs485']} (ID: {config['modbus_id']})")
    
    try:
        StartSerialServer(
            context=context,
            framer=ModbusRtuFramer,
            port=config["port_rs485"],
            baudrate=config["baudrate"],
            stopbits=1,
            bytesize=8,
            parity='N',
            slave=config["modbus_id"]
        )
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        GPIO.cleanup()