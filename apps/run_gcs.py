#!/usr/bin/env python3

from asl_sdr_hackfest.txrx_gateways import TX_gateway, RX_gateway
import signal



class Runner(object):
    def run(self):
        signal.signal(signal.SIGINT, self.terminate)
        
        self.gateways = {}
        self.gateways['GCStx'] = TX_gateway(portIn = 6128, portOut = 6132)
        self.gateways['GCSrx'] = RX_gateway(portIn = 6133, portOut = 6131)

        for gw in self.gateways:
            self.gateways[gw].start()

        signal.pause()


    def terminate(self, signal, frame):
        for gw in self.gateways:
            self.gateways[gw].stop()

        for gw in self.gateways:
            self.gateways[gw].join()



if __name__ == "__main__":
    runner = Runner()
    runner.run()
