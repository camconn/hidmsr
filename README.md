An interface and library for the MSR605X magnetic card reader/writer.

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

# License
This code is licensed under the GNU Public License, Version 3 or later. See LICENSE for more details.
