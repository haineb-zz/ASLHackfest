#!/usr/bin/env python3

import signal

from asl_sdr_hackfest.service import Service
from asl_sdr_hackfest.postmaster import Postmaster



class Runner(object):
    def run(self):
        signal.signal(signal.SIGINT, self.terminate)

        self.posts = []

        services = {}
        radio = {
            'service': Service(portIn = 6126, portOut = 6127),
            'type': 'radio',
            'config': None,
        }
        services['radio'] = radio

        mavlink_config = {
            'qos': 0,
            'ssrc': 0,
        }
        mavlink = {
            'service': Service(portIn = 6128, portOut = 6131),
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
        self.posts.append(Postmaster(services_config = services))

        services = {}
        radio = {
            'service': Service(portIn = 6127, portOut = 6126),
            'type': 'radio',
            'config': None,
        }
        services['radio'] = radio

        mavlink_config = {
            'qos': 0,
            'ssrc': 0,
        }
        mavlink = {
            'service': Service(portIn = 6130, portOut = 6129),
            'type': 'client',
            'config': mavlink_config,
        }
        services['mavlink'] = mavlink

        cats_config = {
            'qos': 15,
            'ssrc': 1,
        }
        cats = {
            'service': Service(portIn = 5158, portOut = 5159),
            'type': 'client',
            'config': cats_config,
        }
        services['cats'] = cats
        self.posts.append(Postmaster(services_config = services))

        for post in self.posts:
            post.start()

        print('Postmasters initializing. Ctrl-C to stop.')
        signal.pause()


    def terminate(self, signal, frame):
        print('Terminating...')
        for post in self.posts:
            post.stop()
        for post in self.posts:
            post.join()



if __name__ == "__main__":
    runner = Runner()
    runner.run()
