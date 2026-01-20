from pymodbus.server.sync import StartSerialServer
from pymodbus.datastore import (
    ModbusSlaveContext,
    ModbusServerContext,
    ModbusSequentialDataBlock
)

import json
import time
import threading

DATA_FILE = "/home/pi/hourmeter/data/hm_state.json"

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def parse_hms(hms):
    try:
        h, m, s = hms.split(":")
        return int(h), int(m), int(s)
    except:
        return 0, 0, 0

def update_registers(context):
    while True:
        try:
            data = load_data()

            # Parse HH:MM:SS
            hours, minutes, seconds = parse_hms(
                data.get("last_hour", "00:00:00")
            )

            total_seconds = int(data.get("total_seconds", 0))
            hm_display = int(float(data.get("hm_display", 0)) * 100)

            # Ambil status terakhir
            status = 0
            raw = data.get("raw", [])
            if raw:
                status = 1 if raw[-1].get("state") == "ON" else 0

            hi = (total_seconds >> 16) & 0xFFFF
            lo = total_seconds & 0xFFFF

            values = [
                hours,
                minutes,
                seconds,
                hi,
                lo,
                hm_display,
                status
            ]

            context[0x00].setValues(3, 0, values)

            print("Registers updated:", values)

        except Exception as e:
            print("Modbus update error:", e)

        time.sleep(1)

store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0] * 20)
)

context = ModbusServerContext(slaves=store, single=True)

threading.Thread(
    target=update_registers,
    args=(context,),
    daemon=True
).start()

print("Modbus slave running...")

StartSerialServer(
    context=context,
    port="/dev/ttyUSB0",
    baudrate=9600,
    parity='N',
    stopbits=1,
    bytesize=8
)
