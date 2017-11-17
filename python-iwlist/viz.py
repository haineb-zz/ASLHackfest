#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy
import pmt
import struct
import zmq

import binascii
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
    def __init__(self, portIn):
        self.access_points = dict()

        self._ipAddress = '127.0.0.1'
        self._portIn = portIn

        self._zmqContext = zmq.Context()
        self._socketIn = self._zmqContext.socket(zmq.SUB)
        #using blocking recv for now
        #self._socketIn.RCVTIMEO = timeout
        self._socketIn.connect('tcp://%s:%s' % (self._ipAddress,self._portIn))
        try:
            self._socketIn.setsockopt(zmq.SUBSCRIBE, '') # python2
        except TypeError:
            self._socketIn.setsockopt_string(zmq.SUBSCRIBE, '') # python3, if this throws an exception... give up...


    def unpack(self, data):
        channels = [{}]*16

        datalen = len(data)
        i = 0
        fixlen = 14
        while i < datalen - fixlen:
            (dbm, channel, mac) = struct.unpack('!bb12s', data[i:i+fixlen])

            encryption = channel&128 != 0
            channel = channel&0x0F
            i += fixlen
            ssid = data[i:].split('\0', 1)[0]
            i+= len(ssid) + 1

            # print(mac, ssid, channel, encryption, dbm)
            channels[channel][mac] = Access_Point(mac, ssid, channel, encryption, dbm)

        return channels


    def recv(self):
        msg = self._socketIn.recv()
        pdu = pmt.deserialize_str(msg)
        cdr = pmt.to_python(pmt.cdr(pdu))
        cdr = numpy.getbuffer(cdr)
        return cdr


    def update_ap(self, ap):
        self.access_points[ap.mac] = ap


    def run(self):
        while True:
            print self.unpack(self.recv()), "\n"

        N = len(self.access_points)
        fig, ax = plt.subplots(ncols=11)
        plt.bar()


def test():
    Viz(5159).run()


if __name__ == "__main__":
    test()
