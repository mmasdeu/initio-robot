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
damn = curses.initscr()
damn.nodelay(1) # doesn't keep waiting for a key press
damn.keypad(1) # i.e. arrow keys
curses.noecho() # stop keys echoing
key = 0
damn.addstr(0, 0, "q to quit - only the up and down arrow keys do anything")
with robotclass.RobotResource() as robot:
    while key != ord('q'):
        key = damn.getch()
        if robot.irAll():
            robot.reverse(100)
            time.sleep(0.3)
            robot.stop()
            speed = 0
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
            robot.spinLeft(50)
        if key == ord('d') or key == curses.KEY_RIGHT: # Right
            robot.spinRight(50)
        if speed >  100:
            speed = 100
        elif speed < -100:
            speed = -100
        robot.move(speed)
curses.endwin()
