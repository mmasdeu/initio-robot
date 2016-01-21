#!/usr/bin/python
# avoider.py
#======================================================================

import sys
import tty
import termios
import argparse
import logging
import time

parser = argparse.ArgumentParser(
    description='Initio Ultimate Robot'
)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")

args = parser.parse_args()
if args.verbose:
    logging.basicConfig(level = logging.DEBUG)

from logging import debug

def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if ch == '0x03':
        raise KeyboardInterrupt
    return ch

def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return chr(0x10 + ord(c3) - 65)  # 16=Up, 17=Down, 18=Right, 19=Left arrows

# End of single character reading
#======================================================================

import robotclass
accel = 5
speed = 0
with robotclass.RobotResource() as robot:
    while True:
        if robot.irAll():
            robot.reverse(10)
            time.sleep(1)
            robot.stop()
            continue
        key = readkey()
        if key ==' x' or key == '.':
            robot.stop()
        elif key == 'w' or ord(key) == 16:
            speed += accel
        elif key == 'a' or ord(key) == 19:
            speed = 0
            robot.spinLeft(50)
        elif key == 's' or ord(key) == 18:
            speed -= accel
        elif key == 'a' or ord(key) == 17:
            speed = 0
            robot.spinRight(50)
        elif ord(key) == 3:
            break
        if speed >  100:
            speed = 100
        elif speed < -100:
            speed = -100
        if speed > 0:
            robot.forward(speed)
        elif speed < 0:
            robot.reverse(-speed)
