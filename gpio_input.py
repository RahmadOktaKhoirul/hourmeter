import RPi.GPIO as GPIO
from config import HM_GPIO_PIN, GPIO_ACTIVE_LOW

class HMInput:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(
            HM_GPIO_PIN,
            GPIO.IN,
            pull_up_down=GPIO.PUD_UP if GPIO_ACTIVE_LOW else GPIO.PUD_DOWN
        )

    def is_on(self):
        val = GPIO.input(HM_GPIO_PIN)
        return val == 0 if GPIO_ACTIVE_LOW else val == 1
