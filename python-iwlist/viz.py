#!/usr/bin/python

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
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
        self.channels_list = list()
        for i in range(0,11):
            self.channels_list.append(list())

        self.channel1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.aps_in_channel = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.channels_list[0] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.channels_list[1] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.channels_list[2] = [x * 2 for x in self.channel1]
        self.channel1 = [x * 3 for x in self.channel1]
        self.channel4 = [x * 4 for x in self.channel1]
        self.channel5 = [x * 5 for x in self.channel1]
        self.channel6 = [x * 6 for x in self.channel1]
        self.channel7 = [x * 7 for x in self.channel1]
        self.channel8 = [x * 8 for x in self.channel1]
        self.channel9 = [x * 9 for x in self.channel1]
        self.channel10 = [x * 10 for x in self.channel1]
        self.channel11 = [x * 2.5 for x in self.channel1]
        self.strength = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 25]
        self.width= 0.2
        N=11
        self.ind = np.arange(N)
        print("Viz init")


    def update_ap(self, ap):
        self.access_points[ap.mac] = ap


    def run(self):
        plt.ion()  # Turns on interactive mode
        fig = plt.figure()
        fig, axarr = plt.subplots(ncols=11, sharey=True)
        prop = plt.rcParams['axes.prop_cycle']
        for c in range(0,11):
            axarr[c].xaxis.set_major_locator(ticker.NullLocator())
            axarr[c].tick_params(length=0)
            axarr[c].set_xlabel((str(c+1)))
            [axarr[c].bar(param[0],param[1],color=param[2]['color']) for param in zip(self.aps_in_channel, self.strength, prop)]
            

        axarr[0].set_ylim([0, 100])
        axarr[0].yaxis.set_major_formatter(ticker.FixedLocator([0, 1, 2, 3, 4, 5]))
        axarr[0].yaxis.set_major_formatter(ticker.FixedFormatter(['', '-80', '-60', '-40', '-20', '0']))

        axarr[0].set_ylabel('dBm', horizontalalignment='left')


        plt.subplots_adjust(bottom=0.2, top=0.9, left=0.1, right=0.9, wspace=0.0)

        while True:
            first = self.strength[0]
            for v in range(0,len(self.strength)):
                try:
                    self.strength[v] = self.strength[v+1]
                except IndexError:
                    self.strength[v] = first
            for ax in axarr:
                ax.clear()
                [ax.bar(param[0],param[1],color=param[2]['color']) for param in zip(self.aps_in_channel, self.strength, prop)]

            plt.pause(1)
            print("Strength[0] = " + str(self.strength[0]))


if __name__ == "__main__":
    print("Start Viz script")
    v = Viz()
    print("Made v")
    v.run()
    print("Ran v")
