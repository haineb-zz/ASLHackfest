#!/usr/bin/python


import iwlist
import time
import psutil
import pmt
import struct
#import zmq

ZMQ_IP = '127.0.0.1'
ZMQ_PORT = 5058

zmq_context = zmq.Context()
socketOut = zmq_context.socket(zmq.PUB)
socketOut.bind('tcp://%s:%s' % (ZMQ_IP, ZMQ_PORT))


def scanner_send(data):
    #car = pmt.make_dict()
    #data = bytes(data)
    #cdr = pmt.to_pmt(data)
    #pdu = pmt.cons(car, cdr)
    #socketOut.send(pmt.serialize_str(pdu))
    socketOut.send(data)

def pack_ap(ap):
    #s = struct.Struct()
    s = struct.pack('!bb12s',
                    int(ap['signal_level_dBm']),
                    (int(ap['channel']) & 0x0F) | (128 if ap['encryption'] is 'yes' else 0),
                    "".join(ap['mac'].split(':')),
                    )

    s += ap['essid'] + b'\0' # null terminate the string
    print('s', s)

    return s


INTERFACE='wlp3s0b1'#'wlp2s0'

access_points = dict()
keys= ['essid', 'encryption', 'signal_level_dBm', 'channel']
keys_short = ['essid', 'encryption', 'channel']

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

    bytearr = bytearray()
    for val in new_stuff:
        bytearr += val

    scanner_send(bytearr)
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



