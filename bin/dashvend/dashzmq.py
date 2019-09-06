import zmq
import binascii
import struct
import time
import threading
import queue
from priorityentry.priorityentry import PriorityEntry

class DashZMQ(threading.Thread):

    def __init__(self, dataQueue, loop_time = 1.0/60, mainnet=False, host="tcp://127.0.0.1", port=10001):
        self.dataQueue = dataQueue
        self.timeout = loop_time

        self.host = host
        self.port = port

        self.connect()
        super(DashZMQ, self).__init__()

    def run(self):
        self.listen()

    def connect(self):
        self.zmqContext = zmq.Context()
        self.zmqSubSocket = self.zmqContext.socket(zmq.SUB)

        self.zmqSubSocket.setsockopt(zmq.SUBSCRIBE, b"hashtxlock")
        self.zmqSubSocket.connect("{}:{}".format(self.host, self.port))

    def listen(self):
        while True:
            msg = self.zmqSubSocket.recv_multipart()
            topic = str(msg[0].decode("utf-8"))
            body = msg[1]
            sequence = "Unknown"

            if len(msg[-1]) == 4:
                msgSequence = struct.unpack('<I', msg[-1])[-1]
                sequence = str(msgSequence)
                print(sequence)

            if topic == "hashtxlock":
                h = binascii.hexlify(body).decode("utf-8")
                self.dataQueue.put(PriorityEntry(2, {'transaction': h}))
