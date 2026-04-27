#!/usr/bin/env python3

import socket
import sys
from struct import unpack

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the receiving port
host, port = '---.---.--.---', 10000
server_address = (host, port)

print(f'Starting UDP server on {host} port {port}')
sock.bind(server_address)

# Wait for message
while True:
    message, address = sock.recvfrom(1024)

    print(f'Received {len(message)} bytes:')
    x, y, z = unpack('3f', message)
    print(f'X: {x}, Y: {y}, Z: {z}')

sock.close()
