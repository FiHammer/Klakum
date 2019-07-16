import RPi.GPIO as GPIO
import time


path_seg = "/"





class Relay:
    def __init__(self, pin):
        self.pin = pin
        self.value = 0
        GPIO.setup(pin, GPIO.OUT, initial=1)

    def set(self, value):
        if type(value) == str:
            try:
                value = int(value)
            except ValueError:
                if value == "True":
                    value = 1
                elif value == "False":
                    value = 0
                else:
                    if value:
                        value = 1
                    else:
                        value = 0
        elif value:
            value = 1
        else:
            value = 0

        self.value = value
        if self.value:
            GPIO.output(self.pin, 0)  # an
        else:
            GPIO.output(self.pin, 1)  # aus

    def get(self):
        return self.value

    def switch(self):
        if self.value:
            self.set(0)
        else:
            self.set(1)


class RelaySurge:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT, initial=1)

    def switch(self):
        GPIO.output(self.pin, 0)
        time.sleep(0.1)
        GPIO.output(self.pin, 1)
