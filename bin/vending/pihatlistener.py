#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import queue
import time
import serial
import select
import sys
from priorityentry.priorityentry import PriorityEntry

class PiHatListener(threading.Thread):
    subscribed = False
    cashless_counter = 0

    def __init__(self, dataQueue, loop_time = 1.0/60):
        self.functionQueue = queue.Queue()
        self.dataQueue =  dataQueue
        self.timeout = loop_time
        self.ser = serial.Serial('/dev/ttyAMA0', 115200, timeout = 1)

        super(PiHatListener, self).__init__()


    def onThread(self, function, *args, **kwargs):
        self.functionQueue.put((function, args, kwargs))

    def run(self):
        while True:
            try:
                function, args, kwargs = self.functionQueue.get(timeout=self.timeout)
                function(*args, **kwargs)
            except queue.Empty:
                self.idle()


    def idle(self):
        while True:
            line = self.ser.readlines()
            if len(line) > 0:
                self.read(line)
            break

    def subscribeToVMC(self):
        self.ser.write(b'C,SETCONF,mdb-addr=0x10\n')
        # currency codes (0x1---):
        # US Dollar - 840
        # EURO - 978
        # Swiss Franc - 756
        # Croatian Kuna - 191
        self.ser.write(b'C,SETCONF,mdb-currency-code=0x1191\n')
        self.ser.write(b'C,1\n')

    def unsubscribeToVMC(self):
        self.ser.write(b'C,0\n')

    def startVending(self, amount = 10.0):
        self.ser.write(str.encode('C,START,'+ str(amount) +'\n'))


    def confirmVending(self, amount = 0.5):
        self.ser.write(str.encode('C,VEND,'+ str(amount) +'\n'))

    def declineVending(self):
        self.ser.write(str.encode('C,VEND,0\n'))

    def read(self, line):
        for command in line:
            print (command)
            if b'ENABLED' in command:
                self.dataQueue.put(PriorityEntry(1, {'subscribed': True}))
            elif b'DISABLED' in command:
                self.dataQueue.put(PriorityEntry(1, {'subscribed': False}))
            elif b'VEND' in command:
                ids = command.decode('utf-8').strip().split(',')[3]
                self.dataQueue.put(PriorityEntry(1, {'id': ids }))
            elif b'cashless is on' in command:
                self.dataQueue.put(PriorityEntry(1, {'error': 'cashless'}))
