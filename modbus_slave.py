from pymodbus.server.sync import StartSerialServer
from pymodbus.datastore import ModbusSlaveContext, ModbusSequentialDataBlock
from pymodbus.datastore import ModbusServerContext
import time
from storage import load_data

store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(1, [0]*10)
)
context = ModbusServerContext(slaves=store, single=True)

def update_registers():
    while True:
        d = load_data()
        total = d["total_seconds"]

        h = total // 3600
        m = (total % 3600) // 60

        store.setValues(3, 1, [total >> 16, total & 0xFFFF])
        store.setValues(3, 3, [h])
        store.setValues(3, 4, [m])
        time.sleep(1)

def start():
    import threading
    threading.Thread(target=update_registers, daemon=True).start()

    StartSerialServer(
        context,
        port="/dev/ttyUSB0",
        baudrate=9600,
        parity="N",
        stopbits=1
    )
