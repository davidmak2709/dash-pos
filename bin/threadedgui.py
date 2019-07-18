#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import queue
import PIL.Image, PIL.ImageTk
import tkinter as tk
from gui.guilistener import GuiListener
from gui.client import Client
from screeninfo import get_monitors
from time import sleep
import pyqrcode
from dashvend.config import DASHVEND_DIR

# '127.0.0.1',65449 input
# '127.0.0.1',65448 output

DASHCOLOR = "#1C75B8"
BGCOLOR = "#f5f6f7"
BGCOLOR_WHITE = "#ffffff"
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
        self.master.config(cursor = 'none')
	# ukljuciti za debug
        # self.master.geometry('400x400')
        self.master.config(background="white")
        self.master.overrideredirect(True)
        self.master.focus_set()
        
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.master.grid_rowconfigure(1, weight=2)
        self.master.grid_columnconfigure(1, weight=2)

        self.master.grid_rowconfigure(2, weight=1)
        self.master.grid_columnconfigure(2, weight=1)

        self.waitingTimeVar = tk.StringVar()
        self.waitingTimerId = None
        
        
        self.paymentTimeVar = tk.StringVar()
        self.paymentTimerId = None
        
        """ Poziv prvog screen-a """
        self.syncScreen()

    def processIncoming(self):
        """
        Procesiranje poruka iz reda
        """
        while self.queue.qsize():
            try:
                msg = self.queue.get(0).data
                # Check contents of message and do what it says
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
                    elif (message[0] == 'waitingScreen'):
                        self.waitingScreen()

            except queue.Empty:
                pass
    
    def syncScreen(self):
        self.clear()
        topLabel = tk.Label(self.master, text = "Loading ...".upper(),
                          font =('Verdana', 32, 'bold','italic'),
                          foreground= DASHCOLOR,
                              anchor="center")
        topLabel.config(background=BGCOLOR_WHITE)
        topLabel.pack(expand= True)
        return
 
    
    def idleScreen(self):
       self.clear()
       topMessage = "PRESS HERE \nTO BUY WITH:"
       topLabel = tk.Label(self.master, text = topMessage,
                    font =('Verdana', 28, 'bold','italic'),
                    foreground= DASHCOLOR,
                    anchor="center")
       topLabel.config(background=BGCOLOR_WHITE)
       topLabel.grid(row= 0,column= 0, columnspan= 3, padx= 30, pady= 50)
        
       buttonWidth = 300
       buttonHeight = 100
       img = PIL.Image.open(DASHVEND_DIR + "/bin/gui/images/logo.png")
       img = img.resize((buttonWidth, buttonHeight), PIL.Image.ANTIALIAS)
       photoDashLogo =  PIL.ImageTk.PhotoImage(img)
       
       dashButton = tk.Button(self.master,image=photoDashLogo, command=self.startVend,
                       width=420, height=200, highlightbackground=DASHCOLOR,
                       activebackground="#e9edf5", highlightcolor=DASHCOLOR, 
                       highlightthickness=3, bd=0, relief= "raised")
        
       dashButton.config(background= BGCOLOR_WHITE)
       dashButton.image = photoDashLogo
       dashButton.grid(row= 1, column= 0, columnspan= 3, padx= 30, pady= 50)
       
       self.defaultFooter().grid(row= 2, column= 0, columnspan= 3, sticky="nsew")
       return
    
    def selectBeverageScreen(self):
         self.clear()
         message = "select your\n favourite\n beverage"
         label = tk.Label(self.master, text = message.upper(),
                          font =('Verdana', 32, 'bold','italic'),
                          foreground= DASHCOLOR,
                              anchor="center")
         label.config(background=BGCOLOR_WHITE)
         label.grid(row=0, column=0, rowspan=1, columnspan=3, padx= 30, pady= 50)
         
         arrowWidth = 300
         arrowHeight = 150
         img = PIL.Image.open(DASHVEND_DIR + "/bin/gui/images/left_arrow.png")
         img = img.resize((arrowWidth, arrowHeight), PIL.Image.ANTIALIAS)
         photoAutoLogo =  PIL.ImageTk.PhotoImage(img)
        
         arrowLabel = tk.Label(self.master, image = photoAutoLogo)
         arrowLabel.image = photoAutoLogo
         arrowLabel.config(background= BGCOLOR_WHITE)
         arrowLabel.grid(row= 1, column= 0, padx= 30, pady= 0)
         
         self.defaultFooter().grid(row= 2, column= 0, columnspan= 3, sticky="nsew")
         return
   
    def paymentScreen(self, address, amount): 
        self.clear() 
        topLabel = tk.Label(self.master, text = "SEND\n" + str(amount) +" DASH",
                          font =('Verdana', 30, 'bold','italic'),
                          foreground= DASHCOLOR,
                              anchor="center")
        topLabel.config(background=BGCOLOR_WHITE)
        topLabel.grid(row= 0, column= 0, columnspan= 3)


        code = pyqrcode.create('dash:'+address+'?amount='+str(amount)+'&label=DLT&IS=1')
        codeXBM = code.xbm(scale=8) 
        codeBMP = tk.BitmapImage(data=codeXBM)
        codeBMP.config(background=BGCOLOR_WHITE)
        
        qrCode = tk.Label(self.master,image=codeBMP, relief="flat")
        qrCode.image = codeBMP
        qrCode.grid(row= 1, column= 0, columnspan= 3)

        instructionLabel = tk.Label(self.master, text = "Scan QR code for\n payment".upper(),
                          font =('Verdana', 22, 'bold','italic'),
                          foreground= DASHCOLOR,
                          anchor="center")
        instructionLabel.config(background=BGCOLOR_WHITE)
        instructionLabel.grid(row= 2, column= 0, columnspan= 3)
        
        
        waitingTime = 45
        self.paymentTimeVar.set(waitingTime)
        self.master.after(1000, self.paymentScreenTimer, waitingTime-1)
        timer = tk.Label(self.master, textvariable = self.paymentTimeVar,
                          font =('Verdana', 30, 'bold','italic'),
                          foreground= "red",
                              anchor="center")
        timer.config(background=BGCOLOR_WHITE)
        
        timer.grid(row=3, column=0, rowspan=1, columnspan=3, padx= 30, pady= 10)
        
        
        return
    
    def paymentScreenTimer(self,count):
        if count == 0:
            self.master.after_cancel(self.paymentTimerId)
            return
        
        self.paymentTimeVar.set(count)
        self.paymentTimerId = self.master.after(1000, self.paymentScreenTimer,count-1)
        


    def waitingScreen(self):
        self.clear()
        waitingTime = 15
        self.waitingTimeVar.set(waitingTime)
        self.master.after(1000, self.waitingScreenTimer, waitingTime-1)
        timer = tk.Label(self.master, textvariable = self.waitingTimeVar,
                          font =('Verdana', 30, 'bold','italic'),
                          foreground= "red",
                              anchor="center")
        timer.config(background=BGCOLOR_WHITE)
        
        timer.grid(row=0, column=2, rowspan=1, columnspan=1, padx= 30, pady= 10)
        
        topLabel = tk.Label(self.master, text = "WAITING FOR \nFUNDS...",
                          font =('Verdana', 26, 'bold','italic'),
                          foreground= DASHCOLOR,
                              anchor="center")
        topLabel.config(background=BGCOLOR_WHITE)
        topLabel.grid(row=1, column=0, rowspan=1, columnspan=3, padx= 30, pady= 25)
    
        self.defaultFooter().grid(row= 2, column= 0, columnspan= 3, sticky="nsew")
        return

    def waitingScreenTimer(self,count):
        if count == -1:
            self.master.after_cancel(self.waitingTimerId)
            return
        
        self.waitingTimeVar.set(count)
        self.waitingTimerId = self.master.after(1000, self.waitingScreenTimer,count-1)

        
    
    def finalScreen(self):
        self.clear()
        topLabel = tk.Label(self.master, text = "THANK YOU!",
                          font =('Verdana', 32, 'bold','italic'),
                              foreground= DASHCOLOR,anchor="center")

        topLabel.config(background=BGCOLOR_WHITE)
        topLabel.grid(row=0, column=0, rowspan=2, columnspan=3, padx= 30, pady= 50)
    
        self.defaultFooter().grid(row= 2, column= 0, columnspan= 3, sticky="nsew")
        return

    def defaultFooter(self):        
        frame = tk.Frame(self.master)
        frame.config(background= BGCOLOR)
        frame.grid_rowconfigure(0, weight=1)
        for i in range(3):
            frame.grid_columnconfigure(i, weight=1)
        
        logoWidth = 80
        logoHeight = 80
       
        img = PIL.Image.open(DASHVEND_DIR + "/bin/gui/images/auto_logo.png")
        img = img.resize((logoWidth + 20, logoHeight), PIL.Image.ANTIALIAS)
        photoAutoLogo =  PIL.ImageTk.PhotoImage(img)
       
        autoLabel = tk.Label(frame, image = photoAutoLogo)
        autoLabel.image = photoAutoLogo
        autoLabel.config(background= BGCOLOR)
        autoLabel.grid(row= 0, column= 0, padx= 30, pady= 0)
       
        img = PIL.Image.open(DASHVEND_DIR + "/bin/gui/images/riteh_logo.gif")
        img = img.resize((100, 100), PIL.Image.ANTIALIAS)
        photoRitehLogo =  PIL.ImageTk.PhotoImage(img)
       
        ritehLabel = tk.Label(frame, image = photoRitehLogo)
        ritehLabel.image = photoRitehLogo
        ritehLabel.config(background= BGCOLOR)
        ritehLabel.grid(row= 0, column= 1, padx= 30, pady= 0)
       
        img = PIL.Image.open(DASHVEND_DIR + "/bin/gui/images/qibixx_logo.png")
        img = img.resize((logoWidth, logoHeight), PIL.Image.ANTIALIAS)
        photoQibixxLogo =  PIL.ImageTk.PhotoImage(img)
        
        qibixxLabel = tk.Label(frame, image = photoQibixxLogo)
        qibixxLabel.image = photoQibixxLogo
        qibixxLabel.config(background= BGCOLOR)
        qibixxLabel.grid(row= 0, column= 2, padx= 30, pady= 0)
        
        return frame
    
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

        # Create the queue
        self.queue = queue.Queue()

        # Set up the GUI part
        self.gui = GuiVend(master, self.queue, self.startVend)

        # Waiting for connection to dash thread
        self.c = self.connect()

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

if __name__ == "__main__":
    client = ThreadedGUI(tk.Tk())
    client.master.mainloop()
