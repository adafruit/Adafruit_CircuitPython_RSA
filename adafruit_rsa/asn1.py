# SPDX-FileCopyrightText: 2011 Sybren A. Stüvel <sybren@stuvel.eu>
#
# SPDX-License-Identifier: Apache-2.0

"""
`adafruit_rsa.asn1`
====================================================

ASN.1 definitions.

Not all ASN.1-handling code use these definitions, but when it does, they should be here.
"""

try:
    from pyasn1.type import namedtype, tag, univ
except ImportError as err:
    raise ImportError("Usage of asn1.py requires pyasn1 library") from err

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_RSA.git"


class PubKeyHeader(univ.Sequence):
    """OpenSSL Public Key Header"""

    componentType = namedtype.NamedTypes(
        namedtype.NamedType("oid", univ.ObjectIdentifier()),
        namedtype.NamedType("parameters", univ.Null()),
    )


class OpenSSLPubKey(univ.Sequence):
    """Creates a PKCS#1 DER-encoded NamedType."""

    componentType = namedtype.NamedTypes(
        namedtype.NamedType("header", PubKeyHeader()),
        # This little hack (the implicit tag) allows us to get a Bit String as Octet String
        namedtype.NamedType(
            "key",
            univ.OctetString().subtype(implicitTag=tag.Tag(tagClass=0, tagFormat=0, tagId=3)),
        ),
    )


class AsnPubKey(univ.Sequence):
    """ASN1 contents of DER encoded public key:

    .. code-block:: shell

        RSAPublicKey ::= SEQUENCE {
            modulus           INTEGER,  -- n
            publicExponent    INTEGER,  -- e
        }

    """

    componentType = namedtype.NamedTypes(
        namedtype.NamedType("modulus", univ.Integer()),
        namedtype.NamedType("publicExponent", univ.Integer()),
    )
