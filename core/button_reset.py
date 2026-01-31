import RPi.GPIO as GPIO
import time

RESET_PIN = 5  # GPIO5
_last_state = 1
_last_time = 0

def init_button():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RESET_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def is_reset_pressed():
    global _last_state, _last_time

    state = GPIO.input(RESET_PIN)
    now = time.time()

    # detect falling edge + debounce 0.5s
    if _last_state == GPIO.HIGH and state == GPIO.LOW:
        if now - _last_time > 0.5:
            _last_time = now
            _last_state = state
            return True

    _last_state = state
    return False
