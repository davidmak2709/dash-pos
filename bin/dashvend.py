#!/usr/bin/env python3

import time
import queue
import math
import configparser
import threading
import requests
import json

from dashvend.logger import info # stdout and file logging
from dashvend.addresses import RPCAddress  # purchase addresses
from dashvend.dashrpc import DashRPC  # local daemon - balances/refunds
from dashvend.dashzmq import DashZMQ # dash network monitor
from dashvend.vend import Vend  # main app and hardware interface
from dashvend.config import MAINNET  # dash network to use
from dashvend.config import DRINK_IDS # dict {name : id}
from dashvend.config import DASHVEND_DIR
from dashvend.config import MACHINE_ID
from dashvend.config import MACHINE_API_KEY
from dashvend.config import MACHINE_API_URL
from vending.pihatlistener import PiHatListener
from gui.client import Client
from gui.guilistener import GuiListener
from bitcoinrpc.authproxy import JSONRPCException

start_time = 0

def conversion(config, amount):
    config.read(DASHVEND_DIR + '/bin/conversion/rates.ini')
    return round(amount / float(config['rates']['dash']), 5)

def post_api(choice, amount, dash_amount):
    payload = {
        "product": choice,
        "amount": amount,
        "dash_amount": dash_amount,
        "machine": MACHINE_ID
    }
    headers = {"Authorization": MACHINE_API_KEY,
               "Content-Type":"application/json"}
    try:
        r = requests.post(MACHINE_API_URL, data=json.dumps(payload), headers=headers)
        info(r.content)
    except Exception as e:
        info(e)
    return

if __name__ == "__main__":
    config = configparser.ConfigParser()

    dashrpc = DashRPC(mainnet=MAINNET)

    vend = Vend()

    dataQueue = queue.PriorityQueue()

    #init GUI
    listener = GuiListener(65448, dataQueue)
    #DONE
    listener.setDaemon(True)
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
        time.sleep(10)

    rpcaddress = RPCAddress(mainnet=MAINNET, dashrpc=dashrpc)

    vend.set_address_chain(rpcaddress)  # attach address
    vend.set_dashrpc(dashrpc)  # attach local wallet for refunds

    phl = PiHatListener(dataQueue=dataQueue)
    #DONE
    phl.setDaemon(True)
    phl.start()
    phl.onThread(phl.subscribeToVMC)

    dashzmq = DashZMQ(dataQueue=dataQueue, mainnet=MAINNET)
    #DONE
    dashzmq.setDaemon(True)
    dashzmq.start()
    waiting_transaction = False

    while True:
        msg = dataQueue.get().data
        info("Dequeued message: " + str(msg))

        # Reconnect procedura
        if not dashrpc.ready():
            c.sendMessage('syncScreen')
            dashrpc.connect()
            info("waiting for dashd to finish synchronizing")
            while(not dashrpc.ready()):
                time.sleep(10)
            c.sendMessage('idleScreen')

        if int(time.time() - start_time) >= 60 and waiting_transaction:
            phl.onThread(phl.declineVending)
            waiting_transaction = False

        if 'error' in msg.keys():
            if msg['error'] == 'cashless':
                phl.cashless_counter += 1
                if phl.cashless_counter == 2:
                    c.sendMessage('syncScreen')
                    phl.onThread(phl.unsubscribeToVMC)
                    time.sleep(10)
                    phl.onThread(phl.subscribeToVMC)
                    phl.cashless_counter = 0


        if 'subscribed' in msg.keys():
            if msg['subscribed'] == True:
                c.sendMessage('idleScreen')
                info("*" * 80)
                info(" --> ready. listening to dash %s network." % (MAINNET and 'mainnet' or 'testnet'))
                phl.subscribed = True

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
            vend.set_product_cost(dash_amount)  # set product cost in dash

            info('ID-> ' + str(msg['id']))
            info('AMOUNT-> ' + str(amount) + ' kn')
            info('CHOICE->' + str(choice))
            info('ADDRESS-> ' + vend.current_address)
            info('DASH AMOUNT' + str(dash_amount))

            c.sendMessage('paymentScreen-' + vend.current_address + '-' + str(dash_amount))
            start_time = time.time()
            waiting_transaction = True

        if 'transaction' in msg.keys():
            try:
                transaction = dashrpc._proxy.gettransaction(msg['transaction'], True)
                if transaction['instantlock']:
                    if int(time.time() - start_time) < 60:
                        retVal = vend.process_IS_transaction(transaction)
                        #TODO logika za preplaćeni iznos
                        if retVal == 'valid' or retVal == 'over':
                            phl.onThread(phl.confirmVending)
                            start_time = 0
                            waiting_transaction = False
                            c.sendMessage('finalScreen')
                            if retVal == 'over':
                                c.sendMessage('overpaid')
                            post_api(choice, amount, dash_amount)
                            time.sleep(30)
                        elif retVal == 'under':
                            #DONE manji iznos
                            c.sendMessage('refund')
                    else:
                        #DONE neočekivani
                        c.sendMessage('unexpected')
                        vend._refundall(transaction)

            except JSONRPCException as e:
                info(e)

        time.sleep(1)
