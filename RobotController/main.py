import RPi.GPIO as GPIO
import time

#-----------------------------------------------------------------#
# LCD code

import digitalio
import board
from PIL import Image, ImageDraw
import adafruit_rgb_display.st7735 as st7735        
 
# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
 
# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000
 
# Setup SPI bus using hardware SPI:
spi = board.SPI()

disp = st7735.ST7735R(spi, rotation=270, height=128, x_offset=2, y_offset=3,
                       cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE)
# pylint: enable=line-too-long
 
# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width   # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width   # we swap height/width to rotate it to landscape!
    height = disp.height
image = Image.new('RGB', (width, height))
 
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
 
# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)
 
def displayImage():
    image = Image.open("image1.jpg")
    
    # Scale the image to the smaller screen dimension
    image_ratio = image.width / image.height
    screen_ratio = width / height
    if screen_ratio < image_ratio:
        scaled_width = image.width * height // image.height
        scaled_height = height
    else:
        scaled_width = width
        scaled_height = image.height * width // image.width
    image = image.resize((scaled_width, scaled_height), Image.BICUBIC)
    
    # Crop and center the image
    x = scaled_width // 2 - width // 2
    y = scaled_height // 2 - height // 2
    image = image.crop((x, y, x + width, y + height))
    
    # Display image.
    disp.image(image)

#-----------------------------------------------------------------#
# PID controller code

