import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)


IRTrackingPinLL = 12
IRTrackingPinL = 13
IRTrackingPinR = 14
IRTrackingPinRR = 15


def setup():
    GPIO.setmode(GPIO.BCM) # Set the GPIO pins as BCM
    GPIO.setup(IRTrackingPinLL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(IRTrackingPinL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(IRTrackingPinR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(IRTrackingPinRR, GPIO.IN, pull_up_down=GPIO.PUD_UP)



def loop():
    while True:
        if GPIO.input(IRTrackingPinL) == GPIO.LOW and GPIO.input(IRTrackingPinR) == GPIO.LOW and GPIO.input(IRTrackingPinLL) == GPIO.LOW and GPIO.input(IRTrackingPinRR) == GPIO.LOW:
            print('IR Tracking Test Code')
            print('------------------------------')
            print('The sensor detects white color line')

        elif GPIO.input(IRTrackingPinL) == GPIO.HIGH and GPIO.input(IRTrackingPinR) == GPIO.HIGH and GPIO.input(IRTrackingPinLL) == GPIO.LOW and GPIO.input(IRTrackingPinRR) == GPIO.LOW:
            print('IR Tracking Test Code')
            print('------------------------------')
            print('The sensor detects black color line')

        elif GPIO.input(IRTrackingPinL) == GPIO.HIGH and GPIO.input(IRTrackingPinR) == GPIO.LOW and GPIO.input(IRTrackingPinLL) == GPIO.HIGH and GPIO.input(IRTrackingPinRR) == GPIO.LOW:
            print('IR Tracking Test Code')
            print('------------------------------')
            print('The sensor detects 90 degree left turn')

        elif GPIO.input(IRTrackingPinL) == GPIO.LOW and GPIO.input(IRTrackingPinR) == GPIO.HIGH and GPIO.input(IRTrackingPinLL) == GPIO.LOW and GPIO.input(IRTrackingPinRR) == GPIO.HIGH:
            print('IR Tracking Test Code')
            print('------------------------------')
            print('The sensor detects 90 degree right turn')

        elif GPIO.input(IRTrackingPinL) == GPIO.HIGH and GPIO.input(IRTrackingPinR) == GPIO.HIGH and GPIO.input(IRTrackingPinLL) == GPIO.HIGH and GPIO.input(IRTrackingPinRR) == GPIO.HIGH:
            print('IR Tracking Test Code')
            print('------------------------------')
            print('The sensor detects an intersection')
            # TODO: run motor for a bit to see if intersection is + or T
        time.sleep(0.2)


def destroy():
    GPIO.cleanup() # Release resource


if __name__ == '__main__': # The Program will start from here
    setup()
try:
    loop()
except KeyboardInterrupt: # When control c is pressed child program destroy() will be executed.
    destroy()