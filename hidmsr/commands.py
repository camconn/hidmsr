""" Interface for the the MSR605X magnetic card reader.

This file defines an interface as well as utility functions to read and
interact with the MSR605X HID-based reader.

Licensed under the GNU Public License, version 3 or later.

Copyright (c) 2018 Cameron Conn
"""


import ctypes
import functools
import logging
import sys
import time
import threading

import pywinusb.hid as hid


_l = logging.getLogger("hidmsr.commands")


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

def _data_handler(self, data):
    _l.debug("Got response")
    if len(data) > 1:  # Strip off the first char if we have data longer than 1 byte
        data = data[1:]
    hex_str = ["{:02X}".format(c) for c in data]
    raw_str = "".join(["{:c}".format(c) for c in data])
    out = " ".join(hex_str)
    _l.debug("Response Data:", out)
    self._responses.append(data)


class MSRDevice():
    """ Represents a MSR HID-based Magnetic Card Reader/Writier device. """

    def __init__(self, vendor_id=0x0801, product_id=0x0003):
        _l.debug("Creating MSR device")
        self._vid = vendor_id
        self._pid = product_id

        filter = hid.HidDeviceFilter(vendor_id = vendor_id, product_id = product_id)

        all_devices = filter.get_devices()
        if len(all_devices) == 0:
            raise RuntimeError("No appropriate MSR device found! Please check your device is plugged in.")

        # Just assume we want the first device.
        device = all_devices[0]
        device.open()

        self._dev = device
        self._lock = threading.Lock()
        self._responses = []

        data_handler = functools.partial(_data_handler, self)
        device.set_raw_data_handler(data_handler)
        _l.debug("Created MSR device.")

    def _send_command_wait(self, command, wait_time=0.05):
        """ Send a command to the MSR device and wait for a result. """
        _l.debug("Sending wait command", command)

        responses = []
        try:
            self._lock.acquire()
            self._responses.clear()
            self.__send_command(command)

            # Wait for any messages to come though
            while len(self._responses) == 0:
                time.sleep(wait_time)
            time.sleep(wait_time)  # we've gotten one message, so let's see if we get any more.

            responses = self._responses.copy()
            self._responses.clear()
            #self._lock.release()
            #return responses
        except KeyboardInterrupt as e:
            print("Caught KeyboardInterrupt. Quitting command send.")
        finally:
            self._lock.release()
            return responses

    def _send_command_nowait(self, command):
        """ Send a command to the MSR device without waiting for a result. """
        _l.debug("Sending nowait command", command)

        # Make sure that we aren't interfering with an existing running command.
        try:
            self._lock.acquire()
            self.__send_command(command)
        except KeyboardInterrupt as e:
            print("Caught KeyboardInterrupt. Quitting command send.")
        finally:
            self._lock.release()

    def __send_command(self, command):
        """ Send a command to the MSR device. """
        if not self._dev.is_active():
            raise RuntimeError("The MSR device is not active! This should never happen!")
        report = _create_report_data(0x00, _extend_command(command))
        self._dev.send_feature_report(report)

    def firmware_version(self):
        """ Get the firmware version of this device. """
        return self._send_command_wait([0xC5, 0x1B, 0x76])

    def reset(self):
        """ Reset the device's state. """
        self._send_command_nowait([0xC2, 0x1B, 0x61, 0x44, 0xF8, 0x19])

    def read_raw(self):
        """ Read a card's raw data without any preprocessing. """
        return self._send_command_wait([0xC5, 0x1B, 0x6D])

    def read(self):
        """ Read ISO data from a card. """
        return self._send_command_wait([0xC5, 0x1B, 0x72])

    def close_device(self):
        """ Properly close a HID device to prevent running out of handles.
        After you call this method, don't try to use this class anymore or you
        will get unexpected behavior!
        """
        if not self._dev.is_active():
            _l.warning("The pywinusb device is not active. This may cause you some problems.")
        return self._dev.close()

    def set_hico(self):
        """ Set high coercivity. """
        self._send_command_wait([0xC2, 0x1B, 0x78])

    def set_loco(self):
        """ Set low coercivity. """
        self._send_command_wait([0xC2, 0x1B, 0x79])

    def ram_test(self):
        """ Test the RAM of the MSR Device. """
        return self._send_command_wait([0xC2, 0x1B, 0x87])

    def set_bpi(self, bpi1=None, bpi2=None, bpi3=None):
        """ Set the BPI for card reader. """
        # WTF?!?! How do I set this up?
        self.__send_command_wait([])

    def write(self, track1=None, track2=None, track3=None):
        """ Write data to a magnetic card. """

        if not (track1 or track2 or track3):
            _l.error("Need some data to write! " \
                     "If you would like to erase a card, use erase() instead.")
        pass

    # NOTE: Unknown methods below!
    # These are not tested to see if they work or not!

    def unknown1(self):
        """ Unknown device function. Included for the sake of completeness. """
        _l.warning("This is an unknown function. Use at your own risk!")
        self.__send_command([0xC5, 0x1B, 0xA9])

    def unknown2(self):
        """ Unknown device function. Included for the sake of completeness. """
        _l.warning("This is an unknown function. Use at your own risk!")
        self.__send_command([0xC5, 0x1B, 0xA1])

    def unknown3(self):
        """ Unknown device function. Included for the sake of completeness. """
        _l.warning("This is an unknown function. Use at your own risk!")
        self.__send_command([0xC5, 0x1B, 0xA2])

    def unknown4(self):
        """ Unknown device function. Included for the sake of completeness. """
        _l.warning("This is an unknown function. Use at your own risk!")
        self.__send_command([0xC5, 0x1B, 0xA3])

    def unknown5(self):
        """ Unknown device function. Included for the sake of completeness. """
        _l.warning("This is an unknown function. Use at your own risk!")
        self.__send_command([0xC5, 0x1B, 0xA4])

    def unknown6(self):
        """ Unknown device function. Included for the sake of completeness. """
        _l.warning("This is an unknown function. Use at your own risk!")
        self.__send_command([0xC5, 0x1B, 0xAE])

