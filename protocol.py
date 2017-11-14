#!/usr/bin/python

from bitstring import BitArray 
import struct

class Protocol(object):
	FALSE = '0b0'
	TRUE = '0b1'
	ZERO2 = '0b00'
	ONE2 = '0b01'
	TWO2 = '0b10'
	THREE2 = '0b11'

	def __init__(self, *args, **kwargs):
		self.version = kwargs.get('version')

	def __str__(self):
		return ""

	# TODO Do we need negatives? If so, this needs more testing.
	def bin_formater(self, value, length):
		if value is None:
			return ("0b" + bin(0).lstrip('-0b').zfill(length))
		else:
			return ("0b" + bin(value).lstrip('-0b').zfill(length))

	def bin_to_uint(self, value):
		return BitArray(bin=value).uint

	def bin_to_bool(self, value):
		return BitArray(bin=value).bool

	# Requires protocol to implement from_bitarray()
	def from_bytearray(self, byte_array):
		bit_array = BitArray(bytes=byte_array)
		self.from_bitarray(bit_array)

	# Requires protocol to implement to_bitarray()
	def to_bytearray(self):
		return self.to_bitarray().bytes

