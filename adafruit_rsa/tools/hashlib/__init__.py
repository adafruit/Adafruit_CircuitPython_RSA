"""
The MIT License (MIT)

Copyright (c) 2013, 2014 micropython-lib contributors

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
# pylint: disable=invalid-name
try:
    # pylint: disable=import-self
    import hashlib
except ImportError:
    hashlib = None


def init():
    """Create a new hashlib module with provided algorithms.
    """
    for i in ("sha1", "sha224", "sha256", "sha384", "sha512", "md5"):
        c = getattr(hashlib, i, None)
        if not c:
            c = __import__("_" + i, None, None, (), 1)
            c = getattr(c, i)
        globals()[i] = c

def new(algo, data=b""):
    """Returns a new hashing object using the
    named algorithm; optionally initialized with data (which must be
    a bytes-like object).
    """
    try:
        c = globals()[algo]
        return c(data)
    except KeyError:
        raise ValueError(algo)

init()
