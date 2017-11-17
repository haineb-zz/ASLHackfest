import threading
import queue

from asl_sdr_hackfest.zmq_sub import ZMQ_sub, ZMQ_sub_timeout
from asl_sdr_hackfest.zmq_pub import ZMQ_pub



class Service(threading.Thread, object):
    def __init__(self, portIn, portOut, name=None):
        self.running = False

        self._ZMQ_in = ZMQ_sub(portIn = portIn)
        self._ZMQ_out = ZMQ_pub(portOut = portOut)

        self._input_queue = queue.Queue()

        threading.Thread.__init__(self)
        self.setName(name)


        
    def run(self):
        self.running = True
        
        while self.running is True:
            try:
                data = self._ZMQ_in.recv()
            except ZMQ_sub_timeout:
                continue
            self.inputData(bytearray(data))


    def stop(self):
        self.running = False


    def inputData(self, data):
        self._input_queue.put(data)


    def readData(self):
        data = None
        if not self._input_queue.empty():
            data = self._input_queue.get()
        return data


    def outputData(self, data):
        self._ZMQ_out.send(data)
