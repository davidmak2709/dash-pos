#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 17:34:07 2019

@author: toni
"""

import queue
import PIL.Image, PIL.ImageTk
import tkinter as tk
from guilistener import GuiListener
from screeninfo import get_monitors
from time import sleep
from client import Client
import pyqrcode
# '127.0.0.1',65449 input
# '127.0.0.1',65448 output

DASHCOLOR = "#1C75B8"

class GuiVend():
    def __init__(self, master, queue, startVend):
        self.master = master
        self.queue = queue
        self.startVend = startVend
        # Set up the GUI
        self.master.title('Vend')
        # ukljuciti u produkciji
        self.master.wm_attributes('-type', 'splash')
        self.master.attributes("-fullscreen", True)
        self.master.geometry("{0}x{1}+0+0".format(self.master.winfo_screenwidth(), 
                                 self.master.winfo_screenheight()))
        # self.master.geometry('400x400')
        self.master.config(background="white")
        self.master.overrideredirect(True)
        self.master.focus_set()

        
        
        """ Redosljed pozivanja"""
        self.syncScreen()
        #self.idleScreen()
        
        #self.selectBeverageScreen()
        
        #self.paymentScreen("XqHt831rFj5tr4PVjqEcJmh6VKvHP62QiM", 0.1)
        
        #self.finalScreen()

    def processIncoming(self):
        """
        Procesiranje poruka iz reda
        """
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do what it says
                # TODO porcesiranje svih poruka
                if 'gui' in msg.keys():
                    message = msg['gui'].split('-')
                    print (message)
                    
                    if(message[0] == 'syncScreen'):
                        self.syncScreen()                
                    elif (message[0] == 'idleScreen'):
                        self.idleScreen()
                    elif (message[0] == 'selectBeverageScreen'):
                        self.selectBeverageScreen()                    
                    elif (message[0] == 'paymentScreen'):
                        self.paymentScreen(message[1], float(message[2]))                   
                    elif (message[0] == 'finalScreen'):
                        self.finalScreen()
                 
                
            except queue.Empty:
                pass
    
    def syncScreen(self):
        self.clear()
        #canvas = tk.Canvas(self.master, width=480, height=800, background="white")
        topLabel = tk.Label(self.master, text = "Loading ...".upper(),
                          font =('Verdana', 32, 'bold','italic'),
                          foreground= DASHCOLOR,
                              anchor="center")
        topLabel.config(background="white")
        topLabel.pack(expand= True)
        #canvas.pack()
        return
 
    
    def idleScreen(self):
        self.clear()
        #canvas = tk.Canvas(self.master, width=480, height=800, background="white")
        topLabel = tk.Label(self.master, text = "BUY WITH:",
                          font =('Verdana', 32, 'bold','italic'),
                          foreground= DASHCOLOR,
                              anchor="center")
        topLabel.config(background="white")
        topLabel.pack(padx = 30., pady = 50)
        
        width = 300
        height = 100
        img = PIL.Image.open("images/logo.png")
        img = img.resize((width,height), PIL.Image.ANTIALIAS)
        photoImg =  PIL.ImageTk.PhotoImage(img)
        dashButton = tk.Button(self.master,image=photoImg, command=self.startVend, 
                        width=420, height=200, highlightbackground=DASHCOLOR,
                        activebackground="#e9edf5", highlightcolor=DASHCOLOR, 
                        highlightthickness=3, bd=0)
        
        dashButton.config(background= "white")
        dashButton.image = photoImg
        dashButton.pack(padx = 30., pady = 50)
        
        
        # sve ispod ne treba ako nećemo imati žetonjeru
        """
        midLabel = tk.Label(self.master, text = "OR",
                          font =('Verdana', 32, 'bold','italic'),
                          foreground= DASHCOLOR,
                              anchor="center")
        midLabel.config(background="white")
        midLabel.pack()
     
        
        width = 200
        height = 90
        img = PIL.Image.open("cash.png")
        img = img.resize((width,height), PIL.Image.ANTIALIAS)
        photoImg =  PIL.ImageTk.PhotoImage(img)
        cashButton = tk.Button(self.master, text= "Cash",image=photoImg, command=self.startVend, 
                        width=420, height=200)
        cashButton.config(background= "white")
        cashButton.image = photoImg
        cashButton.pack()
        ##
        """
        #canvas.pack()
        return
    
    def selectBeverageScreen(self):
         self.clear()
         #canvas = tk.Canvas(self.master, width=480, height=800, background="white")
         message = "select your\n favourite\n beverage"
         label = tk.Label(self.master, text = message.upper(),
                          font =('Verdana', 32, 'bold','italic'),
                          foreground= DASHCOLOR,
                              anchor="center")
         label.config(background="white")
         label.pack(expand = 1)
         #canvas.pack()
         return
   
    def paymentScreen(self, address, amount): 
        self.clear()
       # canvas = tk.Canvas(self.master, width=480, height=800, background="white")
        topLabel = tk.Label(self.master, text = "SEND\n" + str(amount) +" DASH = X HRK",
                          font =('Verdana', 32, 'bold','italic'),
                          foreground= DASHCOLOR,
                              anchor="center")
        topLabel.config(background="white")
        topLabel.pack(padx = 20, pady = 20)


        code = pyqrcode.create('dash:'+address+'?amount='+str(amount)+'&label=DLT&IS=1')
        codeXBM = code.xbm(scale=8) 
        codeBMP = tk.BitmapImage(data=codeXBM)
        codeBMP.config(background="white")
        
        qrCode = tk.Label(self.master,image=codeBMP, relief="flat")
        qrCode.image = codeBMP
        qrCode.pack(padx = 20, pady = 20)

        addressLabel = tk.Label(self.master, text = address,
                          font =('Verdana', 16, 'bold','italic'),
                          foreground= DASHCOLOR,
                              anchor="center")
        addressLabel.config(background="white")
        addressLabel.pack(padx = 20, pady = 20)
        #canvas.pack()
        return
    
    def finalScreen(self):
        self.clear()
        #canvas = tk.Canvas(self.master, width=480, height=800, background="white")
        topLabel = tk.Label(self.master, text = "THANK YOU!",
                          font =('Verdana', 32, 'bold','italic'),
                          foreground= DASHCOLOR,
                              anchor="center")
        topLabel.config(background="white")
        topLabel.pack(expand= True)
        #canvas.pack()
    
        return
    
    def clear(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        #self.grid_forget()
        return


class ThreadedGUI:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI. We spawn a new thread for the worker.
        """
        self.master = master

        # Waiting for connection to dash thread
        self.c = self.connect()

        # Create the queue
        self.queue = queue.Queue()

        # Set up the GUI part
        self.gui = GuiVend(master, self.queue, self.startVend)

        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.running = 1
        #conecct to listening
        self.connection = GuiListener(port = 65449, dataQueue = self.queue)
        self.connection.start()
        #nije ni potrebno ako se stavi scree1 u konstruktor GUIVend
        #self.connection.onThread(self.connection.initScreen)
        
        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            # TODO
            import sys
            sys.exit(1)
        self.master.after(100, self.periodicCall)

    def startVend(self):
        print("starting vending process")
        self.c.sendMessage('startVend')

    def connect(self):
        while True:
            try:
                c = Client('127.0.0.1',65448)
                return c
            except:
                pass
            print('Connecting...')
            sleep(1)

client = ThreadedGUI(tk.Tk())
client.master.mainloop()
