# SPDX-FileCopyrightText: 2011 Sybren A. Stüvel <sybren@stuvel.eu>
#
# SPDX-License-Identifier: Apache-2.0

"""
RSA module
====================================================

Module for calculating large primes, and RSA encryption, decryption, signing
and verification. Includes generating public and private keys.

**WARNING:** This implementation does not use compression of the cleartext input to
prevent repetitions, or other common security improvements. Use with care.

"""

from adafruit_rsa.key import PrivateKey, PublicKey, newkeys
from adafruit_rsa.pkcs1 import (
    DecryptionError,
    VerificationError,
    compute_hash,
    decrypt,
    encrypt,
    find_signature_hash,
    sign,
    sign_hash,
    verify,
)

__author__ = "Sybren Stuvel, Barry Mead and Yesudeep Mangalapilly"
__date__ = "2018-09-16"
# __version__ = '4.0.0'
__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_RSA.git"
