import gateway
import qos



class UAV2GCS(gateway.Gateway):
    '''Overload with custom data wrapping/mangling here.'''
    def codeData(self, data):
        cls = qos.QoS.header_calculate(data)
        data = cls.to_bytearray() + data
        print(data) # PHY IS HERE!!!
        cls, data = qos.QoS.header_consume(data)
        return data
