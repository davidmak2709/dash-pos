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
import queue

if __name__ == "__main__":
    dashrpc = DashRPC(mainnet=MAINNET)
    dashzmq = DashZMQ(mainnet=MAINNET,dashrpc=dashrpc)

#    dashp2p = DashP2P(mainnet=MAINNET)

    vend = Vend()
    dashzmq.connect()
    dashzmq.set_vend(vend)


    info("connecting to dashd, waiting for masternode and budget sync")
    dashrpc.connect()
    while(not dashrpc.ready()):
        time.sleep(60)

    bip32 = Bip32Chain(mainnet=MAINNET, dashrpc=dashrpc)

#    ix = InstantX()
#    vend.set_instantx(ix)  # attach instantx detection
    vend.set_address_chain(bip32)  # attach address chain
    vend.set_product_cost(VENDING_COST)  # set product cost in dash
    vend.set_dashrpc(dashrpc)  # attach local wallet for refunds


    dataQueue = queue.Queue()
    phl = PiHatListener(dataQueue=dataQueue)

    phl.start()
    phl.onThread(phl.subscribeToVMC)

    while True:
        msg = dataQueue.get()

        if not dashrpc.ready():
            dashrpc.connect()
#        dashp2p.connect()
#        dashp2p.forward(vend.get_listeners())
            info("waiting for dashd to finish synchronizing")
            while(not dashrpc.ready()):
                time.sleep(60)

        if 'error' in msg.keys():
            if msg['error'] == 'cashless':
                phl.cashless_counter += 1
                if phl.cashless_counter == 3:
                    phl.onThread(phl.unsubscribeToVMC)
                    time.sleep(10)
                    phl.onThread(phl.subscribeToVMC)
                    phl.cashless_counter = 0

        if 'subscribed' in msg.keys():
            if msg['subscribed'] == True:
                vend.set_state(Vend.STARTUP)
                info("*" * 80)
                info(" --> ready. listening to dash %s network." % (MAINNET and 'mainnet' or 'testnet'))

                phl.subscribed = True
                # tu ide button na ciji se klik pokrece startVending
                phl.onThread(phl.startVending)

        if 'amount' in msg.keys():
            print('PRICE-> ' + str(msg['amount']))
            phl.amount = msg["amount"]
            vend.set_state(Vend.READY)
            #phl.onThread(phl.declineVending)
            if dashzmq.listen():
                info("aaaaaaaa")
                phl.onThread(phl.confirmVending)
                vend.set_state(Vend.SALE)
            else:
                phl.onThread(phl.declineVending)
                vend.set_state(Vend.STARTUP)
 #       dashp2p.listen()
        time.sleep(1)
