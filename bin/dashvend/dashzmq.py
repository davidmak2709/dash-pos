import zmq
import binascii
import struct
import time
import threading
import queue
from bitcoinrpc.authproxy import JSONRPCException

class DashZMQ(threading.Thread):

    def __init__(self, dataQueue, dashrpc, loop_time = 1.0/60, mainnet=False, host="tcp://127.0.0.1", port=10001):
        self.functionQueue = queue.Queue()
        self.dataQueue = dataQueue
        self.timeout = loop_time

        self.host = host
        self.port = port

        self.dashrpc = dashrpc
        self.connect()
        super(DashZMQ, self).__init__()

    def run(self):
        self.listen()

    def connect(self):
        self.zmqContext = zmq.Context()
        self.zmqSubSocket = self.zmqContext.socket(zmq.SUB)

        self.zmqSubSocket.setsockopt(zmq.SUBSCRIBE, b"hashtx")
        self.zmqSubSocket.setsockopt(zmq.SUBSCRIBE, b"hashtxlock")
        self.zmqSubSocket.connect("{}:{}".format(self.host, self.port))

    def set_vend(self,vend):
        self.vend = vend

    def listen(self):
        #start_time = time.time()
        while True:
            #if int(time.time() - start_time) >= 60:
                #return False
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
                        self.dataQueue.put({'transaction': transaction})
                        """retVal = self.vend.process_IS_transaction(transaction, start_time)
                        if not retVal:
                            continue
                        else:
                            return retVal"""

                except JSONRPCException as e:
                    pass
