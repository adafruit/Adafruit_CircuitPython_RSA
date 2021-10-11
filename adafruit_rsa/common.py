# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011 Sybren A. Stüvel <sybren@stuvel.eu>
#
# SPDX-License-Identifier: Apache-2.0

"""Common functionality shared by several modules."""

# pylint: disable=invalid-name

import os

from struct import pack
import adafruit_binascii as binascii

from adafruit_rsa._compat import byte, is_integer
from adafruit_rsa import machine_size

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_RSA.git"


class NotRelativePrimeError(ValueError):
    """Raises if provided a and b not relatively prime."""

    def __init__(self, a, b, d, msg=None):
        super().__init__(
            msg or "%d and %d are not relatively prime, divider=%i" % (a, b, d)
        )
        self.a = a
        self.b = b
        self.d = d


def bit_length(int_type):
    """Return the number of bits necessary to represent an integer in binary,
    excluding the sign and leading zeros"""
    length = 0
    while int_type:
        int_type >>= 1
        length += 1
    return length


def bit_size(num):
    """
    Number of bits needed to represent a integer excluding any prefix
    0 bits.

    Usage::

        >>> bit_size(1023)
        10
        >>> bit_size(1024)
        11
        >>> bit_size(1025)
        11

    :param num:
        Integer value. If num is 0, returns 0. Only the absolute value of the
        number is considered. Therefore, signed integers will be abs(num)
        before the number's bit length is determined.
    :returns:
        Returns the number of bits in the integer.
    """

    try:
        return bit_length(num)
    except AttributeError as err:
        raise TypeError(
            "bit_size(num) only supports integers, not %r" % type(num)
        ) from err


def byte_size(number):
    """
    Returns the number of bytes required to hold a specific long number.

    The number of bytes is rounded up.

    Usage::

        >>> byte_size(1 << 1023)
        128
        >>> byte_size((1 << 1024) - 1)
        128
        >>> byte_size(1 << 1024)
        129

    :param number:
        An unsigned integer
    :returns:
        The number of bytes required to hold a specific long number.
    """
    if number == 0:
        return 1
    return ceil_div(bit_size(number), 8)


def ceil_div(num, div):
    """
    Returns the ceiling function of a division between `num` and `div`.

    Usage::

        >>> ceil_div(100, 7)
        15
        >>> ceil_div(100, 10)
        10
        >>> ceil_div(1, 4)
        1

    :param num: Division's numerator, a number
    :param div: Division's divisor, a number

    :return: Rounded up result of the division between the parameters.
    """
    quanta, mod = divmod(num, div)
    if mod:
        quanta += 1
    return quanta


def extended_gcd(a, b):
    """Returns a tuple (r, i, j) such that r = gcd(a, b) = ia + jb"""
    # r = gcd(a,b) i = multiplicitive inverse of a mod b
    #      or      j = multiplicitive inverse of b mod a
    # Neg return values for i or j are made positive mod b or a respectively
    # Iterateive Version is faster and uses much less stack space
    x = 0
    y = 1
    lx = 1
    ly = 0
    oa = a  # Remember original a/b to remove
    ob = b  # negative values from return results
    while b != 0:
        q = a // b
        (a, b) = (b, a % b)
        (x, lx) = ((lx - (q * x)), x)
        (y, ly) = ((ly - (q * y)), y)
    if lx < 0:
        lx += ob  # If neg wrap modulo orignal b
    if ly < 0:
        ly += oa  # If neg wrap modulo orignal a
    return a, lx, ly  # Return only positive values


def inverse(x, n):
    """Returns the inverse of x % n under multiplication, a.k.a x^-1 (mod n)

    >>> inverse(7, 4)
    3
    >>> (inverse(143, 4) * 143) % 4
    1
    """

    (divider, inv, _) = extended_gcd(x, n)

    if divider != 1:
        raise NotRelativePrimeError(x, n, divider)

    return inv


