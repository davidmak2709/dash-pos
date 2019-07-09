#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 19:07:05 2019

@author: toni
"""

import queue
import threading
import socket

class GuiListener(threading.Thread):
    def __init__(self, port, dataQueue, loop_time = 1.0/60):
        self.functionQueue = queue.Queue()
        self.dataQueue =  dataQueue
        self.timeout = loop_time
        super(GuiListener, self).__init__()
        self.HOST = '127.0.0.1'
        self.PORT = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.HOST, self.PORT))

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
        self.s.listen()
        conn, addr = self.s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                #debug
                print (data)
                self.dataQueue.put({'gui': data.decode('utf-8')})
                #send response
                conn.sendall(data)
                
    def initScreen(self):
        self.dataQueue.put('screen1')
        
    def __del__(self):
        self.s.close()



#someClass = SomeClass(queue)
#someClass.start()
#someClass.onThread(someClass.initScreen)

