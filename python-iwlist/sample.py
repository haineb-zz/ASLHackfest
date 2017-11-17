#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
import time

class access_point(object):
    def __init__(self, mac, essid, channel, encryption, sig_level):
        self.mac = mac
        self.essid = essid
        self.channel = channel
        self.encryption = encryption
        self.sig_level = sig_level


access_points = ()
ap1 = access_point('abc', 'nasawifi', 11, True, 10)
ap2 = access_point('abc', 'nasawifi', 11, True, 33)
ap3 = access_point('abc', 'nasawifi', 11, True, 25)
ap4 = access_point('abc', 'nasawifi', 11, True, 24)
ap5 = access_point('abc', 'nasawifi', 11, True, 40)
access_points = access_points + (ap1,)
access_points = access_points + (ap2,)
access_points = access_points + (ap3,)
access_points = access_points + (ap4,)
access_points = access_points + (ap5,)
print("Access_points length = " + str(len(access_points)))

N=5
mens_means = (20,35, 30, 35, 27)
men_std = (2,3,4,1,2)

ind = np.arange(N) # the x locations for the groups
width = 0.35

fig, ax = plt.subplots()
rects1 = ax.bar(ind, mens_means, width, color='r', yerr=men_std)

women_means = (25, 32, 34, 20, 25)
women_std = (3, 5, 2, 3, 3)

ap_sig_levels = (20,35, 30, 35, 27)
for a in access_points:

#other_means = (32, 61, 20, 25, 12)

rects2 = ax.bar(ind + width, women_means, width, color='y', yerr=women_std)

rects3 = ax.bar(ind + width + width, ap_means, width, color='b', yerr=women_std)

ax.set_ylabel('dBs')
ax.set_title('Scores by group and gender')
ax.set_xticks(ind + width / 2)
ax.set_xticklabels(('1','2', '3', '4', '5', '6', '7', '8', '9', '10', '11'))

ax.legend((rects1[0], rects2[0]), ('Men', 'Women'))

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height),
                ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

plt.show()

time.sleep(3)
women_means = (30, 37, 34, 29, 37)

'''
This is for formating the ticks on the x axis
https://stackoverflow.com/questions/17158382/centering-x-tick-labels-between-tick-marks-in-matplotlib
'''
import matplotlib.ticker as ticker

# a is an axes object, e.g. from figure.get_axes()

# Hide major tick labels
a.xaxis.set_major_formatter(ticker.NullFormatter())

# Customize minor tick labels
a.xaxis.set_minor_locator(ticker.FixedLocator([1.5,2.5,3.5,4.5,5.5]))
a.xaxis.set_minor_formatter(ticker.FixedFormatter(['1','2','3','4','5']))
