#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 12:09:49 2019

@author: toni
"""

import queue
from time import sleep
from client import Client
from guilistener import GuiListener

guiQ = queue.Queue()
listener = GuiListener(65448,guiQ)
listener.start()

while True:
    try:
        c = Client('127.0.0.1',65449)
        break
    except:
        pass
    print('Connecting...')
    sleep(1)

sleep(5)
c.sendMessage('idleScreen')


while True:
    sleep(3)
    c.sendMessage('selectBeverageScreen')
    sleep(3)
    c.sendMessage('paymentScreen-dlt-0.0001')
    sleep(3)
    c.sendMessage('finalScreen')
    sleep(3)
    c.sendMessage('idleScreen')
