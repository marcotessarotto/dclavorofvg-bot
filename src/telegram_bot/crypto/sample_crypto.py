from Crypto.Cipher import AES

# pip install pycrypto

# >> > from Crypto.Cipher import AES
# >> > from Crypto import Random
# >> >
# >> > key = b'Sixteen byte key'
# >> > iv = Random.new().read(AES.block_size)
# >> > cipher = AES.new(key, AES.MODE_CFB, iv)
# >> > msg = iv + cipher.encrypt(b'Attack at dawn')



key = bytes([0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00,
             ])

iv = bytes([0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00,
             ])

original_cleartext = '2394298374892374' # Input strings must be a multiple of 16 in length

print("original_cleartext = " + original_cleartext)
print("len(original_cleartext)=" + str(len(original_cleartext)))

cipher = AES.new(key, AES.MODE_CBC, iv)
ciphertext = cipher.encrypt(original_cleartext) # materiale cripto e poi il payload
print(type(ciphertext))

print("ciphertext:")
print(str(ciphertext))
print(len(ciphertext))
#print(msg.encode("hex"))

import base64

encoded_ciphertext = base64.b64encode(ciphertext)

print(encoded_ciphertext)


decipher = AES.new(key, AES.MODE_CBC, iv)
print("cleartext:")
print(decipher.decrypt(ciphertext))
