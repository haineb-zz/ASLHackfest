import gateway
import qos

from network_layer_handler import NetworkLayerReceiveHandler, NetworkLayerTransmitHandler
from rtp_handler import RTP_Handler



class TX_gateway(gateway.Gateway):
    def __init__(self, *args, **kwargs):
        self.frame_tx = NetworkLayerTransmitHandler(output_data_func = self.outputData)
        gateway.Gateway.__init__(self, *args, **kwargs)
        self.rtp_handler = RTP_Handler()


    def run(self):
        self.frame_tx.start()
        gateway.Gateway.run(self)


    def stop(self):
        self.frame_tx.stop()
        gateway.Gateway.stop(self)


    def inputData(self, data):
        rtp_header = self.rtp_handler.tx()
        data = rtp_header + data
        cls = qos.QoS.header_calculate(data)
        data = cls.to_bytearray() + data
        self.frame_tx.ingest_data(data)



class RX_gateway(gateway.Gateway):
    def __init__(self, *args, **kwargs):
        self.frame_rx = NetworkLayerReceiveHandler(output_data_func = self.outputData_internal)
        gateway.Gateway.__init__(self, *args, **kwargs)


    def run(self):
        self.frame_rx.start()
        gateway.Gateway.run(self)


    def stop(self):
        self.frame_rx.stop()
        gateway.Gateway.stop(self)


    def inputData(self, data):
        self.frame_rx.ingest_data(data)


    def outputData_internal(self, data):
        cls, data = qos.QoS.header_consume(data)
        rtp_header, data = self.rtp_handler.header_consume(data)
        self.outputData(data)

