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
		r.csrc_count =	0
		r.csrc = 0

		# Fields the application will fill
		r.marker = False	

		# Fields the handler will fill
		if ssrc not in self.streams.keys():
			r.ssrc = self.new_tx_stream(p_type)
		else:
			r.ssrc = ssrc

		r.seq_num = self.streams[r.ssrc].get_seq_num()
		r.payload_type = self.streams[r.ssrc].payload_type
		r.set_timestamp = self.streams[r.ssrc].get_timestamp()
		#r.set_timestamp((struct.pack("!f", self.streams[r.ssrc].get_timestamp()))

		return r.to_bytearray()


	def rx(self, rtp_bytearray):
		r = RTP()
		r.from_bytearray(rtp_bytearray)
		if r.ssrc not in self.streams.keys():
			self.new_rx_stream(r.ssrc, r.payload_type)
		self.streams[r.ssrc].update(r.seq_num, r.timestamp)
		return r


	def new_tx_stream(self, p_type):
		new_ssrc = random.randint(1, self.INT32_MAX)
		if new_ssrc in self.streams.keys():
			self.new_tx_stream(ssrc, p_type)
		else:
			self.streams[new_ssrc] = Stream(new_ssrc, p_type, tx=True)
		return new_ssrc
		
	def new_rx_stream(self, ssrc, p_type):
		self.streams[ssrc] = Stream(ssrc, p_type, tx=False)

	def header_consume(self, data):
		rtp_header = self.rx(data[:RTP.HEADER_LENGTH])
		return (rtp_header, data[RTP.HEADER_LENGTH:])

class Stream(object):
	def __init__(self, ssrc, p_type, tx=False):
		self.ssrc = ssrc
		self.last_seq_num = 0
		self.last_timestamp = time.time()
		self.payload_type = RTP.PAYLOAD_TYPES[p_type]
		self.tx = tx

	'''	
	For tx side. Increments and returns seq number
	'''	
	def get_seq_num(self):
		self.last_seq_num += 1
		return self.last_seq_num

	'''	
	For tx side. Updates and returns timestamp
	'''	
	def get_timestamp(self):
		self.last_timestamp = time.time()
		return self.last_timestamp

	'''	
	For rx side.	Updates the last_seq_num and last_timestamp 
	for the stream
	'''	
	def update(self, seq_num, ts):
		self.last_seq_num = seq_num
		self.last_timestamp = ts 

