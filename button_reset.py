import time
import RPi.GPIO as GPIO
from core.storage import send_command

RESET_PIN = 17  # BCM 17 = Pin 11

GPIO.setmode(GPIO.BCM)
GPIO.setup(RESET_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("=== Button Reset Listener Started (GPIO17) ===")

last_state = GPIO.input(RESET_PIN)

try:
    while True:
        current_state = GPIO.input(RESET_PIN)

        # DETEKSI TEKAN (HIGH -> LOW)
        if last_state == GPIO.HIGH and current_state == GPIO.LOW:
            print(">>> RESET BUTTON PRESSED <<<")
            send_command("hmreset")
            print(">>> HM RESET COMMAND SENT <<<")
            time.sleep(1)  # debounce

        last_state = current_state
        time.sleep(0.05)

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
