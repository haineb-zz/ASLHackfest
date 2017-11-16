#!/usr/bin/python
import time
import random
import struct
from asl_sdr_hackfest.protocols.rtp import RTP


class RTP_Handler(object):
    def __init__(self):
        self.streams = dict()
        self.INT32_MAX = 2147483647

    def tx(self, ssrc, p_type):
        r = RTP()
        # Fields we're unlikely to use during the hackfest
        r.version = 2
        r.padding = False
        r.extension = False
        r.csrc_count =    0
        r.csrc = 0

        # Fields the application will fill
        r.marker = False    

        # Fields the handler will fill
        if ssrc not in self.streams.keys():
            r.ssrc = self.new_tx_stream(p_type, ssrc)
        #else:
        #    r.ssrc = ssrc
        r.ssrc = ssrc
        r.seq_num = self.streams[r.ssrc].get_seq_num()
        r.payload_type = self.streams[r.ssrc].payload_type
        r.timestamp = self.streams[r.ssrc].create_timestamp32()
        #r.set_timestamp((struct.pack("!f", self.streams[r.ssrc].get_timestamp()))

        return r.to_bytearray()


    def rx(self, rtp_bytearray):
        r = RTP()
        r.from_bytearray(rtp_bytearray)
        if r.ssrc not in self.streams.keys():
            self.new_rx_stream(r.ssrc, r.payload_type)
        self.streams[r.ssrc].update(r.seq_num, r.timestamp)
        return r


    def new_tx_stream(self, p_type, ssrc):
        self.streams[ssrc] = Stream(ssrc, p_type, tx=True)
        #new_ssrc = random.randint(1, self.INT32_MAX)
        #if new_ssrc in self.streams.keys():
        #    self.new_tx_stream(p_type)
        #else:
        #    self.streams[new_ssrc] = Stream(new_ssrc, p_type, tx=True)
        #return new_ssrc
        
    def new_rx_stream(self, ssrc, p_type):
        self.streams[ssrc] = Stream(ssrc, p_type, tx=False)

    def header_consume(self, data):
        rtp_header = self.rx(data[:RTP.HEADER_LENGTH])
        return (rtp_header, data[RTP.HEADER_LENGTH:])

class Stream(object):
    def __init__(self, ssrc, p_type, tx=False):
        self.ssrc = ssrc
        self.last_seq_num = 0
        self.last_timestamp = 10000 #self.create_timestamp32()
        if isinstance(p_type, int):
            self.payload_type = p_type
        else:
            self.payload_type = RTP.PAYLOAD_TYPES[p_type]
        self.tx = tx
        self.UINT16_MAX = 65535
        self.UINT32_MAX = 4294967295
        self.window_top = 20
        self.window_btm = 10
        self.time_win_top = 250
        self.time_win_btm = 100 

    '''    
    For tx side. Increments and returns seq number
    '''    
    def get_seq_num(self):
        self.last_seq_num += 1
        return self.last_seq_num

    '''    
    For tx side. Updates and returns timestamp
    '''    
    def create_timestamp32(self):
        t = (int(round(time.time()*1000)) & (2**32-1))
        self.last_timestamp = struct.pack('!L', t)
        return self.last_timestamp 

    def unpack_timestamp32(self, ts):
        new_ts = 0
        try:
            new_ts = ts.uint
            return new_ts
        except AttributeError:
            print("timestamp was not a BitArray")
            pass
        try:
            new_ts = struct.unpack('!L', ts)
            return new_ts
        except stuct.error:
            print("timestamp was not a valid struct")
            pass
        if isinstance(ts, int):
            print("timestamp was always an int")
            return ts
        print("Weird timestamp. Returning zero")
        return 0
        
    '''    
    For rx side.    Updates the last_seq_num and last_timestamp 
    for the stream
    '''    
    def update(self, seq_num, ts):
        if ((self.last_seq_num == 0) and (self.last_timestamp == 10000)):
            self.last_seq_num = seq_num
            self.last_timestamp = ts
            return
        if self.check_seq_num_window(seq_num):
            self.last_seq_num = seq_num
        else:
            print("Received invalid sequence number for this stream")
            print("May want to drop it.")
            #return
        if self.check_timestamp_window(ts):
            self.last_timestamp = ts
        elif (self.last_timestamp == 10000):
            print("Reinitialize stream ", self.ssrc)
            self.last_seq_num = seq_num
            self.last_timestamp = ts
        else:
            # Outside timestamp window
            print("Received invalid timestamp for this stream")
            print("May want to drop it.")
            #return

    def check_seq_num_window(self, seq_num):
        win_top = self.last_seq_num + self.window_top
        if (win_top < self.UINT16_MAX):
            if ( seq_num > (win_top)):
                print("Seq_num is too big")
                return False
            #if ( seq_num < (struct.unpack('H', struct.pack('h', (self.last_seq_num - self.window_btm)) )[0])):
            if ( seq_num < (self.last_seq_num - self.window_btm)):
                print("Seq_num is too small")
                return False
        else:
            if ( seq_num > (win_top - self.UINT16_MAX)):
                print("seq_num too big")
                return False
            if ( seq_num < (self.last_seq_num - self.window_btm)):
                print("Seq_num is too small")
                return False
        return True

    def check_timestamp_window(self, ts):
        time_top = self.unpack_timestamp32(self.last_timestamp) + self.time_win_top
        ts_in = self.unpack_timestamp32(ts)
        if (time_top < self.UINT32_MAX):
            if ( ts_in > (time_top)):
                print("Timestamp is too big")
                return True 
                #return False
            #if ( ts < (struct.unpack('L', struct.pack('L', (self.last_timestamp - self.time_win_btm)) ))):
            if ( ts_in < (self.unpack_timestamp32(self.last_timestamp) - self.time_win_btm)):
                print("Timestamp is too small")
                return False
        else:
            if ( ts_in > (time_top - self.UINT32_MAX)):
                print("Timestamp is too big")
                return True 
                #return False
            if ( ts_in < (self.unpack_timestamp32(self.last_timestamp) - self.time_win_btm)):
                print("Timestamp is too small")
                return False
        return True

