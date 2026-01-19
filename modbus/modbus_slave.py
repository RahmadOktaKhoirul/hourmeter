from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext
from pymodbus.server.sync import StartSerialServer
import json
from config.settings import DATA_FILE

def run_modbus():
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(1, [0]*20)
    )

    context = store

    def updater():
        while True:
            with open(DATA_FILE) as f:
                d = json.load(f)

            total = d["total_seconds"]
            h, m, s = map(int, d["last_hour"].split(":"))

            store.setValues(3, 1, [total >> 16, total & 0xFFFF])
            store.setValues(3, 3, [h, m])
            store.setValues(3, 5, [1])

            time.sleep(1)

    import threading
    threading.Thread(target=updater, daemon=True).start()

    StartSerialServer(
        context,
        port="/dev/ttyUSB0",
        baudrate=9600,
        timeout=1
    )
