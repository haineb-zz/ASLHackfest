import threading
import queue

import qos
from network_layer import NetworkLayerReceive, NetworkLayerTransmit



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
                    self.output_data_func(q.get())




class NetworkLayerTransmitHandler(threading.Thread, object):
    def __init__(self, output_data_func):
        self.running = False

        self.out_queue = queue.Queue()
        self.in_queues = []
        for i in range(0,16):
            self.in_queues.append(queue.Queue())
        
        self.tx_class = NetworkLayerTransmit(self.out_queue, self.in_queues)

        self.output_data_func = output_data_func

        threading.Thread.__init__(self)


    def ingest_data(self, data):
        qoscls, payload = qos.QoS.header_consume(data)
        pcp = qoscls.get_priority_code()
        self.in_queues[pcp].put(data)
    
        
    def stop(self):
        self.running = False


    def run(self):
        self.running = True

        while (self.running is True):
            self.tx_class.do_transmit(mtu = 255)
            if self.out_queue.empty() is False:
                self.output_data_func(self.out_queue.get())
