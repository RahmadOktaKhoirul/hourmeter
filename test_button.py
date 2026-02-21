import RPi.GPIO as GPIO
import time

PIN = 5  # GPIO5

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("=== GPIO5 PER SECOND LOGGER ===")

try:
    while True:
        state = GPIO.input(PIN)

        status = "ON (CONNECTED TO GND)" if state == GPIO.LOW else "OFF (OPEN)"

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] GPIO5 = {status}")

        time.sleep(1)

except KeyboardInterrupt:
    print("Exit")

finally:
    GPIO.cleanup()
