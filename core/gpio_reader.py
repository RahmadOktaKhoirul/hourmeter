import RPi.GPIO as GPIO
from config.settings import GPIO_PIN

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def is_hm_on():
    return GPIO.input(GPIO_PIN) == GPIO.LOW
