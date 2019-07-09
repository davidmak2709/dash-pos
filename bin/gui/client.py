#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket

class Client():
    def __init__(self, HOST, PORT):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))

    def sendMessage(self,msg): 
        self.s.sendall(msg.encode('utf-8'))
        response = self.s.recv(1024)
        print('Received', repr(response))

