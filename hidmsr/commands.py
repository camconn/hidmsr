#!/usr/bin/env python3
''' Interface for the the MSR605X magnetic card reader.

This file defines an interface as well as utility functions to read and
interact with the MSR605X HID-based reader.

Licensed under the GNU Public License, version 3 or later.

Copyright (c) 2018 Cameron Conn
'''


import ctypes
import sys
import time

import pywinusb.hid as hid

output = sys.stdout

def _extend_command(command: list, length=64):
    """ Extend a command until it fills out the specified number of bytes. """
    remaining = [0x00] * (length - len(command))
    result = [*command, *remaining]
    return result

RESET_COMMAND = _extend_command([0xC2, 0x1B, 0x61, 0x44, 0xF8, 0x19])
READ_COMMAND = _extend_command([0xC5, 0x1B, 0x6D])
VERS_COMMAND = _extend_command([0xC5, 0x1B, 0x76])

def create_report_data(interface: int, data: list, length=0):
    """ Create a report to send from a hex dump.

    Arguments
    =========
        interface : int - The interface to send the report to.
        data : list - The data to have in the report. This should be a string
            of `int`s.
        length: int - The length of the report to create (default 0). If zero,
            it will default to the length of the data string, plus one.

    Returns
    =======
        A ctype array of `c_ubyte`s.
    """

    if length <= 0:
        length = len(data) + 1
    elif length < (len(data) + 1):
        raise ValueError('The length must be longer than the data!')

    report = [interface, *data]
    buf = (ctypes.c_ubyte * length)(*report)
    return buf

def decode_hex(data):
    """ Decode an array of hexadecimal strings into a list of integers. """
    return [int(c, 16) for c in data]

def _sample_handler(data):
    if len(data) > 1:  # Strip off the first char if we have data longer than 1 byte
        data = data[1:]

    hex_str = ['{:02X}'.format(c) for c in data]
    raw_str = ''.join(['{:c}'.format(c) for c in data])
    out = ' '.join(hex_str)
    print('Hex data: ({} bytes)'.format(len(data)), end=' ')
    print('({})'.format(raw_str))
    print(out)

if __name__ == "__main__":
    filter = hid.HidDeviceFilter(vendor_id = 0x0801, product_id = 0x0003)

    all_devices = filter.get_devices()
    if len(all_devices) == 0:
        print("Found no matching devices. Exiting...")
        sys.exit(1)

    device = all_devices[0]
    device.open()
    print(device)

    device.set_raw_data_handler(_sample_handler)

    report1 = create_report_data(0x00, RESET_COMMAND)
    device.send_feature_report(report1)
    print('Sent report #1')
    time.sleep(1)

    report_v = create_report_data(0x00, VERS_COMMAND)
    device.send_feature_report(report_v)
    print('Sent version command #2')
    time.sleep(1)

    report3 = create_report_data(0x00, READ_COMMAND)
    device.send_feature_report(report3)
    print('Sent read command #3')
    time.sleep(10)

    report4 = create_report_data(0x00, RESET_COMMAND)
    device.send_feature_report(report4)
    print('Sent reset command #4')
    time.sleep(3)

    print("Closing device handle and exiting.")
    device.close()