# declare PID class that stores previous time and previous error
class PID:

    def init(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.Ci = 0

        self.previous_time = time.time()
        self.previous_error = 0

    def update(self, error):
        de = error - self.previous_error
        dt = time.time() - self.previous_time
        self.Ci += error * dt

        if dt <= 0.0:
            return 0

        output = self.Kp * error + self.Kd * de/dt + self.Ki * self.Ci

        return output

#-----------------------------------------------------------------#
# Sensors code

# declare the sensor pins
GPIO.setwarnings(False)

rightIRTrackingPinL = 12
rightIRTrackingPinR = 16

leftIRTrackingPinL = 20
leftIRTrackingPinR = 21

leftPins = [leftIRTrackingPinL, leftIRTrackingPinR]
rightPins = [rightIRTrackingPinL, rightIRTrackingPinR]

# define function to set up the optical sensors
def setupOptiSensor():
    GPIO.setmode(GPIO.BCM) # Set the GPIO pins as BCM
    GPIO.setup(leftIRTrackingPinL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(leftIRTrackingPinR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(rightIRTrackingPinL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(rightIRTrackingPinR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# define function to get optical values
def getOptiValues(pins):
    value = 0
    for pin in pins:
        value = value << 1
        value = value | GPIO.input(pin)
    return value

def destroy():
    GPIO.cleanup() # Release resource

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




#-----------------------------------------------------------------#
# Twitter code
from twython import Twython

consumer_key = 'IbZYLMhINCxuxRLd4OyrM2Ph2'
consumer_secret = 'pBfsBvgDYBTjcXuYNgJXl5DhwXNEosZStpjCu4az7SgTvgyMcx'
access_token = '1220402110610604032-0Eca0tLBOjE2TKd1fPbh6BfZzMZ4u2'
access_token_secret = 'GH4fuU3riSkWVh0UGODAasDCI2gN8Qqpc7AkGlQnwzHQZ'

twitter = Twython(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

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
        twitter.update_status(status=message, media_id=media_id)
        print("Tweeted: " + message)

#-----------------------------------------------------------------#

#-----------------------------------------------------------------#
# Camera code
from picamera import PiCamera

camera = PiCamera()

def takePhoto():
    camera.capture('./image%s.jpg' % 1)
    return '/home/pi/Desktop/image%s.jpg' % 1

#-----------------------------------------------------------------#
# #-----------------------------------------------------------------#
# Motors code


#-----------------------------------------------------------------#

from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

kit = MotorKit()

def robot_stop():
    kit.motor1.throttle = 0.0
    kit.motor2.throttle = 0.0

def robot_move(left, right, delay):
    kit.motor2.throttle = left
    kit.motor1.throttle = right
    time.sleep(delay)
    #robot_stop()

factor = 1.1

def robot_ir(speed, adjuster, times, flag, blockade):
    left = speed
    right= speed
    if flag == 1 and blockade == 0:
        if adjuster == 0:
            robot_move(left*factor, right*factor, times)
        elif adjuster > 0:
            robot_move(left, right-adjuster, times)  # try = 0 case
            #time.sleep(0.001)
        elif adjuster < 0:
            robot_move(left+adjuster,right, times)  # try = 0 case
            #time.sleep(0.001)
    elif flag == 0 and blockade == 0:
        robot_stop()
    elif blockade == 1:
        robot_stop()
        time.sleep(1)
        robot_move(-left, -right, time)
        time.sleep(1)



#-----------------------------------------------------------------#
# Line tracking code

import math
#import GUI

setupOptiSensor()
setupSonar()

error = 0
dictRightTurns = {0b00: "a bit left", 0b01: "straight", 0b10: "too left", 0b11: "a bit right"}
dictLeftErrors = {0b00: 0.5, 0b01: 0, 0b11: -0.5,  0b10: -1}
dictLeftTurns = {0b00: "a bit right", 0b10: "straight", 0b01: "too right", 0b11: "a bit left"}
dictRightErrors = {0b00: -0.5, 0b10: 0, 0b11: 0.5, 0b01: 1}

# dictErrors = {0b0110: 0, 0b1100: -0.7, 0b1110: -1, 0b1111: 0, 0b0111: 1, 0b0011: 0.7, 0b0000: 2}

# def getError():
#     data = getOptiValues(pins)
#     print(data)
#     error =
global gap_count
gap_count = 0

def getErrorRight():
    dataR = getOptiValues(rightPins)
    error = dictRightErrors[dataR]
    return error, dataR

def getErrorLeft():
    dataL = getOptiValues(leftPins)
    error = dictLeftErrors[dataL]
    return error, dataL

global left90
global right90
left90 = 0
right90 = 0
sampling_rate = 50000
speed = 0.3

def getErrorOverall():
    errorL, dataL = getErrorLeft()
    errorR, dataR = getErrorRight()
    global gap_count
    global left90
    global right90
    if (dataL is 0b00 and dataR is 0b00):
        gap_count += 1
        if (left90 is 1):
            turn("left")
        elif (right90 is 1):
            turn("right")
    else:
        gap_count = 0

    if (dataL is 0b11 and dataR is 0b10):
        left90 = 1
        right90 = 0
    elif (dataL is 0b01 and dataR is 0b11):
        left90 = 0
        right90 = 1
    else:
        left90 = 0
        right90 = 0

    return errorL + errorR

def turn(direction):
    while True:
        errorL, dataL = getErrorLeft()
        errorR, dataR = getErrorRight()
        if (dataL is not 0b00 or dataR is not 0b00):
            break
        if (direction is "left"):
            robot_move(0, speed, 1/sampling_rate)
        elif (direction is "right"):
            robot_move(speed, 0, 1/sampling_rate)
        else:
            break

flag = 1
takePhoto()
time.sleep(2)
displayImage()

# GUI.TrackPlot.init(TrackPlot)
# good values: sampling_rate = 50000
#              speed = 0.6
#              Kp = 1, Ki = 0, Kd = 0.01
while True:
    try:
        PID.init(PID, Kp=1, Ki=0, Kd=0.01)
        output = PID.update(PID, getErrorOverall())
        if (gap_count >= 200/factor):
            robot_stop()
            break
        robot_ir(speed, 2*math.atan(output)/math.pi*speed, 1/sampling_rate, flag, 0)
    except KeyboardInterrupt:
        robot_stop()
        break
    except:
        print("IO error")
destroy()
