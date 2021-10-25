import RPi.GPIO as GPIO
import time

#-----------------------------------------------------------------#
# LCD Plot code

from tkinter import *
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
import time

class Plotter:
    def __init__(self, frame):
        self.fig = Figure(figsize=(5,4))
        self.figCanvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.p = self.fig.add_subplot(1,1,1)

    # method for setting the labels of the current plot
    def set_labels(self, title=None, xlabel=None, ylabel=None):
        self.p.set_title(title)
        self.p.set_xlabel(xlabel)
        self.p.set_ylabel(ylabel)

    # method for showing the plot at a specific location on the grid
    def show_plot(self, xloc=0, yloc=0, padx=0, pady=0):
        self.figCanvas.get_tk_widget().grid(row=xloc,column=yloc,padx=padx,pady=pady)

    # method for making the plot disappear off of the current window
    def hide_plot(self):
        self.figCanvas.get_tk_widget().grid_remove()

    # method for clearing the plot and displaying the specified data
    def graph(self, xdata, ydata, color, title, xtitle, ytitle):
        self.p.clear()
        self.set_labels(title, xtitle, ytitle)
        self.p.plot(xdata, ydata, color)
        self.figCanvas.draw()
        plt.xticks(rotation=45, ha='right')
        plt.autoscale(enable=True, axis='both', tight=None)

# robotGUI class to display the graph
class RobotGUI:
    def __init__(self):

        # declare Tkinter window and variables to calculate the path travelled
        self.root = Tk()

        # make fullscreen
        self.root.overrideredirect(True)
        self.root.geometry("{0}x{1}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))

        self.turnVal = 0
        self.speed = 1

        self.x = 0
        self.y = 0
        self.yDir = 1
        self.xDir = 0
        self.hyp = 0
        self.theta1 = math.pi / 2
        self.phi1 = 0
        self.theta2 = 0
        self.phi2 = math.pi - self.theta2

        self.xVals = []
        self.yVals = []

        self.flag = 1

        self.plotLength = 300

        self.running = False

        self.message = StringVar()
        self.message.set("Welcome to PathPlotter!")

        button = Button(self.root, text="Quit", command=self.stop_program)
        button.grid(row=0, column=0)

        self.plot = Plotter(self.root)
        self.plot.show_plot(1,0)
        self.begin_measure()

        self.root.mainloop()

    def begin_measure(self):
        for i in range(0, self.plotLength):
        
            self.running = True

            # getting the turnvals from the track array 
            self.turnVal = track[round(i/self.plotLength * len(track))]
            self.speed = 0.4

            # calculating angles and direction of travel
            self.hyp = math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2) + self.speed
                                - 2 * math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2))
                                * math.cos(math.pi * (1 - self.turnVal / 2)))
            if self.x != 0:
                self.theta1 = math.atan(self.y / self.x)
            else:
                self.theta1 = math.pi / 2
            self.theta2 = self.turnVal * math.pi / 2
            self.phi2 = math.pi - self.theta2
            self.phi1 = math.asin(math.sin(self.phi2) / self.hyp)
            self.y = self.hyp * math.sin(self.phi1 + self.theta1)
            self.x = self.hyp * math.cos(self.phi1 + self.theta1)

            self.x = round(self.x, 2)
            self.y = round(self.y, 2)

            self.xVals.append(self.x)
            self.yVals.append(self.y)

            self.plot.graph(self.xVals, self.yVals, 'b', "Path Travelled So Far", "x", "y")

            # self.loop = self.root.after(1, lambda: self.begin_measure())

    # method for terminating the program
    def stop_program(self):
        # try:
            # if self.running:
                # self.root.after_cancel(self.loop)
        self.root.destroy()
        self.root.quit()
        # except:
            # print("Program terminated")

    # method for running the current program
    def run_program(self):
        self.message.set("Program running...")
        if not self.running:
            self.begin_measure()

#-----------------------------------------------------------------#
# PID controller code


