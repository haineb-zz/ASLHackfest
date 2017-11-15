#!/usr/bin/env python3
import asl_sdr_hackfest.protocols.qos as qos



datain = b'\x61\x61\x62'

cls, payload = qos.QoS.header_consume(datain)
print(cls)
print('Payload:')
print(payload)

payload = b'\x61\x61'

cls = qos.QoS.header_calculate(payload)
print(cls.to_bytearray() + payload)
