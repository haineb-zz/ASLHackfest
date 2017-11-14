from bitstring import BitArray 
from protocol import Protocol



class QoS(Protocol):
        def __init__(self, *args, **kwargs):
                self.priority_code = kwargs.get('priority_code')

                
        def __str__(self):
                print("Printing out QoS values")
                print(self.get_priority_code())
                print("Done")
                return ""

        
        def to_bitarray(self):
                ba = BitArray(self.bin_formater(0, 4))
                ba.append(self.bin_formater(self.priority_code, 4))
                return ba


        def from_bitarray(self, ba):
                bas = ba.bin
                self.set_priority_code(bas[4:8])


        def get_priority_code(self):
                return self.priority_code


        def set_priority_code(self, pcp):
                self.priority_code = self.bin_to_uint(pcp)

                
        def header_calculate_internal(self, payload):
                self.set_priority_code(bin(0))
