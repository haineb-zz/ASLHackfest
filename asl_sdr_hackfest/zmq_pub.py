import zmq
import numpy, pmt



class ZMQ_pub(object):
    def __init__(self, portOut):
        self._ipAddress = '127.0.0.1'
        self._portOut = portOut

        self._zmqContext = zmq.Context()
        self._socketOut = self._zmqContext.socket(zmq.PUB)
        self._socketOut.bind('tcp://%s:%s' % (self._ipAddress, self._portOut))


    def send(self, data):
        car = pmt.make_dict()
        data = bytes(data)
        cdr = pmt.to_pmt(data)
        pdu = pmt.cons(car, cdr)
        self._socketOut.send(pmt.serialize_str(pdu))
