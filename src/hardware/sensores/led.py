import time
from gpiozero import LED

class LedController:
    def __init__(self, pin, delay=0.25):
        self.__pin = pin
        self.led = LED(pin)
        self.delay = delay
        self.__is_running = False  # Usamos doble guion bajo para name mangling

    def blink(self):
        """Start blinking the LED"""
        self.__is_running = True
        while self.__is_running:
            self.led.on()
            time.sleep(self.delay)
            self.led.off()
            time.sleep(self.delay)

    def stop(self):
        """Stop blinking the LED"""
        self.__is_running = False
        self.led.off()
        print(f"Led pin {self.__pin} stopped.")
