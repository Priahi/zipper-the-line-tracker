#Sample 2---------stepper motor
import time
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

kit = MotorKit()

#motor1 = right
#motor2 = left
'''
for i in range (10):
    kit.stepper1.onestep()
    time.sleep(0.1)
    kit.stepper2.onestep()
    time.sleep(0.1)
kit.stepper1.release()
kit.stepper2.release()
'''
'''
kit.motor1.throttle = 1.0
kit.motor2.throttle = 1.0
time.sleep(0.5)
kit.motor1.throttle = 0
kit.motor2.throttle = 0
'''
#right
kit.motor1.throttle = -0.3
kit.motor2.throttle = 0.6
time.sleep(0.5)
kit.motor1.throttle = 0
kit.motor2.throttle = 0

#backwards
kit.motor1.throttle = -1.0
kit.motor2.throttle = -1.0
time.sleep(0.5)
kit.motor1.throttle = 0
kit.motor2.throttle = 0

#left
kit.motor2.throttle = -0.3
kit.motor1.throttle = 0.6
time.sleep(0.5)
kit.motor1.throttle = 0
kit.motor2.throttle = 0
