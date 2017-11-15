from asl_sdr_hackfest.gateway import Gateway
from asl_sdr_hackfest.protocols.qos import QoS

from asl_sdr_hackfest.protocols.network_layer_handler import NetworkLayerReceiveHandler, NetworkLayerTransmitHandler
from asl_sdr_hackfest.protocols.rtp_handler import RTP_Handler



class TX_gateway(Gateway):
    def __init__(self, *args, **kwargs):
        self.frame_tx = NetworkLayerTransmitHandler(output_data_func = self.outputData)
        Gateway.__init__(self, *args, **kwargs)
        self.rtp_handler = RTP_Handler()


    def run(self):
        self.frame_tx.start()
        Gateway.run(self)


    def stop(self):
        self.frame_tx.stop()
        Gateway.stop(self)


    def inputData(self, data):
        rtp_header = self.rtp_handler.tx(1, 'gsm')
        data = rtp_header + data
        cls = QoS.header_calculate(data)
        data = cls.to_bytearray() + data
        self.frame_tx.ingest_data(data)



class RX_gateway(Gateway):
    def __init__(self, *args, **kwargs):
        self.frame_rx = NetworkLayerReceiveHandler(output_data_func = self.outputData_internal)
        Gateway.__init__(self, *args, **kwargs)
        self.rtp_handler = RTP_Handler()


    def run(self):
        self.frame_rx.start()
        Gateway.run(self)


    def stop(self):
        self.frame_rx.stop()
        Gateway.stop(self)


    def inputData(self, data):
        self.frame_rx.ingest_data(data)


    def outputData_internal(self, data):
        cls, data = QoS.header_consume(data)
        rtp_header, data = self.rtp_handler.header_consume(data)
        self.outputData(data)
