#!/usr/bin/env python2

import sys
sys.path.append('lib')

import logging
logging.basicConfig()

import time
from threading import Thread

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cfclient.utils.logconfigreader import LogVariable, LogConfig

import termios
old_settings = termios.tcgetattr(sys.stdin)

import tty
tty.setcbreak(sys.stdin)

def cleanup():
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

import atexit
atexit.register(cleanup)

class Main:
    quit = False
    roll = 0
    pitch = 0
    yawrate = 0
    thrust = 0

    def __init__(self):
        self.crazyflie = Crazyflie()
        cflib.crtp.init_drivers()

        interfaces = cflib.crtp.scan_interfaces()
        print interfaces
        for interface in interfaces:
            print "Found %s" % (interface[0])

        self.crazyflie.open_link("radio://0/10/250K")

        self.crazyflie.connectSetupFinished.add_callback(self.connectSetupFinished)

    def connectSetupFinished(self, linkURI):
        pulse_thread = Thread(target=self.pulse_loop)
        pulse_thread.start()

        input_thread = Thread(target=self.input_loop)
        input_thread.start()

        lg = LogConfig ("Battery", 1000)
        lg.addVariable(LogVariable("pm.vbat", "float"))
        log = self.crazyflie.log.create_log_packet(lg)
        if (log != None):
            log.dataReceived.add_callback(self.batteryData)
            log.start()
        else:
            print "battery not found in log TOC"

        stabilizerconf = LogConfig("Stabilizer", 1000)
        stabilizerconf.addVariable(LogVariable("stabilizer.thrust", "uint16_t"))
        stabilizerconf.addVariable(LogVariable("stabilizer.yaw", "float"))
        stabilizerconf.addVariable(LogVariable("stabilizer.roll", "float"))
        stabilizerconf.addVariable(LogVariable("stabilizer.pitch", "float"))
        stabilizerlog = self.crazyflie.log.create_log_packet(stabilizerconf)

        if (stabilizerlog != None):
            stabilizerlog.dataReceived.add_callback(self.stabilizerData)
            stabilizerlog.start()
        else:
            print "stabilizer not found in log TOC"

    def is_number(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def input_loop(self):
        while True:
            str = sys.stdin.read(1)

            if str == 'z':
                self.quit = True
                break

            if str == 'q':
                if self.thrust <= 10000:
                    self.thrust = 10001
                else:
                    self.thrust += 1000
            elif str == 'a':
                self.thrust -= 1000
            elif str == 'w':
                if self.thrust <= 10000:
                    self.thrust = 20000
                else:
                    self.thrust += 5000
            elif str == 's':
                self.thrust -= 5000
            elif str == 'x':
                self.pitch = 0
                self.roll = 0
                if self.thrust > 35000:
                    self.thrust = 35000
                    time.sleep(3)
                self.thrust = 0
            elif str == 'i': # forward
                self.pitch += 1
            elif str == 'k': # back
                self.pitch -= 1
            elif str == 'j': # left
                self.roll -= 1
            elif str == 'l': # right
                self.roll += 1
            else:
                if self.is_number(str):
                    self.thrust = 10000 + int(50000 * int(str) / 9.0)

            print "thrust = %d, pitch = %5.02f, roll = %5.02f" % (self.thrust, self.pitch, self.roll)

    def pulse_loop(self):
        while not self.quit:
            self.crazyflie.commander.send_setpoint(self.roll, self.pitch, self.yawrate, self.thrust)
            time.sleep(0.1)

        self.crazyflie.commander.send_setpoint(0, 0, 0, 0)
        time.sleep(0.1)
        self.crazyflie.close_link()

    def stabilizerData(self, data):
        print "pitch=%.2f, roll=%.2f, yaw=%.2f, thrust=%d" % (data["stabilizer.pitch"], data["stabilizer.roll"], data["stabilizer.yaw"], data["stabilizer.thrust"])

    def batteryData(self, data):
        print "battery=%.2f" % (data['pm.vbat'])

Main()
