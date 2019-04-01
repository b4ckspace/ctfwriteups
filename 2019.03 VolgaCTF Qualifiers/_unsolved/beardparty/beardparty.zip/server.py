#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from key_file import key
from main_cipher import Cipher


"""
    Cipher
"""

cipher = Cipher(key)


"""
    Communication utils
"""

def read_message():
    return sys.stdin.readline()


def send_message(message):
    sys.stdout.write('{0}\r\n'.format(message))
    sys.stdout.flush()


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


"""
    Main
"""


if __name__ == '__main__':
    try:
        while True:
            send_message('Enter your your data to encrypt (in base64 format):')
            message = read_message().strip().decode('base64')
            send_message(cipher.encrypt(message))

    except Exception as ex:
        send_message('Something must have gone very, very wrong...')
        eprint(str(ex))

    finally:
        pass