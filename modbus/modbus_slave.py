from pymodbus.server.sync import StartSerialServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
import json
import time
import threading

DATA_FILE = "/home/pi/hourmeter/data/hm_state.json"
SLAVE_ID = 1

# ======================
# LOAD HM DATA
# ======================
def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

# ======================
# UPDATE MODBUS REGISTERS
# ======================
def update_registers(context):
    print("Register update thread started")

    while True:
        try:
            data = load_data()
            total_seconds = int(data.get("total_seconds", 0))

            h = total_seconds // 3600
            m = (total_seconds % 3600) // 60
            s = total_seconds % 60

            hi = (total_seconds >> 16) & 0xFFFF
            lo = total_seconds & 0xFFFF

            hm_format = int((h + m / 60) * 100)

            status = 0
            if data.get("raw"):
                status = 1 if data["raw"][-1]["state"] == "ON" else 0

            values = [
                h,          # HR[0]
                m,          # HR[1]
                s,          # HR[2]
                hi,         # HR[3]
                lo,         # HR[4]
                hm_format,  # HR[5]
                status      # HR[6]
            ]

            context[SLAVE_ID].setValues(3, 0, values)
            print("Registers updated:", values)

        except Exception as e:
            print("Update error:", e)

        time.sleep(1)

# ======================
# DATASTORE
# ======================
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0]*10)
)

context = ModbusServerContext(
    slaves={SLAVE_ID: store},
    single=False
)

# ======================
# START UPDATE THREAD
# ======================
threading.Thread(
    target=update_registers,
    args=(context,),
    daemon=True
).start()

print("Modbus slave running...")

# ======================
# START SERIAL SERVER
# ======================
StartSerialServer(
    context=context,
    port="/dev/ttyUSB0",
    baudrate=9600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1
)
