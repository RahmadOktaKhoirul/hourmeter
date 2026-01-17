import time
from gpio_input import HMInput
from hourmeter import HourMeter
from logger import log
from modbus_slave import start
from config import SAMPLE_INTERVAL

def main():
    log("=== Hour Meter Service Started ===")
    hm_input = HMInput()
    hm = HourMeter()

    start()  # Modbus jalan background

    while True:
        on = hm_input.is_on()
        hm.tick(on)

        disp = hm.get_display()
        log(f"HM={'ON' if on else 'OFF'} TOTAL={disp['last_hour']}")

        time.sleep(SAMPLE_INTERVAL)

if __name__ == "__main__":
    main()
