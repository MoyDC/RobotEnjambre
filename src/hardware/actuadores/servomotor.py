import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../hardware')))
from hardware.moreGPIO.More_GPIO_ESP32 import MoreGpio_ESP32


class ServoController(MoreGpio_ESP32):
    def __init__(self, bus_number=1, address=0x08):
        super().__init__(bus_number, address)
        self._servo_pins = {
            "servoPin4": 4,
            "servoPin13": 13,
            "servoPin15": 15
        }
        self.__value_Max = 180
        self.__value_Min = 0
        self.__valueServo = 0
        self.__pin_servo = -1
        self.__is_pin_setup = False
        self._servo_configs = {}
        
    def get_servo_value(self) -> int:
        """Get the current value of the servo."""
        return self.__valueServo
    
    def get_servo_pin(self, pin_name):
        """Get the pin number associated with a given servo name."""
        return self._servo_pins.get(pin_name)
    
    def get_servo_name_by_pin(self, pin_number):
        """Get the servo name associated with a given pin number."""
        for name, pin in self._servo_pins.items():
            if pin == pin_number:
                return name # Retornar el nombre
        return None  # Retornar None si no se encuentra el pin
    
    def get_all_servo_pins(self):
        """Get all servo pins."""
        return self._servo_pins

    def value_within_range(self, value):
        """Ensure the value is within the defined range."""
        return max(self.__value_Min, min(self.__value_Max, int(value))) # Asegurar que el valor esté en el rango 0-180

    def setup_servo(self, servo_name, initial_value):
        """Setup the servo with a given servo_name and initial_value."""
        pin = self.get_servo_pin(servo_name) # configurar el pin
        if pin is None: 
            print(f"Servo pin {servo_name} not found.")
            self.__is_pin_setup = False
            return
        self.__is_pin_setup = True
        value = self.value_within_range(initial_value)
        self.__valueServo = value
        self.__pin_servo = pin
        self.send_command(self._command_servomotor, pin, value) # Mandar valor por i2c a la esp32
            

    def control_servo(self, value_servo):
        """Control the servo with a specified value."""
        if not self.__is_pin_setup: 
            print("Pin has not been setup")
            return
        value = self.value_within_range(value_servo)
        self.__valueServo = value
        self.send_command(self._command_servomotor, self.__pin_servo, value) # Mandar el valor por i2c a la esp32
    