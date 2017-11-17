#! /usr/bin/python

from asl_sdr_hackfest.protocols.network_layer import Frame

# from random import SystemRandom as sysran
import queue
import sys
import bitarray
import threading

from entropy_engine import *

def to_bitarray(bytearray):
    bits = ''
    for byte in bytearray:
        # Remove '0b' prefix and pad up to 8 zeros per byte
        bits += bin(byte).split('0b')[1].zfill(8)
    return bitarray.bitarray(bits)

def to_bytearray(bits):
    # Note: python does implicit conversions
    if isinstance(bits, bitarray.bitarray):
        return bytearray(bits)
    elif isinstance(bits, str):
        return bytearray(bits, 'utf8')
    else:
        raise

class Chaos_layer(threading.Thread, object):
    def __init__ (self, chance_to_run = 0.5):
        self.bits = bitarray.bitarray(Frame.headerlength*8)

        self.chance_for_fun = 0
        if (chance_to_run <= 1):
            self.chance_for_fun *= 100
        else:
            self.chance_for_fun = chance_to_run

        self.d6 = Dice()
        self.d20 = D20()
        self.d100 = D100()

    def run (self, bytearr_queue, bytearr):
        roll100 = self.d100.roll()
        roll6 = self.d6.roll()

        chaos_tool = None

        if (roll100 < self.chance_for_fun and roll6 == 1):
            chaos_tool = self.bitFlips
        elif (roll100 < self.chance_for_fun and roll6 == 2):
            chaos_tool = self.zeroField
        elif (roll100 < self.chance_for_fun and roll6 == 3):
            chaos_tool = self.genetic
        elif (roll100 < self.chance_for_fun and roll6 == 4):
            chaos_tool = self.delayed_enqueue
        elif (roll100 < self.chance_for_fun and roll6 == 5):
            chaos_tool = self.random_delayed_enqueue
        elif (roll100 < self.chance_for_fun and roll6 == 6):
            chaos_tool = None
        else:
            chaos_tool = None
            # raise

        try:
            chaos_tool (bytearr_queue, bytearr)
        except:
            bytearr_queue.put(bytearr)

    def bitFlips (self, bytearr_queue, bytearr):
        f_bits = to_bitarray(bytearr)
        f_bits.invert()

        f_bytes = to_bytearray(f_bits)
        bytearr_queue.put(f_bytes)

    # TODO: write test?
    def zeroField (self, bytearr_queue, bytearr):
        frame = Frame.unpack_frame(bytearr)
        field = self.d6.roll()
        if field == 0:
            frame.addr = None
        elif field == 1:
            frame.qos = None
        elif field == 2:
            frame.MF = None
        elif field == 3:
            frame.NACK = None
        elif field == 4:
            frame.length = None
        elif field == 5:
            frame.fragment = None
        else:
            frame.packetid = None
            frame.checksum = None
            frame.payload = None

        bytearr_queue.put(Frame.pack_frame(frame))

    def genetic (self, bytearr_queue, bytearr):
        f_bits = to_bitarray(bytearr)

        begin = self.d20.roll()
        end = len(f_bits) - self.d20.roll()

        if begin > end:
            begin, end = end, begin

        self.bits[begin:end], f_bits[begin:end] = f_bits[begin:end], self.bits[begin:end]

        # TODO: For mutation, 100 % 64 != 0 (not even)
        roll6 = self.d6.roll()
        roll100 = self.d100.roll()
        for n in range(roll6):
            if (roll100 > self.chance_for_fun):
                f_bits[roll100%len(f_bits)] = not f_bits[roll100%len(f_bits)]

        bytearr_queue.put(to_bytearray(f_bits))

    def delayed_enqueue (self, bytearr_queue, bytearr, secs = 1):
        # Note: intentionally not really thread-safe per put_nowait
        if (not bytearr_queue.full()):
            print ("delay enqueue by %d seconds" % secs)
            t = threading.Timer(secs, bytearr_queue.put_nowait, [bytearr])
            t.start()
            return t
        else:
            raise

    def random_delayed_enqueue (self, bytearr_queue, bytearr):
        secs = self.d6.roll()
        return self.delayed_enqueue(bytearr_queue, bytearr, secs)
