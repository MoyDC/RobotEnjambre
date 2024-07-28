import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../moreGPIO')))
from More_GPIO_ESP32 import MoreGpio_ESP32

class output_ESP32(MoreGpio_ESP32):
    def __init__(self, bus_number=1, address=0x08):
        super().__init__(bus_number, address)
        self._output_pins = {
            "OUTPUTSPin23": 23,
            "OUTPUTSPin19": 19,
            "OUTPUTSPin18": 18,
            "OUTPUTSPin5": 5
        }
        self._output_configs = {}
    
    def get_output_pin(self, pin_name):
        return self._output_pins.get(pin_name)
    
    def get_output_name_by_pin(self, pin_number):
        for name, pin in self._output_pins.items():
            if pin == pin_number:
                return name
        return None  # Retornar None si no se encuentra el pin
    
    def get_all_output_pins(self):
        return self._output_pins
    
    def setup_output(self, output_name, initial_value):
        pin = self.get_output_pin(output_name)
        if pin is not None:
            self._output_configs[output_name] = {'pin': pin, 'value': initial_value}
            self.send_command(self._command_output, pin, initial_value)
        else:
            print(f"output pin {output_name} not found.")
    
    def control_output(self, value):
        for output_name, config in self._output_configs.items():
            pin = config['pin']
            self.send_command(self._command_output, pin, value)
            self._output_configs[output_name]['value'] = value