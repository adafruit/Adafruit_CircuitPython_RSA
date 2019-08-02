# JSON Web Token (JWT) Generation
# https://tools.ietf.org/html/rfc7519
import time
import json
from micropython import const

try:
    from binascii import b2a_base64
except ImportError:
    from adafruit_rsa.tools.binascii import b2a_base64
    pass

# TODO: See if str.translate works so an external lib doesnt need to be imported again
# https://docs.python.org/3/library/stdtypes.html#str.translate
from adafruit_rsa.tools import string

import adafruit_rsa


def b42_urlsafe_encode(payload):
    """Translates payload into b64-encoded payload
    """
    return string.translate(
        b2a_base64(payload)[:-1].decode("utf-8"), {ord("+"): "-", ord("/"): "_"}
    )


# Decoded prvate_key.PEM Dump via Computer
# TODO: Fiddle with Pyasn1 more to see if this can be done on-device instead...
private_key = (int1, int2, int3, int4, int5)

# Create a priv_key object from the private_key
priv_key = adafruit_rsa.PrivateKey(*private_key)


# Micropython offset
# TODO: check if this works on circuitpython, or if it's even required...
epoch_offset = 946684800

# Construct Claims
token = {
    # The time that the token was issued at
    "iat": time.time() + epoch_offset,
    # The time the token expires.       TTL Token
    "exp": time.time() + epoch_offset + 43200,
    # The audience field should always be set to the GCP project id.
    "aud": "artful-shelter-244016",
}

# JWT Header Construction


# JWT RS256 (RSASSA-PKCS1-v1_5 using SHA-256 RFC 7518 sec 3.3).
jwt_algo = "RS256"
header = {"alg": jwt_algo, "typ": "JWT"}
# TODO: move b42_urlsafe_encode method into the library directly
content = b42_urlsafe_encode(json.dumps(header).encode("utf-8"))
# TODO: move b42_urlsafe_encode method into the library directly
# {Base64url encoded header}.{Base64url encoded claim set}
content = content + "." + b42_urlsafe_encode(json.dumps(token).encode("utf-8"))
print("signing...")

# TODO: amount of lines required to generate the signature should be less
# example: {"alg": "RS256", "typ": "JWT"}.{"aud": "my-project", "iat": 1509650801, "exp": 1509654401}.[signature bytes]
signature = b42_urlsafe_encode(adafruit_rsa.sign(content, priv_key, "SHA-256"))
print("signed")

jwt = "{0}.{1}".format(content, signature)
#jwt = content + "." + signature  # signed JWT

print(jwt)
