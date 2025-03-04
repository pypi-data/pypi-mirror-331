# core/utils.py
import os
import uuid

def generate_unique_id():
    return str(uuid.uuid4())

def get_appdata_path():
    return os.environ.get('APPDATA', '')