class pid:
    """PID controller."""

    def init(self, Kp, Ki, Kd):
        
        # set origin time as the current time
        origin_time = time.time()

        # Gains for each term
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        # Corrections calculated in update (outputs)
        self.Cp = 0.0
        self.Ci = 0.0
        self.Cd = 0.0

        self.previous_time = origin_time
        self.previous_error = 0.0
        
    def Update(self, error):          

        # dt is change in time (time interval between calls to update)
        # if dt is negative, return 0  
        current_time = time.time()
        dt = current_time - self.previous_time
        if dt <= 0.0:
            return 0
        
        # de is change in error (from previous)
        de = error - self.previous_error

        self.Cp = error
        self.Ci += error * dt
        self.Cd = de / dt

        self.previous_time = current_time
        self.previous_error = error

        return (
            (self.Kp * self.Cp)    # proportional term
            + (self.Ki * self.Ci)  # integral term
            + (self.Kd * self.Cd)  # derivative term
        )


#-----------------------------------------------------------------#
# Sensors code

# setup the sensors according to their ports
GPIO.setwarnings(False)
rightIRTrackingPinL = 12
rightIRTrackingPinR = 16
leftIRTrackingPinL = 20
leftIRTrackingPinR = 21

# setup left and right pins array to store the left and right sensor ports
leftPins = [leftIRTrackingPinL, leftIRTrackingPinR]
rightPins = [rightIRTrackingPinL, rightIRTrackingPinR]

