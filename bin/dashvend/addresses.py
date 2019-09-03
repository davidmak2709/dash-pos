"""
address management
"""
from . logger import info,debug
from bitcoinrpc.authproxy import JSONRPCException

class RPCAddress(object):

    def __init__(self, mainnet, dashrpc):
        self.dashrpc = dashrpc
        self.mainnet = mainnet
        self._init_next_address()

    def get_address_info(self):
        """ get address and received amount """
        addr = self.dashrpc._proxy.getnewaddress()
        return {
            "addr": addr,
            "received": float(
                self.dashrpc._proxy.getreceivedbyaddress(addr))
        }


    def _init_next_address(self):
        """ find next unused address """
        r = self.dashrpc._proxy
        unused_found = False
        while (not unused_found):
            addr = self.get_address_info()
            if addr['received'] > 0:
                continue
            unused_found = True
        self.next_address = addr

    def get_next_address(self):
        self._init_next_address()
        info("--> new active payment address: %s" % self.next_address['addr'])
        return self.next_address['addr']
