from asl_sdr_hackfest.gateway import Gateway
from asl_sdr_hackfest.protocols.qos import QoS

from asl_sdr_hackfest.protocols.network_layer_handler import NetworkLayerReceiveHandler, NetworkLayerTransmitHandler



class TX_gateway(Gateway):
    def __init__(self, *args, **kwargs):
        self.frame_tx = NetworkLayerTransmitHandler(output_data_func = self.outputData)
        Gateway.__init__(self, *args, **kwargs)


    def run(self):
        self.frame_tx.start()
        Gateway.run(self)


    def stop(self):
        self.frame_tx.stop()
        Gateway.stop(self)


    def inputData(self, data):
        cls = qos.QoS.header_calculate(data)
        data = cls.to_bytearray() + data
        self.frame_tx.ingest_data(data)



class RX_gateway(Gateway):
    def __init__(self, *args, **kwargs):
        self.frame_rx = NetworkLayerReceiveHandler(output_data_func = self.outputData_internal)
        Gateway.__init__(self, *args, **kwargs)


    def run(self):
        self.frame_rx.start()
        Gateway.run(self)


    def stop(self):
        self.frame_rx.stop()
        Gateway.stop(self)


    def inputData(self, data):
        self.frame_rx.ingest_data(data)


    def outputData_internal(self, data):
        cls, data = qos.QoS.header_consume(data)
        self.outputData(data)
