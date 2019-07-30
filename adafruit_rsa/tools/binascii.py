"""
The MIT License (MIT)

Copyright (c) 2013, 2014 micropython-lib contributors
Modified by Dave Astels for Adafruit Industries, 2019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
if not "unhexlify" in globals():

    def unhexlify(data):
        if len(data) % 2 != 0:
            raise ValueError("Odd-length string")

        return bytes([int(data[i : i + 2], 16) for i in range(0, len(data), 2)])


if not "hexlify" in globals():

    def hexlify(data):
        """Return the hexadecimal representation of the
        binary data. Every byte of data is converted into
        the corresponding 2-digit hex representation.
        The returned bytes object is therefore twice
        as long as the length of data.
        """
        if len(data) == 0:
            raise ValueError("Provided data is zero-length")
        return bytes([int(data[i : i + 16], 2) for i in range(0, len(data), 2)])



b2a_hex = hexlify
a2b_hex = unhexlify

PAD = "="

# pylint:disable=invalid-name,line-too-long
table_a2b_base64 = b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff>\xff\xff\xff?456789:;<=\xff\xff\xff\xff\xff\xff\xff\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\xff\xff\xff\xff\xff\xff\x1a\x1b\x1c\x1d\x1e\x1f !\"#$%&'()*+,-./0123\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
# pylint:enable=line-too-long

assert len(table_a2b_base64) == 256


def a2b_base64(ascii_data):
    "Decode a line of base64 data."

    res = []
    quad_pos = 0
    leftchar = 0
    leftbits = 0
    last_char_was_a_pad = False

    for c in ascii_data:
        c = chr(c)
        if c == PAD:
            if quad_pos > 2 or (quad_pos == 2 and last_char_was_a_pad):
                break  # stop on 'xxx=' or on 'xx=='
            last_char_was_a_pad = True
        else:
            n = ord(table_a2b_base64[ord(c)])
            if n == 0xFF:
                continue  # ignore strange characters
            #
            # Shift it in on the low end, and see if there's
            # a byte ready for output.
            quad_pos = (quad_pos + 1) & 3
            leftchar = (leftchar << 6) | n
            leftbits += 6
            #
            if leftbits >= 8:
                leftbits -= 8
                res.append((leftchar >> leftbits).to_bytes(1, "big"))
                leftchar &= (1 << leftbits) - 1
            #
            last_char_was_a_pad = False
    else:
        if leftbits != 0:
            raise Exception("Incorrect padding")

    return b"".join(res)


# ____________________________________________________________

table_b2a_base64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def b2a_base64(bin_data):
    "Base64-code line of data."

    newlength = (len(bin_data) + 2) // 3
    newlength = newlength * 4 + 1
    res = []

    leftchar = 0
    leftbits = 0
    for c in bin_data:
        # Shift into our buffer, and output any 6bits ready
        leftchar = (leftchar << 8) | c
        leftbits += 8
        res.append(table_b2a_base64[(leftchar >> (leftbits - 6)) & 0x3F])
        leftbits -= 6
        if leftbits >= 6:
            res.append(table_b2a_base64[(leftchar >> (leftbits - 6)) & 0x3F])
            leftbits -= 6
    #
    if leftbits == 2:
        res.append(table_b2a_base64[(leftchar & 3) << 4])
        res.append(PAD)
        res.append(PAD)
    elif leftbits == 4:
        res.append(table_b2a_base64[(leftchar & 0xF) << 2])
        res.append(PAD)
    return "".join(res).encode("ascii")

