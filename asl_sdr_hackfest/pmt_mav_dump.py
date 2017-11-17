from pymavlink import mavutil
import pmt
import numpy

class PMT_MAV_dump(object):
    # NOTE: default arguments derived from MAVProxy's --master argument
    def __init__(self, ip = "127.0.0.1", remote_port = 5760, protocol = 'tcp'):
        print ('connecting to %s:%s:%d' % (protocol, ip, remote_port))
        self.mc = mavutil.mavlink_connection(device='%s:%s:%d' % (protocol, ip, remote_port), retries = 9000)

    # NOTE: have this method invert ZMQ_pub modules' send method
    def method(self, pmt_cons):
        s = pmt.deserialize_str(pmt_cons)

        if pmt.is_pair(s):
            car = pmt.car(s)
            cdr = pmt.to_python(pmt.cdr(s))
            cdr = numpy.getbuffer(cdr)

            meta = car
            data = self.mc.mav.decode(bytearray(cdr))

            # NOTE: to fully parse fields of message use this for reference:
            # https://www.samba.org/tridge/UAV/pymavlink/apidocs/classIndex.html
            return \
                "gr metadata: %s \
                message type: %s" % (meta, data.get_type())