def crt(a_values, modulo_values):
    """Chinese Remainder Theorem.

    Calculates x such that x = a[i] (mod m[i]) for each i.

    :param a_values: the a-values of the above equation
    :param modulo_values: the m-values of the above equation
    :returns: x such that x = a[i] (mod m[i]) for each i


    >>> crt([2, 3], [3, 5])
    8

    >>> crt([2, 3, 2], [3, 5, 7])
    23

    >>> crt([2, 3, 0], [7, 11, 15])
    135
    """

    m = 1
    x = 0

    for modulo in modulo_values:
        m *= modulo

    for (m_i, a_i) in zip(modulo_values, a_values):
        M_i = m // m_i
        inv = inverse(M_i, m_i)

        x = (x + a_i * M_i * inv) % m

    return x


def read_random_bits(nbits):
    """Reads 'nbits' random bits.

    If nbits isn't a whole number of bytes, an extra byte will be appended with
    only the lower bits set.
    """

    nbytes, rbits = divmod(nbits, 8)

    # Get the random bytes
    randomdata = os.urandom(nbytes)

    # Add the remaining random bits
    if rbits > 0:
        randomvalue = ord(os.urandom(1))
        randomvalue >>= 8 - rbits
        randomdata = byte(randomvalue) + randomdata

    return randomdata


def read_random_int(nbits):
    """Reads a random integer of approximately nbits bits."""

    randomdata = read_random_bits(nbits)
    value = bytes2int(randomdata)

    # Ensure that the number is large enough to just fill out the required
    # number of bits.
    value |= 1 << (nbits - 1)

    return value


def read_random_odd_int(nbits):
    """Reads a random odd integer of approximately nbits bits.

    >>> read_random_odd_int(512) & 1
    1
    """

    value = read_random_int(nbits)

    # Make sure it's odd
    return value | 1


def randint(maxvalue):
    """Returns a random integer x with 1 <= x <= maxvalue

    May take a very long time in specific situations. If maxvalue needs N bits
    to store, the closer maxvalue is to (2 ** N) - 1, the faster this function
    is.
    """

    _bit_size = bit_size(maxvalue)

    tries = 0
    while True:
        value = read_random_int(_bit_size)
        if value <= maxvalue:
            break

        if tries % 10 == 0 and tries:
            # After a lot of tries to get the right number of bits but still
            # smaller than maxvalue, decrease the number of bits by 1. That'll
            # dramatically increase the chances to get a large enough number.
            _bit_size -= 1
        tries += 1

    return value


def bytes2int(raw_bytes):
    """Converts a list of bytes or an 8-bit string to an integer.

    When using unicode strings, encode it to some encoding like UTF8 first.

    >>> (((128 * 256) + 64) * 256) + 15
    8405007
    >>> bytes2int(b'\x80@\x0f')
    8405007

    """

    return int(binascii.hexlify(raw_bytes), 16)


def _int2bytes(number, block_size=None):
    """Converts a number to a string of bytes.

    Usage::

        >>> _int2bytes(123456789)
        b'\x07[\xcd\x15'
        >>> bytes2int(_int2bytes(123456789))
        123456789

        >>> _int2bytes(123456789, 6)
        b'\x00\x00\x07[\xcd\x15'
        >>> bytes2int(_int2bytes(123456789, 128))
        123456789

        >>> _int2bytes(123456789, 3)
        Traceback (most recent call last):
        ...
        OverflowError: Needed 4 bytes for number, but block size is 3

    @param number: the number to convert
    @param block_size: the number of bytes to output. If the number encoded to
        bytes is less than this, the block will be zero-padded. When not given,
        the returned block is not padded.

    @throws OverflowError when block_size is given and the number takes up more
        bytes than fit into the block.
    """

    # Type checking
    if not is_integer(number):
        raise TypeError(
            "You must pass an integer for 'number', not %s" % number.__class__
        )

    if number < 0:
        raise ValueError("Negative numbers cannot be used: %i" % number)

    # Do some bounds checking
    if number == 0:
        needed_bytes = 1
        raw_bytes = [b"\x00"]
    else:
        needed_bytes = common.byte_size(number)
        raw_bytes = []

    # You cannot compare None > 0 in Python 3x. It will fail with a TypeError.
    if block_size and block_size > 0:
        if needed_bytes > block_size:
            raise OverflowError(
                "Needed %i bytes for number, but block size "
                "is %i" % (needed_bytes, block_size)
            )

    # Convert the number to bytes.
    while number > 0:
        raw_bytes.insert(0, byte(number & 0xFF))
        number >>= 8

    # Pad with zeroes to fill the block
    if block_size and block_size > 0:
        padding = (block_size - needed_bytes) * b"\x00"
    else:
        padding = b""

    return padding + b"".join(raw_bytes)


