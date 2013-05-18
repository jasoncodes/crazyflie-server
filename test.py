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

import json

class Main:
    def __init__(self):
        self.crazyflie = Crazyflie()
        cflib.crtp.init_drivers()

        self.crazyflie.open_link("radio://0/10/250K")

        self.crazyflie.connectSetupFinished.add_callback(self.connectSetupFinished)

    def connectSetupFinished(self, linkURI):
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

    def input_loop(self):
        self.quit = False
        while not self.quit:
            try:
                input = json.loads(raw_input())
            except ValueError:
                print json.dumps({'debug': 'invalid JSON received'})
                input = {}
            except EOFError:
                self.quit = True
                break

            try:
                point = input['point']
                self.crazyflie.commander.send_setpoint(
                    point['roll'],
                    point['pitch'],
                    point['yaw'],
                    point['thrust']
                )
            except:
                print json.dumps({'debug': 'error processing point data'})

        self.crazyflie.commander.send_setpoint(0, 0, 0, 0)
        time.sleep(0.1)
        self.crazyflie.close_link()

    def stabilizerData(self, data):
        payload = {
            'stabilizer': {
                'pitch': data["stabilizer.pitch"],
                'roll': data["stabilizer.roll"],
                'yaw': data["stabilizer.yaw"],
                'thrust': data["stabilizer.thrust"]
            }
        }
        print json.dumps(payload)

    def batteryData(self, data):
        payload = {
            'pm': {
                'vbat': data['pm.vbat']
            }
        }
        print json.dumps(payload)

Main()
