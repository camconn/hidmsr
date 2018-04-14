#!/usr/bin/env python3
''' Convert raw magnetic stripe (magstripe) data to text.

This library converts bits of magnetic stripe tracks to human-readable
text. The rest of the parsing (e.g. determining account numbers)
is your problem, not mine.

Licensed under the GNU Public License, version 3 or later.

Copyright (c) 2018 Cameron Conn
'''


import argparse
import binascii
import math
import sys


SIXDEC_CHARS = """ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_"""
ABA_CHARS = """0123456789:;<=>?"""

def hex_to_bin(str_hex: str):
    ''' Convert a hexadecimal string to a binary within a string. '''
    total = ''.join(map(lambda ch: '{:04b}'.format(int(ch, 16)), str_hex))
    return total

def decode_sixdec(bin_str: str):
    ''' Decode a binary string encoded in SIXDEC. '''
    chars = len(bin_str) // 7
    output = ''
    for i in range(0, chars*7, 7):
        substr = bin_str[i:i+7]
        parity = substr[-1]  # Discard for now
        bin_val = substr[:6]
        parity_num = sum(map(lambda x: 1 if x == '1' else 0, bin_val))

        if parity_num % 2 == 0:
            if parity != '1':
                print('invalid parity! {}:{}'.format(bin_val, parity))
        elif parity != '0':
                print('invalid parity! {}:{}'.format(bin_val, parity))

        h = hex(int(bin_val[::-1], 2))
        ch = SIXDEC_CHARS[eval(h)]
        output += ch

    # XXX: We are probably stripping off the LRC here, but I'm too lazy to check.
    return output[:-1]  # Strip last character to avoid garbage

def decode_aba(bin_str: str):
    ''' Decode a binary string encoded in ABA. '''
    chars = len(bin_str) // 5
    output = ''
    for i in range(0, chars*5, 5):
        substr = bin_str[i:i+5]
        parity = substr[-1]  # Discard for now
        bin_val = substr[:4]
        parity_num = sum(map(lambda x: 1 if x == '1' else 0, bin_val))

        if parity_num % 2 == 0:
            if parity != '1':
                print('invalid parity! {}:{}'.format(bin_val, parity))
        elif parity != '0':
                print('invalid parity! {}:{}'.format(bin_val, parity))

        h = hex(int(bin_val[::-1], 2))
        ch = ABA_CHARS[eval(h)]
        output += ch

    # XXX: We are probably stripping off the LRC here, but I'm too lazy to check.
    return output[:-1]  # Strip last character to avoid garbage

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert magnetic stripe data formats.')
    parser.add_argument('track', type=str, nargs='+')
    parsed = parser.parse_args()

    tracks = parsed.track
    if tracks == None:
        print('Please provide data to convert')
        sys.exit(1)

    for i, t in enumerate(tracks):
        decoded_binary = hex_to_bin(t)

        if i == 0 or i == 2:  # Track 1, 3
            result = decode_sixdec(decoded_binary)
        elif i == 1:  # Track 2
            result = decode_aba(decoded_binary)
        print(result)
