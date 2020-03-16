# Copyright 2019 Google Inc.
#
# Modified by Brent Rubell for Adafruit Industries, 2019
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright 2019 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
`decode_priv_key.py`
===================================================================

Generates RSA keys and decodes them using python-rsa
for use with a CircuitPython secrets file.

This script is designed to run on a computer,
NOT a CircuitPython device.

Requires Python-RSA (https://github.com/sybrenstuvel/python-rsa)

* Author(s): Google Inc., Brent Rubell
"""
import subprocess
import rsa

# Generate private and public RSA keys
proc = subprocess.Popen(["openssl", "genrsa", "-out", "rsa_private.pem", "2048"])
proc.wait()
proc = subprocess.Popen(
    ["openssl", "rsa", "-in", "rsa_private.pem", "-pubout", "-out", "rsa_public.pem"]
)
proc.wait()

# Open generated private key file
try:
    with open("rsa_private.pem", "rb") as file:
        private_key = file.read()
except:
    print("No file named rsa_private.pem found in directory.")
pk = rsa.PrivateKey.load_pkcs1(private_key)

print("Copy and paste this into your secrets.py file:\n")
print('"private_key": ' + str(pk)[10:] + ",")
