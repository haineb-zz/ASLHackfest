import threading
import queue
import time

from asl_sdr_hackfest.protocols.qos import QoS
from asl_sdr_hackfest.protocols.network_layer import NetworkLayerReceive, NetworkLayerTransmit, Frame



EGRESS_WINDOW_LOW = 8
EGRESS_WINDOW_HIGH = 12



class NetworkLayerReceiveHandler(threading.Thread, object):
    def __init__(self, output_data_func):
        self.running = False

        self.in_queue = queue.Queue()
        self.out_queues = []
        for i in range(0,16):
            self.out_queues.append(queue.Queue())
        
        self.rx_class = NetworkLayerReceive(self.in_queue, self.out_queues)

        self.output_data_func = output_data_func

        threading.Thread.__init__(self)
        

    def ingest_data(self, data):
        self.in_queue.put(data)


    def stop(self):
        self.running = False
        
        
    def run(self):
        self.running = True

        while (self.running is True):
            self.rx_class.process_receive_queue(maxnum = None)
            self.rx_class.do_receive()
            for q in self.out_queues:
                if q.empty() is False:
                    data = q.get()
                    self.output_data_func(data)




class NetworkLayerTransmitHandler(threading.Thread, object):
    def __init__(self, output_data_func, max_frames_per_second = 4):
        self.running = False

        self.xmit_delay = float(1)/float(max_frames_per_second)

        self.out_queue = queue.Queue()
        self.in_queues = []
        for i in range(0,16):
            self.in_queues.append(queue.Queue())
        
        self.tx_class = NetworkLayerTransmit(self.out_queue, self.in_queues)

        self.output_data_func = output_data_func

        threading.Thread.__init__(self)


    def ingest_data(self, data):
        qoscls = QoS.header_calculate(data)
        pcp = qoscls.get_priority_code()
        self.in_queues[pcp].put(data)
    
        
    def stop(self):
        self.running = False


    def run(self):
        self.running = True

        while (self.running is True):
            self.tx_class.do_transmit(mtu = 96 - Frame.headerlength - 40)
            time.sleep(self.xmit_delay)
            if self.out_queue.empty() is False:
                if self.out_queue.qsize() > EGRESS_WINDOW_HIGH:
                    self.egress_cull()
                data = self.out_queue.get()
                self.output_data_func(data)


    def egress_cull(self):
        init_size = self.out_queue.qsize()

        tmp_egress = []
        while self.out_queue.empty() is False:
            tmp_egress.append(self.out_queue.get())

        to_drop = len(tmp_egress) - EGRESS_WINDOW_LOW

        while to_drop > 0:
            max_cos = 0

            for pkt in tmp_egress:
                cos = pkt[Frame.qos_pos] & 0x0f
                if cos > max_cos:
                    max_cos = cos

            for i in reversed(range(0,len(tmp_egress))):
                if to_drop <= 0:
                    break

                cos = tmp_egress[i][Frame.qos_pos] & 0x0f
                if cos == max_cos:
                    tmp_egress[i] = None
                    to_drop -= 1

            tmp_egress = [x for x in tmp_egress if x is not None]

        tmp_egress.reverse()
        while len(tmp_egress) > 0:
            self.out_queue.put(tmp_egress.pop())

        culled_size = self.out_queue.qsize()
        print('Egress queue culled from {} to {}.'.format(init_size, culled_size))
