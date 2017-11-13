#!/bin/env python3

import struct
import queue


class Frame:
    headerlength = 8
    # addr, qos, len, len, id, fragment, check, check
    addr_pos = 0
    qos_pos = 1
    len_pos = 2
    packetid_pos = 4
    fragment_pos = 5
    checksum_pos = 6

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


class NetworkLayerReceive:
    def __init__(self, in_queue, out_queues):
        """
        :param in_queue:
        :type in_queue: queue.Queue
        :param out_queues:
        :type out_queues: List
        """
        self.in_queue = in_queue
        self.out_queues = out_queues

        self.working_queues = []
        self.fragments = {}

        for _ in out_queues:
            self.working_queues.append(queue.Queue)

    def add_fragment(self, fragment):
        """
        :param self:
        :type self:
        :param fragment:
        :type fragment: Frame
        :return:
        :rtype:
        """
        iden = fragment.packetid

        """fragments structure
        {
        idpacket, (len, [(fragid, payload)])
        }
        """

        if iden in self.fragments:
            self.fragments[iden][1].append((fragment.fragment, fragment.payload))
            if not fragment.MF:
                self.fragments[iden][0] = fragment.fragment
        else:
            total_fragments = None
            if not fragment.MF:
                total_fragments = fragment.fragment

            frag_list = [(fragment.fragment, fragment.payload)]
            self.fragments[iden] = (total_fragments, frag_list)

        if len(self.fragments[iden][1]) == self.fragments[iden][0]:
            # reassemble frame now that all fragments have been received.
            datagram = bytearray()
            for frag in self.fragments[iden][1]:
                datagram.extend(frag)
            return datagram

        return None

    def do_receive(self):
        max_frames_to_process = 1  # at some point we may want to process more then one frame per func call
        frames_processed = 0

        while not self.in_queue.empty():
            # TODO: maybe place a limit on this???
            try:
                data = self.in_queue.get_nowait()
            except queue.Empty:
                pass
            queue_num = data[Frame.qos_pos] & 0x0F

            try:
                self.working_queues[queue_num].put_nowait(data)
                self.in_queue.task_done()
            except queue.Full:
                return False

        for queue_num, working_queue in enumerate(self.working_queues):
            if frames_processed < max_frames_to_process:
                return True

            if not working_queue.empty():
                try:
                    data = working_queue.get_nowait()
                except queue.Empty:
                    continue

                f = Frame.unpack_frame(data)

                if f.fragment == 0 and f.MF is False:
                    # single unfragmented frame pass along untouched
                    try:
                        self.out_queues[queue_num].put_nowait(f.payload)
                    except queue.Full:
                        # TODO: FIND out what happens when you do a .get without matching .task_done?
                        continue
                else:
                    datagram = self.add_fragment(data)
                    if datagram:
                        # this fragment caused a datagram to be completed
                        try:
                            self.out_queues[queue_num].put_nowait(datagram)
                        except queue.Full:
                            return False


class NetworkLayerTransmit:
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
                    self.out_queue.put_nowait(Frame.pack_frame(frame))
                    working_queue.task_done()
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
                    self.out_queue.put_nowait(Frame.pack_frame(frame))
                    in_queue.task_done()
                except queue.Full:
                    return False

                frames_processed += 1
