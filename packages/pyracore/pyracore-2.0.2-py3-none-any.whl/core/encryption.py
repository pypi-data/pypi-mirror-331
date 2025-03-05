# my_malware_library/core/encryption.py
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

AES_KEY = b'ThisIsA32ByteIVForAES256Encrypt!'
AES_IV = b'ThisIsA16ByteIV!'

def encrypt(data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))
    return base64.b64encode(encrypted_data).decode()

def decrypt(encrypted_data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    decrypted_data = unpad(cipher.decrypt(base64.b64decode(encrypted_data)), AES.block_size)
    return decrypted_data.decode()