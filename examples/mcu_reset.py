# External module imports
import RPi.GPIO as GPIO
import time

# Pin Definitons:
gpio_ue = 24
gpio_kepler = 10
gpio_tddsync = 25

# Pin Setup:
GPIO.setmode(GPIO.BCM)

# Unregister and Register UE module
GPIO.setup(gpio_kepler, GPIO.OUT) # LED pin set as output
GPIO.output(gpio_kepler, False)
time.sleep(5)
GPIO.output(gpio_kepler, True)
