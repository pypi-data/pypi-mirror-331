import base64
from os import urandom
from Crypto.Cipher import AES
from Crypto import Random

class AESCipher(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key_length = 32
        self.key = self._padKey(key).encode('utf-8')[:self.key_length]

    def encrypt(self, raw):
        raw = str.encode(self._padPayload(raw))
        iv = Random.new().read(self.bs)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encoded = base64.b64encode(cipher.encrypt(raw)).decode()
        return base64.b64encode((encoded + "::" + base64.b64encode(iv).decode()).encode()).decode()

    def _padPayload(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _padKey(self, s):
        return s + (b"\0" * (self.key_length - len(s) % self.key_length)).decode()