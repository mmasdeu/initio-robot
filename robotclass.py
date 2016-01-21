#!/usr/bin/python
# robotclass.py
#
# Based on the
# Python Module to externalise all Initio/PiRoCon specific hardware
#
# The original module was created by Gareth Davies, this is a class
# which encapsulates the previous functionality.
#
#======================================================================

# Import all necessary libraries
import RPi.GPIO as GPIO, threading, time, os, subprocess

from logging import debug

class RobotResource():
    def __enter__(self):
        class Robot():
            def __init__(self):
                # Pins 24, 26 Right Motor
                # Pins 19, 21 Left Motor
                self._R1 = 24
                self._R2 = 26
                self._L1 = 19
                self._L2 = 21

                # Define obstacle sensors and line sensors
                self._irFL = 7
                self._irFR = 11
                self._lineRight = 13
                self._lineLeft = 12

                # Define Sonar Pin (same pin for both Ping and Echo)
                # Note that this can be either 8 or 23 on PiRoCon
                self._sonar = 8

                self._servosActive = False

                debug("Initio version: %s"%self.version())

                # Initialise the PWM device using the default address

                #use physical pin numbering
                GPIO.setmode(GPIO.BOARD)
                #print GPIO.RPI_REVISION

                #set up digital line detectors as inputs
                GPIO.setup(self._lineRight, GPIO.IN) # Right line sensor
                GPIO.setup(self._lineLeft, GPIO.IN) # Left line sensor

                #Set up IR obstacle sensors as inputs
                GPIO.setup(self._irFL, GPIO.IN) # Left obstacle sensor
                GPIO.setup(self._irFR, GPIO.IN) # Right obstacle sensor

                #use pwm on inputs so motors don't go too fast
                GPIO.setup(self._L1, GPIO.OUT)
                self._p = GPIO.PWM(self._L1, 20)
                self._p.start(0)

                GPIO.setup(self._L2, GPIO.OUT)
                self._q = GPIO.PWM(self._L2, 20)
                self._q.start(0)

                GPIO.setup(self._R1, GPIO.OUT)
                self._a = GPIO.PWM(self._R1, 20)
                self._a.start(0)

                GPIO.setup(self._R2, GPIO.OUT)
                self._b = GPIO.PWM(self._R2, 20)
                self._b.start(0)

                self.startServos()

                # Define pins for Pan/Tilt
                self.pan = 0
                self.tilt = 1
                self.tVal = 0 # 0 degrees is centre
                self.pVal = 0 # 0 degrees is centre

            def version(self):
                return 1

            # SERVOS
            def doServos(self, pVal = None, tVal = None):
                if pVal is None:
                    pVal = self.pVal
                if tVal is None:
                    tVal = self.tVal
                self.setServo(self.pan, pVal)
                self.setServo(self.tilt, tVal)
                self.tVal = tVal
                self.pVal = pVal

            # MOTORS
            #======================================================================
            # Motor Functions
            #
            # stop(): Stops both motors
            def stop(self):
                self._p.ChangeDutyCycle(0)
                self._q.ChangeDutyCycle(0)
                self._a.ChangeDutyCycle(0)
                self._b.ChangeDutyCycle(0)

            # forward(speed): Sets both motors to move forward at speed. 0 <= speed <= 100
            def forward(self, speed):
                self._p.ChangeDutyCycle(speed)
                self._q.ChangeDutyCycle(0)
                self._a.ChangeDutyCycle(speed)
                self._b.ChangeDutyCycle(0)
                self._p.ChangeFrequency(speed + 5)
                self._a.ChangeFrequency(speed + 5)

            # reverse(speed): Sets both motors to reverse at speed. 0 <= speed <= 100
            def reverse(self, speed):
                self._p.ChangeDutyCycle(0)
                self._q.ChangeDutyCycle(speed)
                self._a.ChangeDutyCycle(0)
                self._b.ChangeDutyCycle(speed)
                self._q.ChangeFrequency(speed + 5)
                self._b.ChangeFrequency(speed + 5)

            # spinLeft(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
            def spinLeft(self, speed):
                self._p.ChangeDutyCycle(0)
                self._q.ChangeDutyCycle(speed)
                self._a.ChangeDutyCycle(speed)
                self._b.ChangeDutyCycle(0)
                self._q.ChangeFrequency(speed + 5)
                self._a.ChangeFrequency(speed + 5)

            # spinRight(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
            def spinRight(self, speed):
                self._p.ChangeDutyCycle(speed)
                self._q.ChangeDutyCycle(0)
                self._a.ChangeDutyCycle(0)
                self._b.ChangeDutyCycle(speed)
                self._p.ChangeFrequency(speed + 5)
                self._b.ChangeFrequency(speed + 5)

            # turnForward(leftSpeed, rightSpeed): Moves forwards in an arc by setting different speeds. 0 <= leftSpeed,rightSpeed <= 100
            def turnForward(self, leftSpeed, rightSpeed):
                self._p.ChangeDutyCycle(leftSpeed)
                self._q.ChangeDutyCycle(0)
                self._a.ChangeDutyCycle(rightSpeed)
                self._b.ChangeDutyCycle(0)
                self._p.ChangeFrequency(leftSpeed + 5)
                self._a.ChangeFrequency(rightSpeed + 5)

            # turnReverse(leftSpeed, rightSpeed): Moves backwards in an arc by setting different speeds. 0 <= leftSpeed,rightSpeed <= 100
            def turnReverse(self, leftSpeed, rightSpeed):
                self._p.ChangeDutyCycle(0)
                self._q.ChangeDutyCycle(leftSpeed)
                self._a.ChangeDutyCycle(0)
                self._b.ChangeDutyCycle(rightSpeed)
                self._q.ChangeFrequency(leftSpeed + 5)
                self._b.ChangeFrequency(rightSpeed + 5)

            # End of Motor Functions
            #======================================================================

            #======================================================================
            # IR Sensor Functions
            #
            # irLeft(): Returns state of Left IR Obstacle sensor
            def irLeft(self):
                return GPIO.input(self._irFL)==0

            # irRight(): Returns state of Right IR Obstacle sensor
            def irRight(self):
                return GPIO.input(self._irFR)==0

            # irAll(): Returns true if any of the Obstacle sensors are triggered
            def irAll(self):
                return (GPIO.input(self._irFL)==0 or GPIO.input(self._irFR)==0)

            # irLeftLine(): Returns state of Left IR Line sensor
            def irLeftLine(self):
                return GPIO.input(self._lineLeft)==0

            # irRightLine(): Returns state of Right IR Line sensor
            def irRightLine(self):
                return GPIO.input(self._lineRight)==0

            # End of IR Sensor Functions
            #======================================================================


            #======================================================================
            # UltraSonic Functions
            #
            # getDistance(). Returns the distance in cm to the nearest reflecting object. 0 == no object
            def getDistance():
                GPIO.setup(self._sonar, GPIO.OUT)
                # Send 10us pulse to trigger
                GPIO.output(self._sonar, True)
                time.sleep(0.00001)
                GPIO.output(self._sonar, False)
                start = time.time()
                count = time.time()
                GPIO.setup(self._sonar,GPIO.IN)
                while GPIO.input(self._sonar)==0 and time.time()-count<0.1:
                    start = time.time()
                count=time.time()
                stop=count
                while GPIO.input(self._sonar)==1 and time.time()-count<0.1:
                    stop = time.time()
                # Calculate pulse length
                elapsed = stop-start
                # Distance pulse travelled in that time is time
                # multiplied by the speed of sound (cm/s)
                distance = elapsed * 34000
                # That was the distance there and back so halve the value
                distance = distance / 2
                return distance

            # End of UltraSonic Functions
            #======================================================================

            #======================================================================
            # Servo Functions
            # Pirocon/microcon use ServoD to control servos

            def setServo(self, Servo, Degrees):
                debug("ServosActive: %s"%self._servosActive)
                debug("Setting servo")
                if not self._servosActive:
                    self.startServos()
                self.pinServod(Servo, Degrees) # for now, simply pass on the input values
            def stopServos(self):
                debug("Stopping servo")
                self.stopServod()

            def startServos(self):
                debug("Starting servod")
                self.startServod()

            def startServod(self):
                debug("Starting servod. ServosActive: %s"%self._servosActive)
                SCRIPTPATH = os.path.split(os.path.realpath(__file__))[0]
                os.system("sudo pkill -f servod")
                initString = SCRIPTPATH +'/servod --pcm --idle-timeout=20000 --p1pins="18,22"'
                os.system(initString)
                debug(initString)
                self._servosActive = True

            def pinServod(self, pin, degrees):
                debug("%s, %s"%(pin, degrees))
                pinString = "echo " + str(pin) + "=" + str(50+ ((90 - degrees) * 200 / 180)) + " > /dev/servoblaster"
                debug(pinString)
                os.system(pinString)

            def stopServod(self):
                os.system("sudo pkill -f servod")
                self._servosActive = False


            # CLEANUP
            def cleanup(self):
                self.stop()
                self.stopServos()
                GPIO.cleanup()

        self.robot_obj = Robot()
        return self.robot_obj

    def __exit__(self, exc_type, exc_value, traceback):
        self.robot_obj.cleanup()
