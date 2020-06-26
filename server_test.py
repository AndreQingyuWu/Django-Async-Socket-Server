
'''
import esockets
import datetime
import schedule
import time
def handle_incoming(client, address):
    """
    Return True: The client is accepted and the server starts polling for messages
    Return False: The server disconnects the client.
    """
    print(client)
    client.sendall(b'\x03\x03\x00\x00\x00\x5f\x04\x10')
    #client.sendall(b'\x03\x03\x00\x0a\x00\x0e\xe5\xee')
    return True
#b'\x03\x03\x1e\x00\x00\x00\x00\x00\x00\x00\x00\tP\x00\x00\x00\x00\x00\x1a\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x93\xde'
def handle_readable(client):
    """
    Return True: The client is re-registered to the selector object.
    Return False: The server disconnects the client.
    """

    data = client.recv(1028)
    if data == b'':
        return False
    #if len(data) == 15:
    #client.sendall(b'\x03\x03\x00\x0a\x00\x0e\xe5\xee')
    print(data)
    return True

def get_data(server):
    print(datetime.datetime.now())
    for client, _ in server.clients.items():
        client.sendall(b'\x03\x03\x00\x00\x00\x5f\x04\x10')


server = esockets.SocketServer(port = 2333, host = "0.0.0.0", handle_incoming=handle_incoming,
                               handle_readable=handle_readable)
server.start()

schedule.every().hours.at(":00").do(get_data, server)
while True:
    schedule.run_pending()
'''

import sys
from socket import *  # portable socket interface plus constants
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')
django.setup()
from app import models

devices = models.Device.objects.all()
HOST = devices[0].ip
PORT = devices[0].port
PORT = int(PORT)
sockobj = socket(AF_INET, SOCK_STREAM)  # make a TCP/IP socket object
#sockobj.bind(('0.0.0.0', 2333))
print(HOST, PORT)

sockobj.connect(('0.0.0.0', 2333))  # connect to server machine + port
print('2')
sockobj.sendall(b'1111111')  # send line to server over socket
print('3')
data = sockobj.recv(1024)  # receive line from server: up to 1k
print('Client received: ', data)  # bytes are quoted, was 'x', repr(x)

sockobj.close()