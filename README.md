An interface and library for the MSR605X magnetic card reader/writer.

This project is a reverse engineered interface for the MSR605X magnetic card reader/writer.

# Requirements
For now, this project is supported for Python 3.2 (and later) on Windows. Linux support is
planned in the future, but the only thing it can handle right now is Windows (as far as pywinusb is concerned).

As usual, you will need to install some packages:

    pip install -r requirements.txt

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
- Rene for creating the [pywinusb](https://github.com/rene-aguirre/pywinusb) library
- Carlos M for documenting some reverse engineering for [pyrfidhid](https://github.com/charlysan/pyrfidhid)

# License
This code is licensed under the GNU Public License, Version 3 or later. See LICENSE for more details.

