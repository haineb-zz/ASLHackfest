#!/usr/bin/env python

import gcs2uav
import uav2gcs
import signal



class Runner(object):
    def run(self):
        signal.signal(signal.SIGINT, self.terminate)
        
        self.gateways = {}
        self.gateways['GCS2UAV'] = gcs2uav.GCS2UAV(portIn = 6128, portOut = 6129)
        self.gateways['UAV2GCS'] = uav2gcs.UAV2GCS(portIn = 6130, portOut = 6131)

        for gw in self.gateways:
            self.gateways[gw].start()

        signal.pause()


    def terminate(self, signal, frame):
        for gw in self.gateways:
            self.gateways[gw].running = False

        for gw in self.gateways:
            self.gateways[gw].join()



if __name__ == "__main__":
    runner = Runner()
    runner.run()
