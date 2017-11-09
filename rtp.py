#!/usr/bin/python

from bitstring import BitArray 

class RTP(object):
	FALSE = '0b0'
	TRUE = '0b1'
	ZERO2 = '0b00'
	ONE2 = '0b01'
	TWO2 = '0b10'
	THREE2 = '0b11'
	
	def __init__(self, *args, **kwargs):
		self.version = kwargs.get('version')
		self.padding = kwargs.get('padding')
		self.extension = kwargs.get('extension')
		self.csrc_count = kwargs.get('csrc_count')
		self.marker = kwargs.get('marker')
		self.payload_type = kwargs.get('payload_type')
		self.seq_num = kwargs.get('seq_num')
		self.timestamp = kwargs.get('timestamp')
		self.ssrc = kwargs.get('ssrc')
		self.csrc = kwargs.get('csrc')

	def str(self):
		print("Printing out RTP values")
		print(self.get_version())
		print(self.get_padding())
		print(self.get_extension())
		print(self.get_csrc_count())
		print(self.get_marker())
		print(self.get_payload_type())
		print(self.get_seq_num())
		print(self.get_timestamp())
		print(self.get_ssrc())
		print(self.get_csrc())
		print("Done")

	# TODO Do we need negatives? If so, this needs more testing.
	def bin_formater(self, value, length):
		if value is None:
			return ("0b" + bin(0).lstrip('-0b').zfill(length))
		else:
			return ("0b" + bin(value).lstrip('-0b').zfill(length))

	def to_bitarray(self):
		# Version is always 2
		ba = BitArray(self.TWO2)	
		ba.append(self.TRUE) if self.padding else ba.append(self.FALSE)
		ba.append(self.TRUE) if self.extension else ba.append(self.FALSE)
		ba.append(self.bin_formater(self.csrc_count, 4))
		ba.append(self.TRUE) if self.marker else ba.append(self.FALSE)
		ba.append(self.bin_formater(self.payload_type, 8))
		ba.append(self.bin_formater(self.seq_num, 16))
		ba.append(self.bin_formater(self.timestamp, 32))
		ba.append(self.bin_formater(self.ssrc, 32))
		ba.append(self.bin_formater(self.csrc, 32))
		return ba

	# TODO Currently sets each field to a bitstring. 
	#      Should convert to actual values
	def from_bitarray(self, ba):
		bas = ba.bin
		self.set_version(bas[0:2])
		self.set_padding(bas[2:3])
		self.set_extension(bas[3:4])
		self.set_csrc_count(bas[4:8])
		self.set_marker(bas[8:9])
		self.set_payload_type(bas[9:16])
		self.set_seq_num(bas[16:32])
		self.set_timestamp(bas[32:64])
		self.set_ssrc(bas[64:96])
		self.set_csrc(bas[96:128])

	# Getters

	def get_version(self):
		return self.version

	def get_padding(self):
		return self.padding

	def get_extension(self):
		return self.extension

	def get_csrc_count(self):
		return self.csrc_count

	def get_marker(self):
		return self.marker

	def get_payload_type(self):
		return self.payload_type

	def get_seq_num(self):
		return self.seq_num

	def get_timestamp(self):
		return self.timestamp

	def get_ssrc(self):
		return self.ssrc

	def get_csrc(self):
		return self.csrc

	# Setters

	def set_version(self, v):
		self.version = v

	def set_padding(self, p):
		self.padding = p

	def set_extension(self, e):
		self.extension = e 

	def set_csrc_count(self, cc):
		self.csrc_count = cc 

	def set_marker(self, m):
		self.marker = m

	def set_payload_type(self, pt):
		self.payload_type = pt

	def set_seq_num(self, sn):
		self.seq_num = sn

	def set_timestamp(self, t):
		self.timestamp = t

	def set_ssrc(self, ss):
		self.ssrc = ss

	def set_csrc(self, cs):
		self.csrc = cs

