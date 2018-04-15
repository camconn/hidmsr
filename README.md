An interface and library for the MSR605X magnetic card reader/writer.

This project is a reverse engineered interface for the MSR605X magnetic card reader/writer.

# Requirements
For now, this project is supported for Python 3.2 (and later) on Windows. Linux support is
planned in the future, but the only thing it can handle right now is Windows (as far as pywinusb is concerned).

As usual, you will need to install some packages:

    pip install -r requirements.txt

# Using hidmsr
`hidmsr` documents itself with the standard Python documentation methods for your convenience.

Some things you may be interested in are listed below.

## hidmsr.commands
This submodule includes the `MSRDevice` class. This is how you actually communicate with the MSR605X.

For example, you may use it like this:
```python
import hidmsr.commands as cmds

m = cmds.MSRDevice()
m.reset()
card_data = m.read_raw()
print("Card data:")
print(card_data)
```

Some of the available methods in `MSRDevice` are:
- close() - Close the MSRDevice when you are done using it.
- reset() - Send a reset command to the MSR605X. Returns nothing.
- read() - Read data from the MSR605X. Returns a list which can contain either `str`s or `None`.
- read_raw() - Read data from the MSR605X without decoding it. Returns a list of lists of `int`s.
- firmware_version() - Get the firmware version of the MSR605X.
- set_loco() - Set low magnetic coercivity
- set_hico() - Set high magnetic coercivity
- ram_test() - Test the RAM on the MSR605X
- set_bpi(track1, track2, track3) - Set the BPI of tracks 1, 2, and 3.
- write(track1, track2, track3) - UNIMPLEMENTED! Write data to a magnetic card.
- unknown{1,2,3,4,5,6}() - UNIMPLEMENTED! Unknown functions of the MSR605X found from reversing the firmware.


## hidmsr.convert
This submodule provides methods for decoding data read from the MSR605X as well as some common magnetic stripe data formats.

You may want to use the `decode_sixdec` and `decode_aba` methods in this submodule.

# Reverse Engineering
Essentially, this project was reverse engineered from the existing MSRX Windows Application.

The MSR605X is a HID-based magnetic card reader. Its command protocol is similar to that of the MSR605, and other PL-2303
compatible MSR devices. The command structure is essentially the same, except that it is now carried over the USB HID
protocol.

For notes concerning the HID implementation and a hardware analysis of the MSR605X, please refer to the `reverse`
subdirectory.

Moreover, note that while the MSR605X reports its Vendor and Product IDs as `0x0801` and `0x0003` respectively, the
reported associated device "MagTek Insert Reader" is **not** the MSR605X. It is likely that the original creators of the
MSR605X just hijacked this VID:PID combination.

# Acknowledgements
This project is built upon the shoulder of giants. I would like to thank the following individuals/projects for making this
work possible:
- Raphael Michel for writing [msrtool](https://github.com/raphaelm/msrtool)
- René Aguirre for creating the [pywinusb](https://github.com/rene-aguirre/pywinusb) library
- Carlos M for documenting some reverse engineering for [pyrfidhid](https://github.com/charlysan/pyrfidhid)

# License
This code is licensed under the GNU Public License, Version 3 or later. See LICENSE for more details.

