from pymodbus.server.sync import StartSerialServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
import logging

# Aktifkan logging pymodbus
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Holding register: alamat 0 berisi angka 1234
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [1234] * 10)
)

context = ModbusServerContext(
    slaves=store,
    single=True
)

print("=== MODBUS SLAVE MINIMAL RUNNING ===")

StartSerialServer(
    context=context,
    port="/dev/ttyUSB0",
    baudrate=9600,
    parity="N",
    stopbits=1,
    bytesize=8,
    timeout=1
)
