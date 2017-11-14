#!/usr/bin/env python3

import gcs2uav
import uav2gcs
import signal



class Runner(object):
    def run(self):
        signal.signal(signal.SIGINT, self.terminate)
        
        self.gateways = {}
        self.gateways['GCStx'] = gcs2uav.GCStx(portIn = 6128, portOut = 6132)
        self.gateways['UAVrx'] = gcs2uav.UAVrx(portIn = 6132, portOut = 6129)
        self.gateways['UAVtx'] = uav2gcs.UAVtx(portIn = 6130, portOut = 6133)
        self.gateways['GCSrx'] = uav2gcs.GCSrx(portIn = 6133, portOut = 6131)

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
