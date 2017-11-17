#!/usr/bin/python


import iwlist
import time
import psutil
import struct


def pack_ap(ap):
    #s = struct.Struct()
    s = struct.pack('!b', int(ap['signal_level_dBm']))
    if ap['encryption'] is 'yes':
        s += struct.pack('!b', ((int(ap['channel']) & 0x0F) | 128))
    else:
        s += struct.pack('!b', ((int(ap['channel']) & 0x0F) | 0))
    s += struct.pack('!b', int(ap['signal_level_dBm']))
    s += struct.pack('!s', "".join(ap['mac'].split()))
    s += struct.pack('!s', ap['essid'])
    return s


INTERFACE='wlp2s0'

access_points = dict()
keys= ['essid', 'encryption', 'signal_level_dBm', 'channel']
keys_short = ['essid', 'encryption', 'channel']

new_stuff = dict()
#content = iwlist.scan(interface=INTERFACE)
#cells = iwlist.parse(content)

#while True:
#for a in range (1,5):
while True:
    new_stuff = list()
    content = iwlist.scan(interface=INTERFACE)
    cells = iwlist.parse(content)
    for c in cells:
        if c['mac'] not in access_points.keys():
            ap = dict()
            for k in keys:
                try:
                    ap[k] = str(c[k])
                    print(k, c[k])
                except KeyError:
                    pass
            ap['last_time'] = time.time()
            ap['mac'] = str(c['mac'])
            print("Mac = '" + ap['mac'] + "'")
            access_points[c['mac']] = ap
            new_stuff.append(pack_ap(ap))
            print
        else:
            #print(c['mac'] + " is in access_points.keys ")
            if (time.time()-access_points[c['mac']]['last_time']) > 30:
                print("Haven't heard from " + str(access_points[c['mac']]))
                print("in 30 seconds.  Removing.")
                del(access_points[c['mac']])
                continue
            for k in keys: #keys_short:
                access_points[c['mac']]['last_time'] = time.time()
                if access_points[c['mac']][k] != c[k]: #'mac']:#[k]:
                    access_points[c['mac']][k] = c[k]
                    new_stuff.append(pack_ap(access_points[c['mac']]))
                    #new_stuff[c['mac']] = access_points[c['mac']]
                    #print(c['mac'] + ' ' + k + 'changed')
                    #print('Old = ' + access_points[c['mac']][k])
                    #print('New = ' + c[k])#'mac'][k])
                    #print
    print("CYCLE COMPLETE")

    print("CPU use percentage = " + str(psutil.cpu_percent(interval=None)))
    print("Memory usage = " + str(psutil.virtual_memory().percent) + "%")
    print("Battery = " + str(psutil.sensors_battery().percent) + "%")
    print("Length of access_points as bytes = " + str(len(bytes(access_points))))
    print("Length of new_stuff as bytes = " + str(len(bytes(new_stuff))))
    time.sleep(1)

print
print("Number of access points= " + str(len(access_points.keys())))

print("Access_points keys:")
print(access_points.keys())
for k in access_points.keys(): #.keys():
    #print(type(k))
    print k
    print access_points[k]['signal_level_dBm']
    print access_points[k]

print
print("All access points:")
print(access_points)
#for ap in access_points:
#  print(ap['signal_level_dBm']) #'signal_level_dBm']) 
#  continue



