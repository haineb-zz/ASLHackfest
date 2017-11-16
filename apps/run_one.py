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
            'service': Service(inPort = 6128, outPort = 6129),
            'type': 'radio',
            'config': None,
        }
        services['radio'] = radio

        mavlink_config = {
            'qos': 0,
            'ssrc': 0,
        }
        mavlink = {
            'service': Service(inPort = 5056, outPort = 5057),
            'type': 'client',
            'config': mavlink_config,
        }
        services['mavlink'] = mavlink

        cats_config = {
            'qos': 15,
            'ssrc': 1,
        }
        cats = {
            'service': Service(inPort = 5058, outPort = 5059),
            'type': 'client',
            'config': cats_config,
        }
        services['cats'] = cats
        self.posts.append(Postmaster(services_config = services))

        for post in self.posts:
            post.start()

        signal.pause()


    def terminate(self, signal, frame):
        for post in self.posts:
            post.stop()
        for post in self.posts:
            post.join()



if __name__ == "__main__":
    runner = Runner()
    runner.run()
