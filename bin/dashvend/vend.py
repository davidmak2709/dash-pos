"""
vending app - processing txs
"""

from threading import Timer
from . logger import info, warn  # stdout and file logging
from bitcoinrpc.authproxy import JSONRPCException

class Vend(object):

    def __init__(self):
        self.current_address = None
        self.cost = 0

    def set_dashrpc(self, dashrpc):
        self.dashrpc = dashrpc

    # payment processing

    def set_address_chain(self, addressGen):
        """ attach pycoin key instance """
        self.addressGen = addressGen
        self.get_next_address()

    def get_next_address(self, increment=False):
        """ payment address to monitor """
        self.current_address = self.addressGen.get_next_address()

    def set_product_cost(self, cost):
        """ set required float value to trigger sale """
        self.cost = cost

    # vending processing

    def process_IS_transaction(self, tx):
        if float(tx["amount"]) == self.cost:
            return "valid"
        else:
            return self._refund(tx)

    def _refund(self, tx):
        amount = float(tx["amount"])
        address = self.select_return_address(tx["txid"])
        if amount < 0:
            return "invalid"
        elif amount < self.cost:
            self.sendtoaddress(addr=address, amount=amount)
            return "under"
        elif amount > self.cost:
            self.sendtoaddress(addr=address, amount=amount-self.cost)
            return "over"

    def _refundall(self, tx):
        amount = float(tx["amount"])
        if amount <= 0:
            return False
        address = self.select_return_address(tx["txid"])
        self.sendtoaddress(addr=address, amount=amount)
        return True

    def sendtoaddress(self, addr, amount):
        p = self.dashrpc._proxy
        try:
            amount = abs(round(amount, 5))
            p.sendtoaddress(addr, amount)
        except JSONRPCException as e:
            warn("**********************************************************")
            warn("INSUFFICIENT FUNDS TO PROCESS REFUND/BOUNCE FOR")
            warn("    %s to %s " % (amount, addr))
            warn("    wallet balance: %s" % (p.getbalance()))
            warn("**********************************************************")
            warn(e)

    def get_txn(self, txid):
        p = self.dashrpc._proxy
        return p.getrawtransaction(txid,True)

    def select_return_address(self, txid):
        prevout = self.get_txn(txid)["vin"][0]
        source = self.get_txn(prevout["txid"])["vout"]
        return source[prevout["vout"]]["scriptPubKey"]["addresses"][0]
