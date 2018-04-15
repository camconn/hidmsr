""" Interface for the the MSR605X magnetic card reader.

This file defines an interface as well as utility functions to read and
interact with the MSR605X HID-based reader.

Licensed under the GNU Public License, version 3 or later.

Copyright (c) 2018 Cameron Conn
"""


import ctypes
import sys
import time

import pywinusb.hid as hid


def _extend_command(command: list, length=64):
    """ Extend a command until it fills out the specified number of bytes. """
    remaining = [0x00] * (length - len(command))
    result = [*command, *remaining]
    return result

def _create_report_data(interface: int, data: list, length=0):
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

def _decode_hex(data):
    """ Decode an array of hexadecimal strings into a list of integers. """
    return [int(c, 16) for c in data]


class MSRDevice():
    """ Represents a MSR HID-based Magnetic Card Reader/Writier device. """

    def __init__(self, vendor_id=0x0801, product_id=0x0003):
        self._vid = vendor_id
        self._pid = product_id

        filter = hid.HidDeviceFilter(vendor_id = vendor_id, product_id = product_id)

        all_devices = filter.get_devices()
        if len(all_devices) == 0:
            raise RuntimeError("No appropriate MSR device found! Please check your device is plugged in.")

        # Just assume we want the first device.
        device = all_devices[0]
        device.open()
        def _data_handler(data):
            if len(data) > 1:  # Strip off the first char if we have data longer than 1 byte
                data = data[1:]
            hex_str = ["{:02X}".format(c) for c in data]
            raw_str = "".join(["{:c}".format(c) for c in data])
            out = " ".join(hex_str)
            print("Hex data: ({} bytes)".format(len(data)), end=" ")
            print("({})".format(raw_str))
            print(out)

        device.set_raw_data_handler(_data_handler)
        self._dev = device

    def _send_command(self, command):
        """ Send a command to the MSR device. """
        report = _create_report_data(0x00, _extend_command(command))
        self._dev.send_feature_report(report)

    def get_version(self):
        """ Get the firmware version of this device. """
        self._send_command([0xC5, 0x1B, 0x76])

    def reset(self):
        """ Reset the device's state. """
        self._send_command([0xC2, 0x1B, 0x61, 0x44, 0xF8, 0x19])

    def raw_read(self):
        """ Read a card's raw data without any preprocessing. """
        self._send_command([0xC5, 0x1B, 0x6D])

    def read(self):
        """ Read ISO data from a card. """
        self._send_command([0xC5, 0x1B, 0x72])

    def close_device(self):
        """ Properly close a HID device to prevent running out of handles.
        After you call this method, don't try to use this class anymore or you
        will get unexpected behavior!
        """
        self._dev.close()

    def set_hico(self):
        """ Set high coercivity. """
        self._send_command([0xC2, 0x1B, 0x78])

    def set_loco(self):
        """ Set low coercivity. """
        self._send_command([0xC2, 0x1B, 0x79])

    def ram_test(self):
        """ Test the RAM of the MSR Device. """
        self._send_command([0xC2, 0x1B, 0x87])

    def set_bpi(self, bpi1=None, bpi2=None, bpi3=None):
        """ Set the BPI for card reader. """
        # WTF?!?! How do I set this up?
        self._send_command([])

    def unknown1(self):
        self._send_command([])

    def unknown2(self):
        self._send_command([])

    def unknown3(self):
        self._send_command([])

    def unknown4(self):
        self._send_command([])

    def unknown5(self):
        self._send_command([])

