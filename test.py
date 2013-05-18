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

import socket

class Main:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', 0xf713))
        self.peer_addr = None
        self.last_peer_time = None

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

        print "ready"

    def input_loop(self):
        while True:
            data, self.peer_addr = self.socket.recvfrom(4096)
            self.last_peer_time = time.time()

            try:
                input = json.loads(data)
            except ValueError:
                input = {}


            okay = False

            if 'point' in input:
                okay = True
                point = input['point']
                try:
                    self.crazyflie.commander.send_setpoint(
                        point['roll'],
                        point['pitch'],
                        point['yaw'],
                        point['thrust']
                    )
                except:
                    self.send_data({'debug': 'error processing point data'})

            if not okay:
                self.send_data({'debug': 'no recognised commands'})

        self.crazyflie.commander.send_setpoint(0, 0, 0, 0)
        time.sleep(0.1)
        self.crazyflie.close_link()

    def send_data(self, data):
        if self.last_peer_time and (time.time() - self.last_peer_time) < 3.0:
            data = json.dumps(data, separators=(',',':'))
            self.socket.sendto(data + "\n", self.peer_addr)

    def stabilizerData(self, data):
        payload = {
            'stabilizer': {
                'pitch': data["stabilizer.pitch"],
                'roll': data["stabilizer.roll"],
                'yaw': data["stabilizer.yaw"],
                'thrust': data["stabilizer.thrust"]
            }
        }
        self.send_data(payload)

    def batteryData(self, data):
        payload = {
            'pm': {
                'vbat': data['pm.vbat']
            }
        }
        self.send_data(payload)

Main()
