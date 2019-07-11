from time import sleep
import socket
import os
import subprocess
from dashvend.config import DASHVEND_DIR, DASHD_PATH, DASHCORE_DIR, PASSWORD

REMOTE_SERVER = 'www.google.com'

def is_connected(hostname):
    try:
        host = socket.gethostbyname(hostname)
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

def is_mounted():
    return os.path.ismount('/media/pi/c1821e3d-c341-415b-ac2d-6653f1a12e3f')
  
if __name__ == "__main__":
    while not (is_connected(REMOTE_SERVER) and is_mounted()):
        print('Waiting for connection and external drive...')
        sleep(1)
    print('Connected and mounted')

    subprocess.Popen(str('sudo ' + DASHD_PATH + ' -deamon -datadir=' + DASHCORE_DIR + ' -pid=' + DASHCORE_DIR + '/dashd.pid -listen -rpcallowip=127.0.0.1 -zmqpubhashtx=tcp://127.0.0.1:10001 -zmqpubhashtxlock=tcp://127.0.0.1:10001').split(' '))
    subprocess.Popen(str('python3 ' + DASHVEND_DIR + '/bin/conversion/conversion_dash_hrk.py').split(' '))
    sleep(1)
#    subprocess.Popen(str('python3 ' + DASHVEND_DIR + '/bin/threadedgui.py').split(' '))
    subprocess.Popen(str('sudo python3 ' + DASHVEND_DIR + '/bin/dashvend.py').split(' '))

   
