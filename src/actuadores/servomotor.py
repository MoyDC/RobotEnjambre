import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../moreGPIO')))
from moreGPIO.More_GPIO_ESP32 import MoreGpio_ESP32


class ServoController(MoreGpio_ESP32):
    def __init__(self, bus_number=1, address=0x08):
        super().__init__(bus_number, address)
        self._servo_pins = {
            "servoPin4": 4,
            "servoPin13": 13,
            "servoPin15": 15
        }
        self.__valueServo = 0
        self._servo_configs = {}
        
    def get_servo_value(self) -> int:
        return self.__valueServo
    
    def get_servo_pin(self, pin_name):
        return self._servo_pins.get(pin_name)
    
    def get_servo_name_by_pin(self, pin_number):
        for name, pin in self._servo_pins.items():
            if pin == pin_number:
                return name
        return None  # Retornar None si no se encuentra el pin
    
    def get_all_servo_pins(self):
        return self._servo_pins

    def setup_servo(self, servo_name, initial_value):
        # Asegurar que el valor esté en el rango 0-180
        value = max(0, min(180, int(initial_value)))
        
        #Guardar el valor del servomotor
        self.__valueServo = value
        
        # configurar el pin y mandar valor por i2c a la esp32
        pin = self.get_servo_pin(servo_name)
        if pin is not None:
            self._servo_configs[servo_name] = {'pin': pin, 'value': value}
            self.send_command(self.command_servomotor, pin, value)
        else:
            print(f"Servo pin {servo_name} not found.")

    def control_servo(self, value_servo):
        # Asegurar que el valor esté en el rango 0-180
        value = max(0, min(180, int(value_servo)))
        
        #Guardar el valor del servomotor
        self.__valueServo = value
        
        # Mandar el valor por i2c a la esp32
        for servo_name, config in self._servo_configs.items():
            pin = config['pin']
            self.send_command(self.command_servomotor, pin, value)
            self._servo_configs[servo_name]['value'] = value
    