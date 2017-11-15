#!/bin/env python3

import binascii
import struct
import time
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

        (f.addr, qosbyte, f.length, f.packetid, f.fragment, f.checksum) = struct.unpack('!BBHBBH',
                                                                                        bytearr[:Frame.headerlength])

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
            self.working_queues.append(queue.Queue())

    def clean_fragments(self, timeout):

        key_list = list(self.fragments.keys())

        for k in key_list:
            if time.perf_counter() - self.fragments[k][2] > timeout:
                print("Fragment dropped due to timeout {}".format(k))
                del self.fragments[k]

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
        idpacket, [len, [payload,payload2...]]
        }
        """


        check = fragment.checksum
        fragment.checksum = 0
        if check != binascii.crc32(Frame.pack_frame(fragment))&0xFFFF:
            print("Network Layer: BAD CHECKSUM ({}), packetid: {}".format(check, fragment.packetid) )
            return None

        # TODO: add time of last receive to tuple, and purge old values

        if iden in self.fragments:
            frag_list = self.fragments[iden][1]

            surplus = fragment.fragment + 1 - len(frag_list)
            if surplus > 0:
                frag_list.extend([None]*surplus)
            frag_list[fragment.fragment] = fragment.payload[:fragment.length] # [:fragment.length] removes padding

            self.fragments[iden][2] = time.perf_counter()

            if not fragment.MF:
                # self.fragments[iden] = [fragment.fragment, frag_list]
                self.fragments[iden][0] = fragment.fragment
        else:
            total_fragments = None
            if not fragment.MF:
                total_fragments = fragment.fragment

            frag_list = [None]*(fragment.fragment + 1)
            frag_list[fragment.fragment] = fragment.payload[:fragment.length]
            self.fragments[iden] = [total_fragments, frag_list, time.perf_counter()]

        valid_frags = 0
        for f in self.fragments[iden][1]:
            if f:
                valid_frags += 1

        if valid_frags - 1 == self.fragments[iden][0]:
            # reassemble frame now that all fragments have been received.
            datagram = bytearray()
            for frag in self.fragments[iden][1]:
                datagram += frag
            del self.fragments[iden]
            return datagram

        return None

    def process_receive_queue(self, maxnum):
        """
        :param maxnum: number of elements to receive, or None if no limit
        :type maxnum: int
        :return:
        :rtype:
        """
        i = 0
        while not self.in_queue.empty():
            if maxnum and i > maxnum:
                break
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

    def do_receive(self, timeout = 10):
        max_frames_to_process = 1  # at some point we may want to process more then one frame per func call
        frames_processed = 0

        self.clean_fragments(timeout)

        for queue_num, working_queue in enumerate(self.working_queues):
            if frames_processed >= max_frames_to_process:
                return frames_processed

            if not working_queue.empty():
                try:
                    data = working_queue.get_nowait()
                except queue.Empty:
                    continue

                f = Frame.unpack_frame(data)

                if f.fragment == 0 and f.MF is False:
                    # single unfragmented frame pass along untouched
                    try:
                        self.out_queues[queue_num].put_nowait(f.payload[:f.length])
                        frames_processed += 1
                    except queue.Full:
                        continue
                else:
                    datagram = self.add_fragment(f)
                    frames_processed += 1
                    if datagram:
                        # this fragment caused a datagram to be completed
                        try:
                            self.out_queues[queue_num].put_nowait(datagram)
                        except queue.Full:
                            return frames_processed


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
            self.working_queues.append(queue.Queue())

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
            if frames_processed >= max_frames_to_process:
                return frames_processed

            while not working_queue.empty() or not in_queue.empty():
                if not working_queue.empty():
                    if frames_processed >= max_frames_to_process:
                        return frames_processed

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
                            return frames_processed

                        frame.payload = data[0:payload_mtu]
                        frame.MF = True
                        frame.length = payload_mtu
                    else:
                        frame.length = len(data)
                        frame.payload = data + b'\x00' * (payload_mtu - frame.length)
                        frame.MF = False

                    frame.addr = 0  # TODO: hardcoded for now
                    frame.qos = queue_num  # queue number refers to its priority, lower = better
                    frame.checksum = 0
                    frame.fragment = frag
                    frame.packetid = iden
                    frame.NACK = False

                    frame.checksum = binascii.crc32(Frame.pack_frame(frame))&0xFFFF

                    try:
                        self.out_queue.put_nowait(Frame.pack_frame(frame))
                        working_queue.task_done()
                    except queue.Full:
                        return frames_processed

                    frames_processed += 1

                if not in_queue.empty():
                    try:
                        data = in_queue.get_nowait()
                    except queue.Empty:
                        break

                    frame = Frame()

                    self.idnum += 1

                    iden = self.idnum

                    if iden > 255:
                        iden = 0

                    if len(data) > payload_mtu:
                        try:
                            # note adding to the working queue
                            working_queue.put_nowait((iden, 1, data[payload_mtu:]))
                        except queue.Full:
                            return frames_processed

                        frame.payload = data[0:payload_mtu]
                        frame.MF = True
                        frame.length = payload_mtu
                    else:
                        frame.length = len(data)
                        frame.payload = data + b'\x00' * (payload_mtu - frame.length)
                        frame.MF = False

                    frame.addr = 0  # TODO: hardcoded for now
                    frame.qos = queue_num  # queue number refers to its priority, lower = better
                    frame.checksum = 0
                    frame.fragment = 0
                    frame.packetid = iden
                    frame.NACK = False

                    frame.checksum = binascii.crc32(Frame.pack_frame(frame))&0xFFFF

                    try:
                        self.out_queue.put_nowait(Frame.pack_frame(frame))
                        in_queue.task_done()
                    except queue.Full:
                        return frames_processed

                    frames_processed += 1
        return frames_processed


def test():
    import random
    queuePHY = queue.Queue()
    queuePHY_shuffle = queue.Queue()


    queueA = queue.Queue()
    queueB = queue.Queue()
    transmit_queues = [queueA, queueB]

    queueA_R = queue.Queue()
    queueB_R = queue.Queue()
    receive_queues = [queueA_R, queueB_R]

    t = NetworkLayerTransmit(queuePHY, transmit_queues)
    r = NetworkLayerReceive(queuePHY_shuffle, receive_queues)

    counter = 0

    while counter < 20:
        queueA.put_nowait(str.encode("A " + str(counter) + " " + "A" * 10 * counter))
        counter += 1
        queueB.put_nowait(str.encode("B " + str(counter) + " " + "B" * 10 * counter))
        counter += 1
        queueB.put_nowait(str.encode("B " + str(counter) + " " + "B" * 20 * counter))
        counter += 1
        queueA.put_nowait(str.encode("A " + str(counter) + " " + "A" * 40 * counter))
        counter += 1
        queueB.put_nowait(str.encode("B " + str(counter) + " " + "B" * 30 * counter))
        counter += 1

    while t.do_transmit(150):
        pass

    phy_list = []
    while not queuePHY.empty():
        phy_list.append(queuePHY.get_nowait())

    random.shuffle(phy_list)

    for el in phy_list:
        queuePHY_shuffle.put_nowait(el)

    r.process_receive_queue(None)

    for _ in range(1000):
        r.do_receive()

        while not queueA_R.empty():
            try:
                print(queueA_R.get_nowait())
            except:
                pass

        while not queueB_R.empty():
            try:
                print(queueB_R.get_nowait())
            except:
                pass
        pass

if __name__ == "__main__":
    test()
