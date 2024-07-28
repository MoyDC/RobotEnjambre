import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../moreGPIO')))
from More_GPIO_ESP32 import MoreGpio_ESP32

class pwm_ESP32(MoreGpio_ESP32):
    def __init__(self, bus_number=1, address=0x08):
        super().__init__(bus_number, address)
        self._pwm_pins = {
            "PWMPin12": 12,
            "PWMPin14": 14,
            "PWMPin27": 27,
            "PWMPin26": 26,
            "PWMPin25": 25,
            "PWMPin33": 33,
            "PWMPin17": 17,
            "PWMPin16": 16
        }
        self._pwm_configs = {}
        
    def get_pwm_pin(self, pin_name):
        return self._pwm_pins.get(pin_name)
    
    def get_pwm_name_by_pin(self, pin_number):
        for name, pin in self._pwm_pins.items():
            if pin == pin_number:
                return name
        return None  # Retornar None si no se encuentra el pin
    
    def get_all_pwm_pins(self):
        return self._pwm_pins

    def setup_pwm(self, pwm_name, initial_value):
        pin = self.get_pwm_pin(pwm_name)
        if pin is not None:
            self._pwm_configs[pwm_name] = {'pin': pin, 'value': initial_value}
            self.send_command(self._command_pwm, pin, initial_value)
        else:
            print(f"pwm pin {pwm_name} not found.")
    
    def control_pwm(self, value):
        for pwm_name, config in self._pwm_configs.items():
            pin = config['pin']
            self.send_command(self._command_pwm, pin, value)
            self._pwm_configs[pwm_name]['value'] = value