def bytes_leading(raw_bytes, needle=b"\x00"):
    """
    Finds the number of prefixed byte occurrences in the haystack.

    Useful when you want to deal with padding.

    :param raw_bytes:
        Raw bytes.
    :param needle:
        The byte to count. Default \x00.
    :returns:
        The number of leading needle bytes.
    """

    leading = 0
    # Indexing keeps compatibility between Python 2.x and Python 3.x
    _byte = needle[0]
    for x in raw_bytes:
        if x == _byte:
            leading += 1
        else:
            break
    return leading


def int2bytes(number, fill_size=None, chunk_size=None, overflow=False):
    """
    Convert an unsigned integer to bytes (base-256 representation)::
    Does not preserve leading zeros if you don't specify a chunk size or
    fill size.
    .. NOTE:
        You must not specify both fill_size and chunk_size. Only one
        of them is allowed.
    :param number:
        Integer value
    :param fill_size:
        If the optional fill size is given the length of the resulting
        byte string is expected to be the fill size and will be padded
        with prefix zero bytes to satisfy that length.
    :param chunk_size:
        If optional chunk size is given and greater than zero, pad the front of
        the byte string with binary zeros so that the length is a multiple of
        ``chunk_size``.
    :param overflow:
        ``False`` (default). If this is ``True``, no ``OverflowError``
        will be raised when the fill_size is shorter than the length
        of the generated byte sequence. Instead the byte sequence will
        be returned as is.
    :returns:
        Raw bytes (base-256 representation).
    :raises:
        ``OverflowError`` when fill_size is given and the number takes up more
        bytes than fit into the block. This requires the ``overflow``
        argument to this function to be set to ``False`` otherwise, no
        error will be raised.
    """

    if number < 0:
        raise ValueError("Number must be an unsigned integer: %d" % number)

    if fill_size and chunk_size:
        raise ValueError("You can either fill or pad chunks, but not both")

    # Ensure these are integers.
    assert isinstance(number, int), "Number must be an unsigned integer, not a float."

    raw_bytes = b""

    # Pack the integer one machine word at a time into bytes.
    num = number
    word_bits, _, max_uint, pack_type = machine_size.get_word_alignment(num)
    pack_format = ">%s" % pack_type
    while num > 0:
        raw_bytes = pack(pack_format, num & max_uint) + raw_bytes
        num >>= word_bits
    # Obtain the index of the first non-zero byte.
    zero_leading = bytes_leading(raw_bytes)
    if number == 0:
        raw_bytes = b"\x00"
    # De-padding.
    raw_bytes = raw_bytes[zero_leading:]

    length = len(raw_bytes)
    if fill_size and fill_size > 0:
        if not overflow and length > fill_size:
            raise OverflowError(
                "Need %d bytes for number, but fill size is %d" % (length, fill_size)
            )
        raw_bytes = (b"\x00" * (fill_size - len(raw_bytes))) + raw_bytes
    elif chunk_size and chunk_size > 0:
        remainder = length % chunk_size
        if remainder:
            padding_size = chunk_size - remainder
            raw_bytes = "% {}s".format(length + padding_size).encode() % raw_bytes
    return raw_bytes
