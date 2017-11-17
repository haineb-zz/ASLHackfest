#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy
import pmt
import zmq

import numpy as np
import time


class Access_Point(object):
    def __init__(self, mac, essid, channel, encryption, sig_level):
        self.mac = mac
        self.essid = essid
        self.channel = channel
        self.encryption = encryption
        self.sig_level = sig_level

class Viz(object):
    def __init__(self, portIn, timeout = 100):
        self.access_points = dict()

        self._zmqContext = zmq.Context()
        self._socketIn = self._zmqContext.socket(zmq.SUB)
        self._socketIn.RCVTIMEO = timeout
        self._socketIn.connect('tcp://%s:%s' % (self._ipAddress,self._portIn))
        try:
            self._socketIn.setsockopt(zmq.SUBSCRIBE, '') # python2
        except TypeError:
            self._socketIn.setsockopt_string(zmq.SUBSCRIBE, '') # python3, if this throws an exception... give up...

    def recv(self):
        msg = self._socketIn.recv()
        pdu = pmt.deserialize_str(msg)
        cdr = pmt.to_python(pmt.cdr(pdu))
        cdr = numpy.getbuffer(cdr)
        return cdr


    def update_ap(self, ap):
        self.access_points[ap.mac] = ap


    def run(self):
        N = len(self.access_points)
        fig, ax = plt.subplots(ncols=11)
        plt.bar()
