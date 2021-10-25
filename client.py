import glob
import time
from bluetooth import *
import math
import re

from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

kit = MotorKit()

MAX_FORWARD = 1
MAX_BACKWARDS = -1

def robot_stop():
    kit.motor1.throttle = 0.0
    kit.motor2.throttle = 0.0

def robot_move(left, right):
    kit.motor2.throttle = left
    kit.motor1.throttle = right

def get_data(data):
    tup = tuple(filter(None, data.split(',')))
    return (int(tup[0]), int(tup[1]))

def get_speeds(x, y):

    cX = 290
    cY = 590
    radius = 220
    radX = x - cX
    radY = cY - y
    left_speed = 0
    right_speed = 0

    if (x != 0 and y != 0):
        angle = math.degrees(math.atan2(radY, radX))
        if angle < 0:
            angle += 360

        if angle <= 90:
            left_speed = MAX_FORWARD
            right_speed = (angle % 91) / 90 * MAX_FORWARD
        elif angle <= 180:
            right_speed = MAX_FORWARD
            left_speed = ((180 - angle) % 91) / 90 * MAX_FORWARD
        elif angle <= 270:
            right_speed = MAX_BACKWARDS
            left_speed = ((angle - 180) % 91) / 90 * MAX_BACKWARDS
        else:
            left_speed = MAX_BACKWARDS
            right_speed = ((360 - angle) % 91) / 90 * MAX_BACKWARDS
    else:
        return (0, 0)

    displacement = math.sqrt(radX * radX + radY * radY)

    left = left_speed * displacement / radius
    right = right_speed * displacement / radius

    if left > MAX_FORWARD:
        left = MAX_FORWARD
    if right > MAX_FORWARD:
        right = MAX_FORWARD
    if left < MAX_BACKWARDS:
        left = MAX_BACKWARDS
    if right < MAX_BACKWARDS:
        right = MAX_BACKWARDS

    return (left, right)

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( server_sock, "LineTrackerServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ],
                   )
while True:
    print("Waiting for connection on RFCOMM channel ", port)

    client_sock, client_info = server_sock.accept()
    print ("Accepted connection from ", client_info)

    while True:
        try:
            data = client_sock.recv(1024)

            if len(data) == 0:
                print("no data")
                break

            direction = data.decode(encoding='UTF-8')

            if direction == 'Demo':
                import main
            elif (re.search('[a-zA-Z]', direction)):
                robot_stop()
            else:
                motor_vals = get_data(direction)
                speeds = get_speeds(motor_vals[0], motor_vals[1])
                left_speed = speeds[0]
                right_speed = speeds[1]
                robot_move(left_speed, right_speed)

        except IOError:
            print("IOError")
            continue

        except KeyboardInterrupt:
            print("disconnected")
            client_sock.close()
            server_sock.close()
            break
