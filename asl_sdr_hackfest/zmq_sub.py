import zmq
from zmq import Again as ZMQ_sub_timeout


class ZMQ_sub(object):
    def __init__(self, portIn):
        self._ipAddress = '127.0.0.1'
        self._portIn = portIn

        self._zmqContext = zmq.Context()
        self._socketIn = self._zmqContext.socket(zmq.SUB)
        self._socketIn.RCVTIMEO = 100        
        self._socketIn.connect('tcp://%s:%s' % (self._ipAddress,self._portIn))
        try:
            self._socketIn.setsockopt(zmq.SUBSCRIBE, '') # python2
        except TypeError:
            self._socketIn.setsockopt_string(zmq.SUBSCRIBE, '') # python3, if this throws an exception... give up...


    def recv(self):
        return self._socketIn.recv()
