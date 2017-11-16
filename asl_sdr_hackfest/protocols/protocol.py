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
        elif isinstance(value, float):
            f = ''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!f', value))
            return "0b" + f
        #if (isinstance(value, str) and (length == 32)):
        elif isinstance(value, str):
            print("Packed str = ", ("0b" + ''.join('{0:08b}'.format(x, 'b') for x in bytearray(value))))
            return ("0b" + ''.join('{0:08b}'.format(x, 'b') for x in bytearray(value)))
        else:
            try:
                ret = ("0b" + bin(value).lstrip('-0b').zfill(length))
            except:
                value = int.from_bytes(value, byteorder='big', signed=False)
                ret = ("0b" + bin(value).lstrip('-0b').zfill(length))
            return ret

    def bin_to_uint(self, value):
        try:
            ret = BitArray(bin=value).uint
        except AttributeError: # FIXME: Bad hack for typing issue
            ret = BitArray(bin=bin(value)).uint
        return ret

    def bin_to_bool(self, value):
        return BitArray(bin=value).bool

    # Requires protocol to implement from_bitarray()
    def from_bytearray(self, byte_array):
        bit_array = BitArray(bytes=byte_array)
        self.from_bitarray(bit_array)

    # Requires protocol to implement to_bitarray()
    def to_bytearray(self):
        return bytearray(self.to_bitarray().bytes)


    '''Overload with method to calculate header content and self-update as necessary.'''
    def header_calculate_internal(self, payload):
        pass


    '''Returns the payload with new header on it.'''
    @classmethod
    def header_calculate(cls, payload):
        mycls = cls()
        mycls.header_calculate_internal(payload)
        return mycls


    '''Return QoS instance and remaining payload.'''
    @classmethod
    def header_consume(cls, data):
        mycls = cls()
        length = len(mycls.to_bytearray())
        mycls.from_bytearray(data[:length])
        return (mycls, data[length:])
