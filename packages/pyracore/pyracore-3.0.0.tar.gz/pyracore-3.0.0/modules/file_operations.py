# modules/file_operations.py
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os

AES_KEY = b'ThisIsA32ByteIVForAES256Encrypt!'
AES_IV = b'ThisIsA16ByteIV!'

def encrypt_file(file_path):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    with open(file_path, 'rb') as f:
        with open(file_path + ".enc", 'wb') as wf:
            while chunk := f.read(64 * 1024):
                encrypted_chunk = cipher.encrypt(pad(chunk, AES.block_size))
                wf.write(encrypted_chunk)
    os.remove(file_path)
    os.rename(file_path + ".enc", file_path)

def decrypt_file(file_path):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    with open(file_path, 'rb') as f:
        with open(file_path + ".dec", 'wb') as wf:
            while chunk := f.read(64 * 1024):
                decrypted_chunk = unpad(cipher.decrypt(chunk), AES.block_size)
                wf.write(decrypted_chunk)
    os.remove(file_path)
    os.rename(file_path + ".dec", file_path)