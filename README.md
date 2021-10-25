**Hardware:** 
  - For the reflective optical sensors, we used a 100 Ohm resistor connected to the Digital in pin and a 4100 Ohm resistor connected to the 5V pin. This ratio was chosen to maintain the recommended circuit but to increase the power to the circuit at a safe level that will operate well under our otherwise low power drawing conditions. In total, we used 4 reflective optical sensors for our robot.  They are used as sensors to support our PID controller that detects whether the robot is aligned with the track. 
  - The four sensors are configured in two pairs that are situated tape-width apart - approximately 1 cm (See Appendix G-1 for diagram). This way, if the inner sensors detect black while the outer detect white, the robot is following the line. If both sensors in the right pair detect black while both sensors in the left pair detect white, then the robot is straying left, and vice versa for straying right. 
  - Used in conjunction with a PID controller, we are able to generate a stream of error values based on the robot’s alignment with the track to output adjustment values to the motor, so the robot will turn smoothly and without significant oscillation, having used all three terms of the PID. 
  
**The algorithm for the line tracking functionality:**
  - Proportional Derivative Integral (PID) controller that takes into account the current error value, its derivative and its integral over time according to binary input from the four sensors. Each sensor outputs a bit, with 0 signifying white and 1 signifying black. Therefore, we get a 4-bit input from four sensors with the most significant bit from the leftmost sensor and least significant bit from the rightmost sensor. 
  - Using the input, we calculate an error value that is either positive, negative, or zero which signifies an adjustment to the right, left, or none, respectively. For example, if the input is 4b’0110, then our PID outputs a value of 0, namely no adjustment is required and the robot continues to move forward. 
  - Sensors are sampled at a rate of 3000 Hz, namely approximately every 1/3000 seconds. The sample rate was decided upon after trial and error and fine tuning to allow for sufficient time to see a sharp turn and react to it. 

**The headless Pi use, implementation, and challenges**
  - The headless Pi is used as the main controller for the PID algorithm and the motor speeds. It is attached to a portable battery pack and the Motor Hat and is situated on the 2WD Mobile Platform robot to allow autonomous function and can be controlled via ssh if needed after powering on. 
  - It is at times difficult to control the RPi headless, as it can only be communicated via terminal. In the beginning, it was difficult to get used to coding through the terminal, but this issue was solved by the team’s desire to always learn more and now each member can use the terminal to start the Pi. We also purchased a touchscreen LCD for our demo so this will allow easier use of the Pi going forward. 

**Battery-operated robot implementation and challenges**
  - The main body of our robot is the 2WD Mobile Platform, which consists of 5 AAA batteries and 2 DC motors. The two DC motors connect to pins on the Motor Hat to allow control of voltage supply via the MotorKit (software). The battery source is attached to a power switch on the 2WD Mobile Platform before connecting to the Motor Hat. The motors can independently go forwards and backwards due to the individual H-Bridges existing in the motor hat, removing the need for our team to use relays or another large hardware component that would hinder the robot’s overall speed or else draw more power to move due to the added weight.  
  - The greatest challenge with the robot implementation was during fine tuning of the motor and PID control. Many times, I fine tune our code to working condition and come back the next day to have the robot not following the line properly again. This is due to a number of factors: battery pack drains slowly, ambient lighting and shadows in testing area, different track shape, etc. The general method we used to determine accurate Kd, Kp, and Ki values (in that order) was similar to the Ziegler-Nichols method described here:
    1.	Set all gains to 0.
    2.	Increase Kd until the system oscillates.
    3.	Reduce Kd by a factor of 2-4.
    4.	Set Kp to about 1% of Kd.
    5.	Increase Kp until oscillations start.
    6.	Decrease Kp by a factor of 2-4.
    7.	Set Ki to about 1% of Kp.
    8.	Increase Ki until oscillations start.
    9.	Decrease Ki by a factor of 2-4 and the PID values are approximately set.
    10.	Do some small fine tuning.

●	What the additional functionalities are
  - Android	Mobile app
  - LCD Display
  - Live camera feed
  - twitter bot (The camera is used to take snapshots of the robot’s environment to be posted to Twitter as an update tweet: https://twitter.com/cpen291team11)
  - wall detection
  - Live path graphing on LCD (Since the robot always determines its own direction and speed, we can plot the path it travels, and essentially draw a picture of the tape line that it sees. We assume an initial orientation of moving up in the y direction, and use the last known point to calculate the coordinates of the next point through some trigonometric identities and formulae. This image is shown on the LCD as the robot traverses its path)

Appendix A – Robot pictures
A-1) Front, top, and side view of our robot
 ![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)
 ![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)
 ![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)
A-2) wiring and position of our optical sensors
  ![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)
  ![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)
A-3) wiring and placement of the Motor Hat and Raspberry Pi on the robot
  ![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)
A-4) Back view of our robot with camera and sonar sensor wiring
  ![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)

Appendix B - Other
Fritzing:
  ![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)
 Reflective optical sensor configuration diagram:
  ![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true) 
 Graphical representation of GUI graph algorithm:
  ![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)


