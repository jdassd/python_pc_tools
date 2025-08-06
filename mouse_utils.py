import time
import threading
from pynput.mouse import Button, Controller
from pynput import keyboard

class Clicker(threading.Thread):
    def __init__(self, interval, button, x=None, y=None):
        super().__init__()
        self.interval = interval
        self.button = button
        self.x = x
        self.y = y
        self.running = False
        self.daemon = True
        self.mouse = Controller()

    def run(self):
        self.running = True
        while self.running:
            if self.x is not None and self.y is not None:
                self.mouse.position = (self.x, self.y)
            self.mouse.click(self.button)
            time.sleep(self.interval)

    def stop(self):
        self.running = False

class HotkeyListener(threading.Thread):
    def __init__(self, start_callback, stop_callback):
        super().__init__()
        self.daemon = True
        self.start_callback = start_callback
        self.stop_callback = stop_callback

    def run(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        try:
            if key == keyboard.Key.f6:
                self.start_callback()
            elif key == keyboard.Key.f7:
                self.stop_callback()
        except AttributeError:
            pass
