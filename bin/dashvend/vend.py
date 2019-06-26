"""
vending app - processing, display, and relay trigger interface
"""

from threading import Timer

from . config import VENDING_COST
from . display import Display  # lcd screen for payment screens
from . logger import info, warn  # stdout and file logging
from . trigger import Trigger  # interface to machine relay

from bitcoinrpc.authproxy import JSONRPCException

class Vend(object):

    # display states (screens)
    STARTUP = 0
    READY = 1
    SALE = 2
    TXREFUND = 3
    SHUTDOWN = 4

    def __init__(self):
        """ connect hardware, initialize state dir """
        self.trigger = Trigger()
        self.display = Display()
        self.current_address = None
        self.cost = 0
        self.set_state(Vend.STARTUP)

    def get_listeners(self):
        return ('tx', self.ix.recv_tx,
                'ix', self.ix.recv_ix,
                'txlvote', self.ix.recv_votes,
                'block', self.recv_block)

    def set_instantx(self, ix):
        ix.set_vend(self)
        self.ix = ix

    def set_dashrpc(self, dashrpc):
        self.dashrpc = dashrpc

    # payment processing

    def set_address_chain(self, bip32):
        """ attach pycoin key instance """
        self.bip32 = bip32
        self.get_next_address()

    def get_next_address(self, increment=False):
        """ payment address to monitor """
        self.current_address = self.bip32.get_next_address(increment)
     #   self.ix.set_watch_address(self.current_address)

    def set_product_cost(self, cost):
        """ set required float value to trigger sale """
        # convert to duffs
        self.cost = int(cost * 1e8)

    # vending processing

    def trigger_sale(self):
        self.set_state(Vend.SALE)
    #    self.trigger.trigger()
        Timer(15, lambda: self.set_state(Vend.READY), ()).start()

    def show_txrefund(self):
        self.set_state(Vend.TXREFUND)
        Timer(10, lambda: self.set_state(Vend.READY), ()).start()

    def set_state(self, state):
        self.state = state
        self.display.show_screen_number(
            self.state, self.current_address, float(self.cost / 1e8))

    def process_IS_transaction(self, tx):
        if float(tx["amount"]) == VENDING_COST:
            self.trigger_sale()
        else:
            self._refund(tx)


    def _refund(self, tx):
        amount = float(tx["amount"])
        address = self.select_return_address(tx["txid"])
        if amount < VENDING_COST:
            self.sendtoaddress(addr = address,amount = amount)
            self.show_txrefund()
        elif amount > VENDING_COST:
            self.sendtoaddress(addr = address,amount = amount - VENDING_COST)
            self.trigger_sale()

    def sendtoaddress(self, addr, amount):
        p = self.dashrpc._proxy
        try:
            p.sendtoaddress(addr, amount)
        except JSONRPCException:
            warn("**********************************************************")
            warn("INSUFFICIENT FUNDS TO PROCESS REFUND/BOUNCE FOR")
            warn("    %s to %s " % (amount, addr))
            warn("    wallet balance: %s" % (p.getbalance()))
            warn("**********************************************************")


    def get_txn(self, txid):
        p = self.dashrpc._proxy
        return p.getrawtransaction(txid,True)

    def select_return_address(self, txid):
        prevout = self.get_txn(txid)["vin"][0]
        source = self.get_txn(prevout["txid"])["vout"]
        return source[prevout["vout"]]["scriptPubKey"]["addresses"][0]
