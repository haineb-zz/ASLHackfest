#!/bin/env python3

import struct
import queue


class Frame:
    headerlength = 8

    def __init__(self):
        self.addr = None
        self.qos = None
        self.MF = None
        self.NACK = None
        self.length = None
        self.fragment = None
        self.checksum = None
        self.packetid = None
        self.payload = None


class NetworkLayer:
    def __init__(self, out_queue, in_queues):
        """
        :param out_queue:
        :type out_queue: queue.Queue
        :param in_queues:
        :type in_queues: List
        """
        self.in_queues = in_queues
        self.out_queue = out_queue
        self.idnum = 0

        self.working_queues = []

        for _ in in_queues:
            self.working_queues.append(queue.Queue)

            # TODO: ADD PAYLOAD FIELD

    @staticmethod
    def unpack_frame(bytearr):
        f = Frame()

        (f.addr, qosbyte, f.length, f.packetid, f.fragment, f.checksum) = struct.unpack('!BBHBBH', bytearr)

        f.qos = qosbyte & 0x0F
        f.MF = qosbyte & 128 != 0
        f.NACK = qosbyte & 64 != 0
        f.payload = bytearr[Frame.headerlength:]

        return f

    @staticmethod
    def pack_frame(f):
        # everything should be in network order (big endian)
        qosbyte = (f.qos & 0x0F) | (128 if f.MF else 0) | (64 if f.NACK else 0)

        strut = struct.pack('!BBHBBH', f.addr, qosbyte, f.length, f.packetid, f.fragment, f.checksum)

        return strut + f.payload

    def do_transmit(self, mtu):
        """
        Will proccess one frame for transmission, will pull from the high priority queue before the low
        :param mtu: frame length
        :type mtu: int
        """
        max_frames_to_process = 1  # at some point we may want to process more then one frame per func call
        frames_processed = 0
        payload_mtu = mtu - Frame.headerlength

        # GOES THROUGH WORKING QUEUE 0, QUEUE 0, WORKING 1, QUEUE 1, working 2 ....
        for queue_num, (working_queue, in_queue) in enumerate(zip(self.working_queues, self.in_queues)):
            if frames_processed < max_frames_to_process:
                return

            while not working_queue.empty():
                if frames_processed < max_frames_to_process:
                    return True

                try:
                    (iden, frag, data) = working_queue.get_nowait()
                except queue.Empty:
                    break
                # the queue tuple contains information like the id number of the datagram, the fragment number
                #  and the payload

                frame = Frame()

                if len(data) > payload_mtu:
                    try:
                        working_queue.put_nowait((iden, frag + 1, data[payload_mtu:]))
                    except queue.Full:
                        return False

                    frame.payload = data[0:payload_mtu]
                    frame.MF = True
                    frame.length = payload_mtu
                else:
                    frame.length = len(data)
                    frame.payload = data + b'\x00' * (payload_mtu - frame.length)
                    frame.MF = False

                frame.addr = 0  # TODO: hardcoded for now
                frame.qos = queue_num  # queue number refers to its priority, lower = better
                frame.checksum = 0  # TODO
                frame.fragment = frag
                frame.packetid = iden
                frame.NACK = False

                try:
                    self.out_queue.put_nowait(self.pack_frame(frame))
                except queue.Full:
                    return False

                frames_processed += 1

            while not in_queue.empty():
                try:
                    data = in_queue.get_nowait()
                except queue.Empty:
                    break

                frame = Frame()

                iden = self.idnum + 1

                if iden > 255:
                    iden = 0

                if len(data) > payload_mtu:
                    try:
                        # note adding to the working queue
                        working_queue.put_nowait((iden, 1, data[payload_mtu:]))
                    except queue.Full:
                        return False

                    frame.payload = data[0:payload_mtu]
                    frame.MF = True
                    frame.length = payload_mtu
                else:
                    frame.length = len(data)
                    frame.payload = data + b'\x00' * (payload_mtu - frame.length)
                    frame.MF = False

                frame.addr = 0  # TODO: hardcoded for now
                frame.qos = queue_num  # queue number refers to its priority, lower = better
                frame.checksum = 0  # TODO
                frame.fragment = 1
                frame.packetid = iden
                frame.NACK = False

                try:
                    self.out_queue.put_nowait(self.pack_frame(frame))
                except queue.Full:
                    return False

                frames_processed += 1
