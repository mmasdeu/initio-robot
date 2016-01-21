#!/usr/bin/python
# myrobot.py
#======================================================================

import sys
import tty
import termios
import argparse
import logging

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
with robotclass.RobotResource() as robot:
    while True:
        key = readkey()
        if key == ' ':
            robot.doServos(0, 0)
        elif key.upper() == 'L':
            robot.doServos(-90, -90)
        elif key.upper() == 'R':
            robot.doServos(90, 90)
        elif key ==' x' or key == '.':
            robot.stopServos()
        elif key == 'w' or ord(key) == 16:
            robot.doServos(pVal = min(90, robot.pVal+10))
        elif key == 'a' or ord(key) == 19:
            robot.doServos(tVal = max (-90, robot.tVal-10))
        elif key == 's' or ord(key) == 18:
            robot.doServos(tVal = min(90, robot.tVal+10))
        elif key == 'z' or ord(key) == 17:
            robot.doServos(pVal = max(-90, robot.pVal-10))
        elif key == 'g':
            robot.startServos()
        elif ord(key) == 3:
            break
