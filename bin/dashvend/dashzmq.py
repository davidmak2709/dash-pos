import zmq
import binascii
import struct
import time
from bitcoinrpc.authproxy import JSONRPCException

class DashZMQ(object):

    def __init__(self, mainnet=False, host="tcp://127.0.0.1", port=10001,dashrpc=None):
        self.host = host
        self.port = port
        self.txs = []

        self.dashrpc = dashrpc
        if self.dashrpc is None:
            # TODO: set new dashRPC connection
            print("DashRPC not set")


    def connect(self):
        self.zmqContext = zmq.Context()
        self.zmqSubSocket = self.zmqContext.socket(zmq.SUB)

        self.zmqSubSocket.setsockopt(zmq.SUBSCRIBE, b"hashtx")
        self.zmqSubSocket.setsockopt(zmq.SUBSCRIBE, b"hashtxlock")
        self.zmqSubSocket.connect("{}:{}".format(self.host, self.port))

    def set_vend(self,vend):
        self.vend = vend

    def listen(self):
        start_time = time.time()
        while True:
            if int(time.time() - start_time) >= 40:
                return False
            msg = self.zmqSubSocket.recv_multipart()
            topic = str(msg[0].decode("utf-8"))
            body = msg[1]
            sequence = "Unknown"

            if len(msg[-1]) == 4:
                msgSequence = struct.unpack('<I', msg[-1])[-1]
                sequence = str(msgSequence)
                print(sequence)
            """
            if topic == "hashtx":
                h = binascii.hexlify(body).decode("utf-8")
                try:
                    transaction = self.dashrpc._proxy.gettransaction(h, True)
                    self.txs.append(h)
                    if "error" not in transaction.keys():
                        self.vend.process_IS_transaction(tx=transaction)
                        return True
                except JSONRPCException as e:
                    pass
            """
            if topic == "hashtxlock":
                h = binascii.hexlify(body).decode("utf-8")
                try:
                    transaction = self.dashrpc._proxy.gettransaction(h, True)
                    if transaction["instantlock"]:
                        #self.txs.remove(h)
                        retVal = self.vend.process_IS_transaction(tx=transaction)
                        if retVal == "refund_transaction":
                            continue
                        else:
                            return retVal
                        #return True

                except JSONRPCException as e:
                    pass

            
