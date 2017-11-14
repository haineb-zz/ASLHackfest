import gateway
import qos



class GCStx(gateway.Gateway):
    def codeData(self, data):
        cls = qos.QoS.header_calculate(data)
        data = cls.to_bytearray() + data
        return data


class UAVrx(gateway.Gateway):
    def codeData(self, data):
        cls, data = qos.QoS.header_consume(data)
        return data
