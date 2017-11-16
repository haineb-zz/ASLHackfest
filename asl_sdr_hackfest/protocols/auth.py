import Crypto.Util.Counter

from Crypto.Cipher import AES
from Crypto.Random import random
from Crypto.Hash import HMAC


class AuthLayer:
    def __init__(self, key, noncectr_size=16, mac_size=16):
        """
        :param key: secret key
        :type key:
        :param noncectr_size: number of bytes for the nonce and the ctr, should be 16 bytes to be secure with AES !!!!!
        :type noncectr_size: int
        """
        self.key = key

        self.noncectr_bits = noncectr_size * 8  # needs to be multiple of 8
        self.mac_size = mac_size

        nonce = random.getrandbits(self.noncectr_bits)
        # make sure ctr does not use more then the half of noncectr's bits
        self.ctr = Crypto.Util.Counter.new(self.noncectr_bits, initial_value=nonce)

    def ctr_encrypt(self, data):
        ctrbytes = self.ctr()
        ctrval = (16 - len(ctrbytes)) * b'\x00' + ctrbytes

        enc = AES.new(self.key, AES.MODE_CTR, counter=lambda: ctrval)

        return ctrbytes + enc.encrypt(data)

    def ctr_decrypt(self, data):
        if len(data) < self.noncectr_bits // 8:
            return None

        ctrbytes = data[:self.noncectr_bits // 8]

        ctrval = (16 - len(ctrbytes)) * b'\x00' + ctrbytes

        dec = AES.new(self.key, AES.MODE_CTR, counter=lambda: ctrval)
        return dec.decrypt(data[self.noncectr_bits // 8:])

    def mac_add(self, data):
        h = HMAC.new(self.key)
        h.update(data)
        return data + h.digest()[:self.mac_size]

    def mac_check(self, data):
        if len(data) < self.mac_size:
            return False

        h = HMAC.new(self.key)
        h.update(data[:-1 * self.mac_size])

        if h.digest()[:self.mac_size] == data[-1 * self.mac_size:]:
            return True

        return False

    def mac_check_and_remove(self, data):
        if len(data) < self.mac_size:
            return None
        if not self.mac_check(data):
            return None

        return data[:-1 * self.mac_size]

    def authenc_encrypt(self, data):
        e = self.ctr_encrypt(data)
        if not e:
            return None
        return self.mac_add(e)

    def authenc_decrypt(self, data):
        d = self.mac_check_and_remove(data)
        if not d:
            return None
        return self.ctr_decrypt(d)


def test():
    cls = AuthLayer(b' ' * 16, noncectr_size=16)
    for _ in range(25):
        e = cls.ctr_encrypt(b"TEST")
        print('e', e)
        print('d', cls.ctr_decrypt(e))

    cls = AuthLayer(b' ' * 16, noncectr_size=2)
    for _ in range(25):
        e = cls.ctr_encrypt(b"TEST")
        print('e', e)
        print('d', cls.ctr_decrypt(e))

    print("bad dec: ", cls.ctr_decrypt(b'\x00' * 25))

    m = cls.mac_add(b"TEST")
    print('m ', m, cls.mac_check(m))
    print('bad mac ', cls.mac_check(b'\x00' * 25))

    cls = AuthLayer(b' ' * 16, noncectr_size=4, mac_size=4)
    for _ in range(25):
        e = cls.authenc_encrypt(b"TEST")
        print('e', e)
        print('d', cls.authenc_decrypt(e))

    print("bad auth dec: ", cls.authenc_decrypt(b'\x00' * 25))


if __name__ == "__main__":
    test()
