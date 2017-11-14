import gateway
import qos



class UAVtx(gateway.Gateway):
    def codeData(self, data):
        cls = qos.QoS.header_calculate(data)
        data = cls.to_bytearray() + data
        return data


class GCSrx(gateway.Gateway):
    def codeData(self, data):
        cls, data = qos.QoS.header_consume(data)
        return data
