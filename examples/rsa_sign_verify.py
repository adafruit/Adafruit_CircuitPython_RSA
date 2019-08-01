import adafruit_rsa

# Generate a new keypair
(public_key, private_key) = adafruit_rsa.newkeys(512)

# Create a new message
message = 'Go left at the blue tree'

# Hash the message using SHA-224
hash_method = "SHA-224"
signature = adafruit_rsa.sign(message, private_key, hash_method)

print("Message ", adafruit_rsa.verify(message, signature, public_key))
