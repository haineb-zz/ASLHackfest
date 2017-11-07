import zmq
import threading



class Gateway(threading.Thread, object):
    def __init__(self, portIn, portOut):
        self.running = False

        self._ipAddress = '127.0.0.1'
        self._portIn = portIn
        self._portOut = portOut

        self._zmqContext = zmq.Context()
        self._socketIn = None
        self._socketOut = None

        threading.Thread.__init__(self)

        
    def run(self):
        self.running = True
        
        self._socketIn = self._zmqContext.socket(zmq.SUB)
        self._socketIn.setsockopt(zmq.SUBSCRIBE,'')
        self._socketIn.RCVTIMEO = 100        
        self._socketIn.connect('tcp://%s:%s' % (self._ipAddress, self._portIn))
        
        self._socketOut = self._zmqContext.socket(zmq.PUB)
        self._socketOut.connect('tcp://%s:%s' % (self._ipAddress, self._portOut))

        while self.running is True:
            try:
                data = self._socketIn.recv()
            except zmq.Again:
                continue
            self._socketOut.send(self.codeData(data))


    def stop(self):
        self.running = False


    '''Overload with custom data wrapping/mangling here.'''
    def codeData(self, data):
        print(data)
        return data
