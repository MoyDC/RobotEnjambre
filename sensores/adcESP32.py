import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../moreGPIO')))
from More_GPIO_ESP32 import MoreGpio_ESP32

class adc_ESP2(MoreGpio_ESP32):
    def __init__(self, bus_number=1, address=0x08, adc_pin=None):
        super().__init__(bus_number, address)
        self._adc_pins = {
            "ADCPin36": 36,
            "ADCPin39": 39,
            "ADCPin34": 34,
            "ADCPin35": 35
        }
        self.adc_pin = adc_pin

    def get_adc_pin(self, pin_name):
        return self._adc_pins.get(pin_name)

    def get_adc_name_by_pin(self, pin_number):
        for name, pin in self._adc_pins.items():
            if pin == pin_number:
                return name
        return None  # Retornar None si no se encuentra el pin
    
    def get_all_adc_pins(self):
        return self._adc_pins

    def setup_adc_pin(self, pin_name):
        self.adc_pin = self.get_adc_pin(pin_name)
        if self.adc_pin is None:
            print(f"ADC pin '{pin_name}' not found.")
        #else:
            #print(f"ADC pin set to '{pin_name}'.")

    def read_adc(self, cont=0, delay=0.01):
        if self.adc_pin is None:
            print("ADC pin not set.")
            return None
        else:
            command = self.command_adc
            sensor_value, idPinReturn = self.read_command(command, self.adc_pin, cont, delay)
            return sensor_value, idPinReturn