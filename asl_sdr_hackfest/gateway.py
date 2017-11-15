import zmq
import threading

from asl_sdr_hackfest.zmq_sub import ZMQ_sub, ZMQ_sub_timeout
from asl_sdr_hackfest.zmq_pub import ZMQ_pub



class Gateway(threading.Thread, object):
    def __init__(self, portIn, portOut):
        self.running = False

        self._ZMQ_in = ZMQ_sub(portIn = portIn)
        self._ZMQ_out = ZMQ_pub(portOut = portOut)

        threading.Thread.__init__(self)

        
    def run(self):
        self.running = True
        
        while self.running is True:
            try:
                data = self._ZMQ_in.recv()
            except ZMQ_sub_timeout:
                continue
            self.inputData(data)


    def stop(self):
        self.running = False


    '''Overload with custom data wrapping/mangling here.'''
    def inputData(self, data):
        pass


    def outputData(self, data):
        self._ZMQ_pub.send(data)
