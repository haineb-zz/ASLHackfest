#!/usr/bin/python

from asl_sdr_hackfest.service import *
import sys

class ServiceLoopback:
    def __init__(self, portA = 5786, portB = 6875):
        try:
            self.services = [Service(portA, portB), Service(portB, portA)]
        except:
            raise

    def run (self):
        while True:
            try:
                t = threading.Timer(0.25, self.services[0].outputData, {"data": "Hello"})
                t.start()
                t.join()
                # self.services[0].outputData ("Hello")
                print self.services[1].readData()
            except KeyboardInterrupt:
                for service in self.services:
                    service.stop()
                break
            except:
                print "No messages."
                continue


if __name__ == "__main__":
    slb = ServiceLoopback()
    slb.run()

    # BUG: This code works, but the above doesn't
    # s1 = Service(5786, 6875)
    # s2 = Service(6875, 5786)
    #
    # s1.start()
    # s2.start()
    #
    # while True:
    #     s1.outputData("Hello")
    #     try:
    #         print s2.readData()
    #     except KeyboardInterrupt:
    #         s1.stop()
    #         s2.stop()
    #         break
    #     except:
    #         print "exception!"
    #         continue
