# SPDX-FileCopyrightText: 2019 Google Inc.
# SPDX-FileCopyrightText: 2019 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: Apache-2.0

"""
`decode_priv_key.py`
===================================================================

Generates RSA keys and decodes them using python-rsa
for use with a CircuitPython settings.toml file.

This script is designed to run on a computer,
NOT a CircuitPython device.

Requires Python-RSA (https://github.com/sybrenstuvel/python-rsa)

* Author(s): Google Inc., Brent Rubell
"""

import subprocess

import rsa

# Generate private and public RSA keys
with subprocess.Popen(["openssl", "genrsa", "-out", "rsa_private.pem", "2048"]) as proc:
    proc.wait()
with subprocess.Popen(
    ["openssl", "rsa", "-in", "rsa_private.pem", "-pubout", "-out", "rsa_public.pem"]
) as proc:
    proc.wait()

# Open generated private key file
try:
    with open("rsa_private.pem", "rb") as file:
        private_key = file.read()
except:
    print("No file named rsa_private.pem found in directory.")
pk = rsa.PrivateKey.load_pkcs1(private_key)

print("Copy and paste this into your settings.toml file:\n")
print(f'private_key="{str(pk)[10:]}"')
