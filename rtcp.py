#!/usr/bin/python

from bitstring import BitArray 

class RTCP(object):
	FALSE = '0b0'
	TRUE = '0b1'
	ZERO2 = '0b00'
	ONE2 = '0b01'
	TWO2 = '0b10'
	THREE2 = '0b11'
	
	def __init__(self, *args, **kwargs):
		self.version = kwargs.get('version')
		self.padding = kwargs.get('padding')
		self.count = kwargs.get('count')
		self.type = kwargs.get('type')
		self.length = kwargs.get('length')
		self.data = kwargs.get('data')

	def __str__(self):
		print("Printing out RTCP values")
		print(self.get_version())
		print(self.get_padding())
		print(self.get_count())
		print(self.get_type())
		print(self.get_length())
		print(self.get_data())
		print("Done")
		return ""

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
		ba.append(self.bin_formater(self.count, 5))
		ba.append(self.bin_formater(self.type, 8))
		ba.append(self.bin_formater(self.length, 16))
		# TODO Padding will be variable for data.  Get from value of length
		ba.append(self.bin_formater(self.data, 32))
		return ba

	# TODO Currently sets each field to a bitstring. 
	#      Should convert to actual values
	def from_bitarray(self, ba):
		bas = ba.bin
		self.set_version(bas[0:2])
		self.set_padding(bas[2:3])
		self.set_count(bas[3:8])
		self.set_type(bas[8:16])
		self.set_length(bas[16:32])
		self.set_data(bas[32:])

	# Getters

	def get_version(self):
		return self.version

	def get_padding(self):
		return self.padding

	def get_count(self):
		return self.count

	def get_type(self):
		return self.type

	def get_length(self):
		return self.length

	def get_data(self):
		return self.data

	# Setters

	def set_version(self, v):
		self.version = v

	def set_padding(self, p):
		self.padding = p

	def set_count(self, c):
		self.count = c 

	def set_type(self, t):
		self.type = t

	def set_length(self, l):
		self.length = l

	def set_data(self, d):
		self.data = d

