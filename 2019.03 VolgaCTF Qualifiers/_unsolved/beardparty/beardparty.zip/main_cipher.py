import numpy as np
from sboxes_mod import S
from basis_map import *
import os


def m(x):
    ret = np.array([0, 0, 0, 0])
    for i in range(4):
        null = [0, 0, 0, 0]
        for j in range(10):
            if x[i] & (2 ** j):
                null[i] = 2 ** j
                ret ^= bmap(null)
    return ret


def invm(x):
    ret = np.array([0, 0, 0, 0])
    for i in range(4):
        null = [0, 0, 0, 0]
        for j in range(10):
            if x[i] & (2 ** j):
                null[i] = 2 ** j
                ret ^= invbmap(null)
    return ret


class Cipher(object):
    def __init__(self, master_key):
        self.key = [int(i.encode('hex'), 16) for i in master_key]

    @staticmethod
    def _convert_text(text):
        string = ''
        ret = []
        for i in text:
            string += bin(int(i.encode('hex'), 16))[2:].zfill(8)
        for i in range(0, len(string), 10):
            ret.append(int(string[i:i+10], 2))

        return ret

    @staticmethod
    def _convert_array(array):
        string = ''
        ret = ''
        for i in array:
            string += bin(i)[2:].zfill(10)
        for i in range(0, len(string), 8):
            ret += hex(int(string[i:i+8], 2))[2:].zfill(2).decode('hex')

        return ret

    def test_convert(self):
        text = 'yergfyurefvfergthjyjyt'
        a = self._convert_text(text)
        b = self._convert_array(a)
        print b

    def _expand_key(self):
        k = np.array(self.key)  # [k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11]
        for i in range(7):
            x = m([k[12 * i + 8], k[12 * i + 9], k[12 * i + 10], k[12 * i + 11]])
            x = [S[0][x[0]], S[1][x[1]], S[2][x[2]], S[3][x[3]]]
            x = [x[0] ^ pow(3, i, 2 ** 10), x[1], x[2], x[3]]
            k12_15 = np.array([k[12 * i + 0], k[12 * i + 1], k[12 * i + 2], k[12 * i + 3]]) ^ np.array(x)
            k16_19 = np.array([k[12 * i + 4], k[12 * i + 5], k[12 * i + 6], k[12 * i + 7]]) ^ k12_15
            k20_23 = np.array([k[12 * i + 8], k[12 * i + 9], k[12 * i + 10], k[12 * i + 11]]) ^ k16_19
            k = np.concatenate((k, k12_15, k16_19, k20_23))

        ret_k = []
        for r in range(12):
            kr = np.array([], dtype=int)
            for i in range(8):
                kr = np.concatenate((kr, np.array([k[8 * r + i]])))
            ret_k.append(kr)

        return ret_k

    def _encrypt(self, p):
        k = self._expand_key()
        x = np.array(p)
        for r in range(10):
            x = x ^ k[r]
            for i in range(8):
                x[i] = S[i % 4][x[i]]
            x = np.array([x[0], x[5], x[2], x[7], x[4], x[1], x[6], x[3]])
            x = np.concatenate((m(x[0:4]), m(x[4:])))
        x = x ^ k[10]
        for i in range(8):
            x[i] = S[i % 4][x[i]]
        x = np.array([x[0], x[5], x[2], x[7], x[4], x[1], x[6], x[3]])
        x = x ^ k[11]

        return x

    def _decrypt(self, c):
        k = self._expand_key()
        x = np.array(c)
        x = x ^ k[11]
        x = np.array([x[0], x[5], x[2], x[7], x[4], x[1], x[6], x[3]])
        for i in range(8):
            x[i] = S[i % 4].index(x[i])
        x = x ^ k[10]
        for r in range(9, -1, -1):
            x = np.concatenate((invm(x[0:4]), invm(x[4:])))
            x = np.array([x[0], x[5], x[2], x[7], x[4], x[1], x[6], x[3]])
            for i in range(8):
                x[i] = S[i % 4].index(x[i])
            x = x ^ k[r]

        return x

    def encrypt(self, plaintext):
        ciphertext = np.array([], dtype=int)
        padding = 10 - len(plaintext) % 10
        plaintext = plaintext + hex(padding)[2:].replace('L', '').zfill(2).decode('hex') * padding
        plaintext = self._convert_text(plaintext)
        for i in range(0, len(plaintext), 8):
            ciphertext = np.concatenate((ciphertext, self._encrypt(plaintext[i:i+8])))

        return self._convert_array(ciphertext).encode('base64')

    def decrypt(self, ciphertext):
        plaintext = np.array([], dtype=int)
        ciphertext = self._convert_text(ciphertext.decode('base64'))
        for i in range(0, len(ciphertext), 8):
            plaintext = np.concatenate((plaintext, self._decrypt(ciphertext[i:i+8])))
        plaintext = self._convert_array(plaintext)
        padding = int(plaintext[-1].encode('hex'), 16)
        plaintext = plaintext[:-padding]

        return plaintext


if __name__ == '__main__':
    key = "\x34\x23\x2b\x4a\x45\xb5\x12\xc3\x34\x45\x76\xd7"
    cipher = Cipher(key)

    for i in range(100000):
        print i
        length = int(os.urandom(1).encode('hex'), 16)
        plaintext = os.urandom(length)
        try:
            assert cipher.decrypt(cipher.encrypt(plaintext)) == plaintext
        except Exception as ex:
            print ex
            print plaintext.encode('hex')
            print cipher.decrypt(cipher.encrypt(plaintext)).encode('hex')
