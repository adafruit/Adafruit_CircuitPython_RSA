"""Adafruit RSA Tests
"""
import time
import adafruit_rsa

# Generate general purpose keys
(pub, priv) = adafruit_rsa.newkeys(256, log_level="DEBUG")


def test_encrypt_decrypt():
    msg = "blinka".encode("utf-8")
    msg_enc = adafruit_rsa.encrypt(msg, pub)
    msg_dec = adafruit_rsa.decrypt(msg_enc, priv)
    assert msg == msg_dec, "Decrypted message does not match original message"


def test_mod_msg():
    """Modifies an enecrypted message, asserts failure
    """
    msg = "blinka".encode("utf-8")
    msg_enc = adafruit_rsa.encrypt(msg, pub)
    msg_enc = msg_enc[:-1] + b"X"  # change the last byte
    try:
        msg_dec = adafruit_rsa.decrypt(msg_enc, priv)
        raise ("ERROR: Decrypted message matches original")
    except adafruit_rsa.pkcs1.DecryptionError:
        pass


def test_randomness():
    """Encrypt msg 2x yields diff. encrypted values.
    """
    msg = "blinka".encode("utf-8")
    msg_enc_1 = adafruit_rsa.encrypt(msg, pub)
    msg_enc_2 = adafruit_rsa.encrypt(msg, pub)
    assert msg_enc_1 != msg_enc_2, "Messages should yield different values."


def test_sign_verify_sha256():
    """Test SHA256 sign and verify the message.
    """
    (pub, priv) = adafruit_rsa.newkeys(496, log_level="DEBUG")
    msg = "red apple"
    signature = adafruit_rsa.sign(msg, priv, "SHA-256")
    adafruit_rsa.verify(msg, signature, pub)


def test_sign_verify_sha384():
    """Test SHA-384 sign and verify the message.
    """
    (pub, priv) = adafruit_rsa.newkeys(624, log_level="DEBUG")
    msg = "red apple"
    signature = adafruit_rsa.sign(msg, priv, "SHA-384")
    adafruit_rsa.verify(msg, signature, pub)


def test_sign_verify_sha512():
    """Test SHA-512 sign and verify the message.
    """
    (pub, priv) = adafruit_rsa.newkeys(752, log_level="DEBUG")
    msg = "red apple"
    signature = adafruit_rsa.sign(msg, priv, "SHA-512")
    adafruit_rsa.verify(msg, signature, pub)


def test_sign_verify_fail():
    """Check for adafruit_rsa.pkcs1.VerificationError on
    a modified message (invalid signature).
    """
    msg = "red apple"
    signature = adafruit_rsa.sign(msg, priv, "SHA-512")
    msg = "blue apple"
    try:
        adafruit_rsa.verify(msg, signature, pub)
    except adafruit_rsa.pkcs1.VerificationError:
        # Expected error
        pass


# List all tests
all_tests = [
    test_encrypt_decrypt,
    test_mod_msg,
    test_randomness,
    test_sign_verify_sha256,
    test_sign_verify_sha384,
    test_sign_verify_sha512,
]

# Run adafruit_rsa tests
start_time = time.monotonic()
for i in range(len(all_tests)):
    all_tests[i]()
    print("OK!")
print("Ran {} tests in {} seconds".format(len(all_tests), time.monotonic() - start_time))

