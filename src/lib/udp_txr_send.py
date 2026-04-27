#!/usr/bin/env python3

import socket
import sys
from time import sleep
import random
from struct import pack

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

host, port = '---.---.--.---', 10000
server_address = (host, port)

# Generate some random start values
x, y, z = random.random(), random.random(), random.random()
data = "test"

print(str(data))
sock.sendto(data.encode(), server_address)
sock.close()