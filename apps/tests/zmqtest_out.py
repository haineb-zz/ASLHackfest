#!/usr/bin/env python

import zmq
import time


context = zmq.Context()
sock = context.socket(zmq.PUB)
sock.bind('tcp://127.0.0.1:6130')

while True:
    sock.send('%d %d' % (1, 1))
    sock.send('foobar')

    time.sleep(1)
