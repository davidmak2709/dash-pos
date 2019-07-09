#!/usr/bin/env python3

import time
#import sys

from dashvend.logger import info  # stdout and file logging
from dashvend.addresses import Bip32Chain  # purchase addresses
from dashvend.dashrpc import DashRPC  # local daemon - balances/refunds
#from dashvend.dash_ix import InstantX  # dash instantx processing
from dashvend.dash_zmq import DashZMQ
#from dashvend.dash_p2p import DashP2P  # dash network monitor
from dashvend.vend import Vend  # main app and hardware interface

from dashvend.config import MAINNET  # dash network to use
from dashvend.config import VENDING_COST  # dash amount required for purchase
from vending.pihatlistener import PiHatListener
from gui.client import Client
from gui.guilistener import GuiListener
import queue
import math
import configparser
import threading
from dashvend.config import DRINK_IDS

def conversion(config, amount):
    config.read('conversion/rates.ini')
    return round(amount / float(config['rates']['dash']), 5)

transaction_done = False
def waiting_screen():
    time.sleep(20)
    if transaction_done:
        pass
    else:
        #privremeno sync 
        c.sendMessage('syncScreen')
    

#main
if __name__ == "__main__":
    config = configparser.ConfigParser()
    
    dashrpc = DashRPC(mainnet=MAINNET)
    dashzmq = DashZMQ(mainnet=MAINNET,dashrpc=dashrpc)

    #dashp2p = DashP2P(mainnet=MAINNET)

    vend = Vend()
    dashzmq.connect()
    dashzmq.set_vend(vend)

    dataQueue = queue.Queue()
    
    #init GUI
    listener = GuiListener(65448, dataQueue)
    listener.start()

    while True:
        try:
            c = Client('127.0.0.1',65449)
            break
        except:
            pass
        print('Connecting...')
        time.sleep(1)
    # End init GUI

    info("connecting to dashd, waiting for masternode and budget sync")
    dashrpc.connect()
    while(not dashrpc.ready()):
        time.sleep(60)

    # Set to idle screen after everything is connected
    # možda preselit niže nakon subscribea
    #c.sendMessage('idleScreen')

    bip32 = Bip32Chain(mainnet=MAINNET, dashrpc=dashrpc)

    #ix = InstantX()
    #vend.set_instantx(ix)  # attach instantx detection
    vend.set_address_chain(bip32)  # attach address chain
    vend.set_dashrpc(dashrpc)  # attach local wallet for refunds


    phl = PiHatListener(dataQueue=dataQueue)

    phl.start()
    phl.onThread(phl.subscribeToVMC)

    while True:
        msg = dataQueue.get()
        print(msg)
        #if not guiQ.empty():

        # Reconnect procedura
        if not dashrpc.ready():
            c.sendMessage('syncScreen')
            dashrpc.connect()
            #dashp2p.connect()
            #dashp2p.forward(vend.get_listeners())
            info("waiting for dashd to finish synchronizing")
            while(not dashrpc.ready()):
                time.sleep(60)
            c.sendMessage('idleScreen')


        if 'error' in msg.keys():
            if msg['error'] == 'cashless':
                phl.cashless_counter += 1
                if phl.cashless_counter == 3:
                    c.sendMessage('syncScreen')
                    phl.onThread(phl.unsubscribeToVMC)
                    time.sleep(10)
                    phl.onThread(phl.subscribeToVMC)
                    phl.cashless_counter = 0
                    

        if 'subscribed' in msg.keys():
            if msg['subscribed'] == True:
                c.sendMessage('idleScreen')
                #vend.set_state(Vend.STARTUP)
                info("*" * 80)
                info(" --> ready. listening to dash %s network." % (MAINNET and 'mainnet' or 'testnet'))
                phl.subscribed = True
            elif msg['subscribed'] == False:
                phl.subscribed = False
                #po meni treba dodati error u queue inac zablokira sve ako dode ovdje

        if 'gui' in msg.keys():
            if phl.subscribed and msg['gui'] == 'startVend':
                phl.onThread(phl.startVending)
                c.sendMessage('selectBeverageScreen')
                msg['gui'] = ''

        if 'id' in msg.keys():
            choice = None
            for k,v in DRINK_IDS.items():
                if v == float(msg['id']):
                    choice = k
            amount = math.floor(float(msg['id']))
            # konverzija u dash
            dash_amount = conversion(config, amount)
            print('ID-> ' + str(msg['id']))
            print('AMOUNT-> ' + str(amount) + ' kn')
            print('CHOICE->' + str(choice))
            ## zapisat dash_amount u dashvend/config po VENDING_COST
            ## ne znam sta znaci ovo phl.amount gdje se kasnije koristi
            ## bolja opcija:
            ## u vendu VENDING_COST zamijeniti sa self.cost a ovdje
            vend.set_product_cost(dash_amount)  # set product cost in dash

            print('ADDRESS-> ' + vend.current_address)
            print('DASH AMOUNT' + str(dash_amount))
            c.sendMessage('paymentScreen-' + vend.current_address + '-' + str(dash_amount))
            #zapocni odbrojavanje do wait screena
            #logika čekanja 20 + 10
            transaction_done = False
            wait = threading.Thread(target=waiting_screen)#, args=(transaction_done,))
            wait.start()

            if dashzmq.listen():
                transaction_done = True
                info("Transaction found")
                phl.onThread(phl.confirmVending)
                c.sendMessage('finalScreen')
                time.sleep(4)
                c.sendMessage('idleScreen')
            else:
                phl.onThread(phl.declineVending)
                c.sendMessage('idleScreen')

        #dashp2p.listen()
        #sleep nije ni potreban jer queue blokira dok ne dobije novu poruku
        #slicno kao BMO za svaku poruku imamo odredeni event
        time.sleep(1)
