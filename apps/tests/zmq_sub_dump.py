#!/usr/bin/env python

import zmq
import sys
import binascii



context = zmq.Context()
sock = context.socket(zmq.SUB)
sock.setsockopt(zmq.SUBSCRIBE,'')
sock.connect('tcp://127.0.0.1:%s' % sys.argv[1])

while True:
    data = sock.recv()
    print(binascii.hexlify(data))
