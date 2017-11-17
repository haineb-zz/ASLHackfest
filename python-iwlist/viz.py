#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
import time


class Access_Point(object):
    def __init__(self, mac, essid, channel, encryption, sig_level):
        self.mac = mac
        self.essid = essid
        self.channel = channel
        self.encryption = encryption
        self.sig_level = sig_level

class Viz(object):
    def __init__(self):
        self.access_points = dict()


    def update_ap(self, ap):
        self.access_points[ap.mac] = ap


    def run(self):
        N = len(access_points)
        fig, ax = plt.subplots(ncols=11)
        plt.bar()
