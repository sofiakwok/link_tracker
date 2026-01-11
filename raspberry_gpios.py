# gpio_blink.py
# by Scott Kildall (www.kildall.com)
# LED is on pin 4, use a 270 Ohm resistor to ground

import RPi.GPIO as GPIO
import time
import numpy as np

class LEDs():
    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.OUT)
        self.state = True

        self.leds_on = np.zeros(25)

    def set_led_on(self, stops_on):
        # first, iterate through the list of leds and turn all of them off
        for i in range(25):
            GPIO.output(i, False)
            self.leds_on[i] = 0

        time.sleep(1)
                
        for stop in stops_on:
            GPIO.output(stop,True)
            self.leds_on[stop] = 1