# define optical sensor setup function that calls GPIO.setup to setup the 
# sensors as input
GPIO.setmode(GPIO.BCM) # Set the GPIO pins as BCM
GPIO.setup(leftIRTrackingPinL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(leftIRTrackingPinR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(rightIRTrackingPinL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(rightIRTrackingPinR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# define get optical value function that retuns the values read from the 
# optical sensor in binary format
def getOptiValues(pins):
    value = 0
    for pin in pins:
        value = value << 1
        value = value | GPIO.input(pin)
    return value

# define a cleanup destroy function that calls GPIO.cleanup
def destroy():
    GPIO.cleanup() # Release resource

# call the setup functions to setup the optical sensor
# setupOptiSensor()

#-----------------------------------------------------------------#
# Sonar code

# setting the ports for ultrasonic sensor
TRIG = 26
ECHO = 19

def setupSonar():
    # setting the input and output
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

def getSonar():
    GPIO.output(TRIG, False)
    time.sleep(0.1)
    # time between the pulse 10uS
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    # starting the pulse
    pulse_start = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    # ending the pulse
    pulse_end = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    # calculatGPIOn of distance
    sound_speed = 331.5 + (0.6*21)
    pulse_duratGPIOn = pulse_end - pulse_start
    distance = pulse_duratGPIOn * sound_speed * 50
    distance = round(distance, 2)
    return distance

#-----------------------------------------------------------------#
# Twitter code
from twython import Twython

# define the keys and tokens for twitter
consumer_key = 'IbZYLMhINCxuxRLd4OyrM2Ph2'
consumer_secret = 'pBfsBvgDYBTjcXuYNgJXl5DhwXNEosZStpjCu4az7SgTvgyMcx'
access_token = '1220402110610604032-0Eca0tLBOjE2TKd1fPbh6BfZzMZ4u2'
access_token_secret = 'GH4fuU3riSkWVh0UGODAasDCI2gN8Qqpc7AkGlQnwzHQZ'

# initialize a twitter object by calling Twython initializer
twitter = Twython(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

# define a postTweet function that posts different tweets to @cpen291team11
def postTweet(distance, speed, state, imageFile):
    if state == "end":
        message = "I have finished running the track!"
        if distance <= 10:
            message += "There is an object " + str(distance) + " cm away and we are approaching at " \
                       + str(speed) + " m/s. Brace for evasive maneuvers!!"
        elif distance >= 100:
            message += "There are no obstacles in sight! The closest barrier is " \
                       + str(distance) + "cm away and we are approaching at " + str(speed) + " m/s."
        image = open(imageFile, 'rb')
        response = twitter.upload_media(media=image)
        media_id = [response['media_id']]
        twitter.update_status(status=message, media_ids=media_id)
        print("Tweeted: " + message)


#-----------------------------------------------------------------#
# Camera code
from picamera import PiCamera

# initialize a PiCamera object by calling PiCamera
camera = PiCamera()

# define a takePhoto function that takes a picture and stores it to a
# certain directory
def takePhoto():
    pic = '/home/pi/Desktop/image1.jpg'
    camera.capture('/home/pi/Desktop/image%s.jpg' % 1)
    return pic

# setup the Sonar sensors
setupSonar()

# if the sonar reading is less than 10 cm, take a picture and tweet it
if getSonar() <= 10:
    postTweet(getSonar(), 3, "end", takePhoto())
#-----------------------------------------------------------------#
# Motors code

from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

# define a MotorKit object to control the motors
kit = MotorKit()

track = []

# robot_stop function that stops the motors (throttle = 0)
def robot_stop():
    kit.motor1.throttle = 0.0
    kit.motor2.throttle = 0.0


global count
count = 0
global entry
entry = 0

# robot_move function that change the motors to the input throttle
# for delay amoung of time (in seconds) 
def robot_move(left, right, delay):
    kit.motor2.throttle = left
    kit.motor1.throttle = right

    global entry
    global count
    entry += (right-left)/2
    count += 1

    if count > 100: 
        track.append(entry/count)

    time.sleep(delay)

# robot_run function that simply sets the left and right motors to 
# the input speeds indefinitely 
def robot_run(left, right):
    kit.motor2.throttle = left
    kit.motor1.throttle = right

# a factor variable that controls how much faster the robot moves when
# going straight than turning
factor = 1.1

# define the robot_ir function that moves with the optical sensor 
# and PID controller output
# adjuster is a value from 1 to -1
def robot_ir(speed, adjuster, times, flag, blockade):

    # we set additional varible left and right that is equal to speed to 
    # control the left and right motors
    left = speed
    right= speed
    
    # flag is the variable that controls 
    if flag == 1 and blockade == 0:

        # according to the adjuster value, the robot either turns or goes forward
        # if adjuster is 0, the robot goes forward 
        if adjuster == 0:
            robot_move(left*factor, right*factor, times)

        # if adjuster is positive, the robot turns right by throttling the right
        # motor with speed - adjuster
        elif adjuster > 0:
            robot_move(left, right-adjuster, times)

        # if adjuster is positive, the robot turns left by throttling the left
        # motor with speed - adjuster  
        elif adjuster < 0:
            robot_move(left+adjuster,right, times) 
    
    # else if flag is 0 and blockade is 0 stop the robot
    elif flag == 0 and blockade == 0:
        robot_stop()

    # else if blockade is 1, move the robot back
    elif blockade == 1:
        robot_stop()
        time.sleep(1)
        robot_move(-left, -right, time)
        time.sleep(1)
        robot_stop()

#-----------------------------------------------------------------#
# Line tracking code

import math

# dictionaries for the error value according to the optical sensor readings
dictLeftErrors = {0b00: 0.7, 0b01: 0, 0b11: -0.7,  0b10: -2}
dictRightErrors = {0b00: -0.7, 0b10: 0, 0b11: 0.7, 0b01: 2}

# gap count variable that keeps track of how many consecutive all-white detections
# the optical sensors have 
global gap_count
gap_count = 0

# define getError functions that obtain error value is the dictionary
# declared above and combines the left and right optical sensors
def getErrorRight():
    dataR = getOptiValues(rightPins)
    print(dataR)
    error = dictRightErrors[dataR]
    return error, dataR

def getErrorLeft():
    dataL = getOptiValues(leftPins)
    print(dataL)
    error = dictLeftErrors[dataL]
    return error, dataL

def getErrorOverall():
    errorL, dataL = getErrorLeft()
    errorR, dataR = getErrorRight()
    
    # increments the gap_count variable if the readings of all optical sensors
    # are 0
    global gap_count
    if (dataL is 0b00 and dataR is 0b00):
        gap_count += 1
    
    # otherwise clear the gap_count variable (set to 0)
    else:
        gap_count = 0
    return errorL + errorR

# flag indicates whether we want the robot to move or not
flag = 1

# calls a robot_stop at the beginning of every program start
robot_stop()

# gap variable for how long the robot can move when it doesn't detect anything
# we obtained this value through calibration and calculation (~3cm gap)
gap = 100

# define a demo function that runs the robot autonomously to track line
def demo():
    
    # loops indefinitely for autonomous line tracking
    while True:
        try:
            # set sampling rate and speed
            sampling_rate = 2000
            speed = 0.4
            
            # call pid to update and get the output values that the robot is suppose to turn
            pid.init(pid, Kp=0.1, Ki=0, Kd=7)

            # output is between 1 and -1 and the robot turns right if output is positive and
            # left if its negative, goes forward if 0
            output = pid.Update(pid, getErrorOverall())
            
            # if gap_count is bigger than the 3cm, stops the robot and tweets and graphs path travelled
            if (gap_count >= 100/factor):
                robot_stop()
                postTweet(getSonar(), 3, "end", takePhoto())
                rg = RobotGUI()
                break

            # uncomment this to print the output
            print(output)

            # calls robot_ir
            robot_ir(speed, 2*math.atan(output)/math.pi*speed, 1/sampling_rate, flag, 0)

        # catches a keyboardInterrupt and stops the robot, tweets and graphs path travelled
        except KeyboardInterrupt:
            robot_stop()
            postTweet(getSonar(), 3, "end", takePhoto())
            rg = RobotGUI()
            return

        # catches IO error and continues to run
        except IOError:
            print("IO error")
    destroy()

#-----------------------------------------------------------------#
# Bluetooth handling code

import glob
from bluetooth import *
import re

# Maximum speeds for the motorhat motors
MAX_FORWARD = 1
MAX_BACKWARDS = -1

# converts input string in the format "x,y" into a tuple of integers to use for
# motor speed calculation
def get_data(data):
    tup = tuple(filter(None, data.split(',')))
    return (int(tup[0]), int(tup[1]))

# gets the speed of the left and right motors based on x and y coordinates of
# joystick on app
def get_speeds(x, y):
    # centre coordinates of the joystick in the app
    cX = 290
    cY = 590

    #radius of joystick outer circle
    radius = 220

    # calculting current displacement of joystick from centre
    radX = x - cX
    radY = cY - y

    left_speed = 0
    right_speed = 0

    if (x != 0 and y != 0):
        # angle calculated using simple cartesian coordinates
        angle = math.degrees(math.atan2(radY, radX))

        # for angles > 180 degrees, atan calculates the negative angle, so it is
        # readjusted to compensate
        if angle < 0:
            angle += 360

        # right and left motor speeds are adjusted based on the current quadrant
        # the joystick is in
        # when the joystick is aligned towards the right of the joystick area,
        # the left motor is set to maximum speed and the right motor speed is
        # increased to cause robot to turn right
        # the same applies for left turns
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

    # displacement calculated based on joystick distance from centre
    displacement = math.sqrt(radX * radX + radY * radY)

    # speeds are adjusted relative to the displacement, ie. further from the
    # centre causes faster speeds
    left = left_speed * displacement / radius
    right = right_speed * displacement / radius

    # if the input goes out of bounds and causes the speed to go outside of the
    # indicated range, it is capped at max speed
    if left > MAX_FORWARD:
        left = MAX_FORWARD
    if right > MAX_FORWARD:
        right = MAX_FORWARD
    if left < MAX_BACKWARDS:
        left = MAX_BACKWARDS
    if right < MAX_BACKWARDS:
        right = MAX_BACKWARDS

    return (left, right)

# creating a new bluetooth server socket using rfcomm bluetooth protocols
server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

# setting a uuid that both client and user can use to connect to the service
# this uuid is a standard one that is used for rpi bluetooth communication
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

# advertising the service to allow for client connections
advertise_service( server_sock, "LineTrackerServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ],
                   )
while True:
    print("Waiting for connection on RFCOMM channel ", port)

    # blocking call that waits for a client to connect to the server before
    # proceeding
    client_sock, client_info = server_sock.accept()
    print ("Accepted connection from ", client_info)

    while True:
        try:
            # receieves data from the client
            data = client_sock.recv(1024)

            if len(data) == 0:
                print("no data")
                break

            # data from client will be in string format so it is first decoded
            direction = data.decode(encoding='UTF-8')

            # checks which type of data the client has sent and acts accordingly
            if direction == 'Demo':
                demo()
            elif (re.search('[a-zA-Z]', direction)):
                robot_stop()
            else:
                motor_vals = get_data(direction)
                speeds = get_speeds(motor_vals[0], motor_vals[1])
                left_speed = speeds[0]
                right_speed = speeds[1]
                robot_run(left_speed, right_speed)

        except IOError:
            print("IOError")
            continue

        # on a KeyboardInterrupt, the connection is cancelled and the socket is
        # closed
        except KeyboardInterrupt:
            print("disconnected")
            client_sock.close()
            server_sock.close()
            break
