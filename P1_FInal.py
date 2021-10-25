'''Extra Components to be used'''
#LCD-Images, Animations etc.
#Buzzer-Songs
#RGB-Easier human interface

'''Functions'''
#move(direction, time, ir_check)
#ir_check(time)
#camera(pic, vid, live)
#sonar_check()
#LCD_display
#RGB(color)
#Song()
#PID_controller

'''Motor Functions'''
#(1==full speed fwd, -1==full speed bwd)
#motor1 = right
#motor2 = left
import time
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

kit = MotorKit()

def robot_stop():
    kit.motor1.throttle = 0.0
    time.sleep(0.1)
    kit.motor2.throttle = 0.0

def robot_move(motor1, motor2, delay):
    kit.motor1.throttle = motor1
    kit.motor2.throttle = motor2
    time.sleep(delay)
    robot_stop()

def robot_dir(direction, time):
    if direction == "forward":
         robot_move(1.0, 1.0, time)
    elif direction == "backward":
         robot_move(-1.0, -1.0, time)
    elif direction == "left":
         robot_move(0.5, -0.5, time)
    elif direction == "right":
         robot_move(-0.5, 0.5, time)

def robot_ir(old_motor1, old_motor_2, adjuster, time, flag):
    if flag == 1:
        if adjuster==0:
            robot_move(old_motor1, old_motor_2, time)
        elif adjuster>0:
            robot_move(-adjuster, old_motor_2, time)
        elif adjuster<0:
            robot_move(old_motor1, -adjuster, time)
    else:
        robot_stop()
