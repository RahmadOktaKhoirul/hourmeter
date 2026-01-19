#!/usr/bin/python3
import json, os, time, threading
from pymodbus.server import StartSerialServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer

with open("/home/pi/hour-meter/config.json", "r") as f:
    config = json.load(f)

store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [0]*10))
context = ModbusServerContext(slaves=store, single=True)

def update_registers():
    while True:
        try:
            if os.path.exists(config["data_file"]):
                with open(config["data_file"], "r") as f:
                    sec = json.load(f).get("total_seconds", 0)
                # Pecah 32-bit ke dua 16-bit registers
                context[0].setValues(3, 0, [(sec >> 16) & 0xFFFF, sec & 0xFFFF])
        except: pass
        time.sleep(2)

threading.Thread(target=update_registers, daemon=True).start()

StartSerialServer(context=context, framer=ModbusRtuFramer, port=config["port_rs485"], 
                  baudrate=config["baudrate"], slave=config["modbus_id"])