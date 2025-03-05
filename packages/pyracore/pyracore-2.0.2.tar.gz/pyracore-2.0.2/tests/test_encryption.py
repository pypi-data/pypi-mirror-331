# tests/test_encryption.py
import unittest
from pyracore.core.encryption import encrypt, decrypt

class TestEncryption(unittest.TestCase):
    def test_encrypt_decrypt(self):
        data = "Test message"
        encrypted = encrypt(data)
        decrypted = decrypt(encrypted)
        self.assertEqual(data, decrypted)

if __name__ == '__main__':
    unittest.main()