#! /usr/bin/python

from chaos_layer import *

class Chaos_layer_tester(object):
    def __init__(self, chaos_layer = Chaos_layer(), max_queue_size = 32):
        self.cl = chaos_layer
        self.bq = queue.Queue (max_queue_size)

    def bitFlips_test (self):
        print "bitFlips"
        ba = bitarray.bitarray(Frame.headerlength*8)
        ba.setall(0)
        Ba = to_bytearray(ba)

        self.cl.bitFlips(self.bq, Ba)
        Ba = self.bq.get()

        ba = to_bitarray(Ba)
        ## Note: This should print
        ## '1111111111001111111111111111111111111111111111111111111111111111'
        ## because Frame.qos field masks 0x0F
        print ba

    def genetic_test (self, passes = 42):
        print "genetics"
        ba = bitarray.bitarray(Frame.headerlength*8)
        print ba
        print self.cl.bits
        for n in range(passes):
            Ba = to_bytearray(ba)
            self.cl.genetic(self.bq, Ba)
            Ba = self.bq.get()
            print to_bitarray(Ba)

    def delayed_enqueue_test (self, delayed_enqueued_func, queue_max_size = 32):
        print "delayed enqueue"
        data_queue = self.bq
        Ba = bytearray("helloworld", "utf-8")
        threads = []
        for n in range(queue_max_size):
            threads.append(delayed_enqueued_func(data_queue, Ba))
        for thread in threads:
            thread.join()
        print data_queue.qsize()
        for n in range(data_queue.qsize()):
            data = data_queue.get_nowait()
            print ("%d: %s" % (n, data))

    def uniform_delayed_enqueue_test (self, queue_max_size = 32):
        self.delayed_enqueue_test(self.cl.delayed_enqueue, queue_max_size)

    def random_delayed_enqueue_test (self, queue_max_size = 32):
        self.delayed_enqueue_test(self.cl.random_delayed_enqueue, queue_max_size)

    def burst (self, queue_max_size = 32) :
        self.delayed_enqueue_test(self.cl.random_delayed_enqueue, queue_max_size)

if __name__ == "__main__":
    clt = Chaos_layer_tester()
    clt.bitFlips_test()
    clt.genetic_test()
    clt.burst()

    clt.cl.run(clt.bq, bytearray("helloworld", "utf-8"))
