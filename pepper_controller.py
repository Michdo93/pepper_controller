#!/usr/bin/python
import os
import sys
import threading
import pynput
from pynput import keyboard
import time
import qi
import argparse

class PepperController(object):
    def __init__(self, session, robot_ip, port):
        self.session = session
        self.robot_ip = robot_ip
        self.port = port

        self.motion_service = self.session.service("ALMotion")

        self.w = False
        self.a = False
        self.s = False
        self.d = False
        self.q = False
        self.e = False

        self.speed = 0.0
        self.steer = 0.0
        self.message = ""

        print("w/s: accelerate")
        print("a/d: steer")
        print("q:   stops the engine")
        print("e:   neutral the servo")
        print("CTRL+C:   exit program")

        self.thread = threading.Thread(target=self.check_speedAndSteer, args=())
        self.thread.start()

        # Collect events until released
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release,suppress=True) as listener:
            listener.join()

    def printscreen(self):
        # The call os.system('clear') clears the screen.
        os.system('clear')
        print("w/s: forward / backward acceleration")
        print("a/d: left / right steering")
        print("q:   stop the motors")
        print("e:   neutral the motors")
        print("Quit the program: Press at first ESC to stop and then CTRL+C")
        print("========== Speed display ==========")
        print("Motor speed:  ", self.speed)

        self.message = "speed: %s and steer: %s" % (self.speed, self.steer)
        print(self.message)

    def on_press(self, pressKey):
        if pressKey.char == ('w'):
            self.w = True
            self.speed = self.speed + 0.1

            if self.speed > 1:
                self.speed = 1

            self.printscreen()
        if pressKey.char == ('a'):
            self.a = True
            self.steer = self.steer - 0.05

            if self.steer < -1:
                self.steer = -1

            self.printscreen()
        if pressKey.char == ('s'):
            self.s = True
            self.speed = self.speed - 0.1

            if self.speed < -1:
                self.speed = -1

            self.printscreen()
        if pressKey.char == ('d'):
            self.d = True
            self.steer = self.steer + 0.05

            if self.steer > 1:
                self.steer = 1

            self.printscreen()

        if pressKey.char == ('q'):
            self.q = True
            self.speed = 0
            self.printscreen()

        if pressKey.char == ('e'):
            self.e = True
            self.steer = 0
            self.printscreen()

    def on_release(self, releaseKey):
        self.w = False
        self.a = False
        self.s = False
        self.d = False
        self.q = False
        self.e = False

        if releaseKey == keyboard.Key.esc:
            self.motion_service.killMove()
            self.motion_service.killAll()
            return False

    def check_speedAndSteer(self):
        while ((self.w == False or self.s == False) or (self.a == False or self.d == False)) and not rospy.is_shutdown():
            if(self.speed >= 0.1):
                self.speed = self.speed - 0.1
                self.motion_service.move(self.speed, 0, 0)
                if(self.speed <= 0.1):
                    self.speed = 0.0
                    self.motion_service.stopMove()

            if(self.speed <= -0.1):
                self.speed = self.speed + 0.1
                self.motion_service.move(self.speed, 0, 0)
                if(self.speed >= -0.1):
                    self.speed = 0.0
                    self.motion_service.stopMove()

            if(self.steer >= 0.05):
                self.steer = self.steer - 0.05
                self.motion_service.move(0, 0, self.steer)
                if(self.steer <= 0.05):
                    self.steer = 0.0
                    self.motion_service.stopMove()

            if(self.steer <= -0.05):
                self.steer = self.steer + 0.05
                self.motion_service.move(0, 0, self.steer)
                if(self.steer >= -0.05):
                    self.steer = 0.0
                    self.motion_service.stopMove()

            self.printscreen()
            time.sleep(1)

            self.message = "speed: %s and steer: %s" % (self.speed, self.steer)
            print(self.message)

# Main function.
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    pepper = PepperController(session, args.ip, args.port)
