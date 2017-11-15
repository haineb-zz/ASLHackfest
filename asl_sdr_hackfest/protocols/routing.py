#!/usr/bin/python

from bitstring import BitArray 
from asl_sdr_hackfest.protocols.protocol import Protocol
import struct

class Routing(Protocol):

    def __init__(self, *args, **kwargs):
        self.destination = kwargs.get('destination')
        self.transmitter = kwargs.get('transmitter')
        self.origin = kwargs.get('origin')
        self.ttl = kwargs.get('ttl')
        self.type = kwargs.get('type')


    def __str__(self):
        print("Printing out Routing values")
        print(self.get_destination())
        print(self.get_transmitter())
        print(self.get_origin())
        print(self.get_ttl())
        print(self.get_type())
        print("Done")
        return ""

    def to_bitarray(self):
        # Version is always 2
        ba = BitArray(self.TWO2)    
        ba.append(self.bin_formater(self.destination, 32))
        ba.append(self.bin_formater(self.transmitter, 32))
        ba.append(self.bin_formater(self.origin, 32))
        ba.append(self.bin_formater(self.type, 8))
        ba.append(self.bin_formater(self.ttl, 8))
        return ba

    # TODO Currently sets each field to a bitstring. 
    #      Should convert to actual values
    def from_bitarray(self, ba):
        bas = ba.bin
        self.set_destination(bas[0:32])
        self.set_transmitter(bas[32:64])
        self.set_origin(bas[64:96])
        self.set_type(bas[96:104])
        self.set_ttl(bas[104:112])

    # Getters
    def get_destination(self):
        return self.destination

    def get_transmitter(self):
        return self.transmitter

    def get_origin(self):
        return self.origin

    def get_ttl(self):
        return self.ttl

    def get_type(self):
        return self.type

    # Setters

    def set_destination(self, dest):
        self.destination = dest

    def set_transmitter(self, trans):
        self.transmitter = trans

    def set_origin(self, origin):
        self.origin = origin 

    def set_ttl(self, ttl):
        self.ttl = ttl

    def set_type(self, t):
        self.type = t


