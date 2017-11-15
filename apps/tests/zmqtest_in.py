#!/usr/bin/env python

import zmq


context = zmq.Context()
sock = context.socket(zmq.SUB)
sock.setsockopt(zmq.SUBSCRIBE,'')
sock.connect('tcp://127.0.0.1:6130')

while True:
    data = sock.recv()
    print('recv')
    print(data)
