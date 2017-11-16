import threading

from asl_sdr_hackfest.service import Service

from asl_sdr_hackfest.protocols.network_layer_handler import NetworkLayerReceiveHandler, NetworkLayerTransmitHandler
from asl_sdr_hackfest.protocols.rtp_handler import RTP_Handler
from asl_sdr_hackfest.protocols.qos import QoS



class Postmaster(threading.Thread, object):
    def __init__(self, services_config):
        self.running = False
        
        self.services = services_config

        '''
        # Sample service config:
        # 'radio' is mandatory
        services = {}
        radio = {
            'service': Service(portIn = 6128, portOut = 6129),
            'type': 'radio',
            'config': None,
        }
        services['radio'] = radio

        mavlink_config = {
            'qos': 0,
            'ssrc': 0,
        }
        mavlink = {
            'service': Service(portIn = 5056, portOut = 5057),
            'type': 'client',
            'config': mavlink_config,
        }
        services['mavlink'] = mavlink

        cats_config = {
            'qos': 15,
            'ssrc': 1,
        }
        cats = {
            'service': Service(portIn = 5058, portOut = 5059),
            'type': 'client',
            'config': cats_config,
        }
        services['cats'] = cats
        '''

        self.frame_rx = NetworkLayerReceiveHandler(output_data_func = self.frameDeframed)
        self.frame_tx = NetworkLayerTransmitHandler(output_data_func = self.services['radio']['service'].outputData)

        self.rtp_handler_rx = RTP_Handler()
        self.rtp_handler_tx = RTP_Handler()

        threading.Thread.__init__(self)


    def run(self):
        self.running = True

        for srv in self.services:
            self.services[srv]['service'].start()

        self.frame_rx.start()
        self.frame_tx.start()

        while self.running is True:
            for srv in self.services:
                srv = self.services[srv]
                data = srv['service'].readData()
                if data is None:
                    continue
                if srv['type'] == 'radio':
                    self.frame_rx.ingest_data(data)
                elif srv['type'] == 'client':
                    rtp_header = self.rtp_handler_tx.tx(srv['config']['ssrc'], 'gsm') # This is a byte array, not a header class
                    data = rtp_header + data
                    qos_header = QoS.header_calculate(data) # This is a header class, not a byte array
                    qos_header.set_priority_code(srv['config']['qos'])
                    data = qos_header.to_bytearray() + data
                    self.frame_tx.ingest_data(data)


    def frameDeframed(self, data):
        cls, data = QoS.header_consume(data)

        rtp_header, data = self.rtp_handler_rx.header_consume(data)
        ssrc = rtp_header.get_ssrc()

        for srv in self.services:
            conf = self.services[srv]['config']
            if conf is not None and ssrc == conf['ssrc']:
                self.services[srv]['service'].outputData(data)


    def stop(self):
        self.running = False

        self.frame_rx.stop()
        self.frame_tx.stop()
        for srv in self.services:
            self.services[srv]['service'].stop()

        self.frame_rx.join()
        self.frame_tx.join()
        for srv in self.services:
            self.services[srv]['service'].join()
