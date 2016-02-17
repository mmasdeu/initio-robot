#!/usr/bin/python
# avoider.py
#======================================================================

import sys
import tty
import termios
import argparse
import logging
import time
import curses

parser = argparse.ArgumentParser(
    description='Initio Ultimate Robot'
)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")

args = parser.parse_args()
if args.verbose:
    logging.basicConfig(level = logging.DEBUG)

from logging import debug

# End of single character reading
#======================================================================

import robotclass
accel = 20
speed = 0
damn = curses.initscr()
damn.nodelay(1) # doesn't keep waiting for a key press
damn.keypad(1) # i.e. arrow keys
curses.noecho() # stop keys echoing

key = 0
damn.addstr(0, 0, "q to quit")
with robotclass.RobotResource() as robot:
    while key != ord('q'):
        key = int(damn.getch())
        curses.flushinp()
        if key != -1:
            damn.addstr(0, 0, "\n %s"%str(key))
        while robot.irAll():
            speed = 0
            robot.reverse(50)
            time.sleep(float(0.2))
            robot.stop()
            continue
        if key == ord('x') or key == ord('.'):
            robot.stop()
        if key == ord('w') or key == curses.KEY_UP: # Advance
            speed += accel
        elif key == ord('s') or key == curses.KEY_DOWN: # Reverse
            speed -= accel
        else:
            if speed > 0:
                speed -= accel
                if speed < 0:
                    speed = 0
            elif speed < 0:
                speed += accel
                if speed > 0:
                    speed = 0
        if key == ord('a') or key == curses.KEY_LEFT: # Left
            robot.spinLeft(80)
            time.sleep(float(.5))
        if key == ord('d') or key == curses.KEY_RIGHT: # Right
            robot.spinRight(80)
            time.sleep(float(.5))
        if speed >  100:
            speed = 100
        elif speed < -100:
            speed = -100
        if key == ord('q'):
            break
        key = -1
        damn.addstr(0, 0, "speed = %s"%speed)
        if speed != 0:
            robot.move(speed)
            time.sleep(0.1)
    curses.endwin()
