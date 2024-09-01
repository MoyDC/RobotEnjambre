import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../hardware')))
from hardware.moreGPIO.More_GPIO_ESP32 import MoreGpio_ESP32

class Motor(MoreGpio_ESP32):
    def __init__(self, bus_number=1, address=0x08, command_motor_I2C=0):
        super().__init__(bus_number, address)
        self._command_I2C = command_motor_I2C
        self._motor_options = {
            "motor_Stop": 1,
            "motor_Forward": 2,
            "motor_Reverse": 3
        }
        self.__value_Stop = 0
        self.__value_Max = 200
        self.__value_Min = 0
        self.__value_SP_Motor = 0
        self._motor_configs = {}
        
    def get_motor_value(self) -> int:
        """Get the current setpoint value of the motor."""
        return self.__value_SP_Motor
    
    def get_motor_option(self, option_name):
        """Get the motor option value by name."""
        return self._motor_options.get(option_name)
    
    def get_motor_option_by_number(self, option_number):
        """Get the motor option name by its numeric value."""
        for name, pin in self._motor_options.items():
            if pin == option_number:
                return name # Retornar el nombre
        return None  # Retornar None si no se encuentra el pin
    
    def get_all_motor_options(self):
        """Get all motor options."""
        return self._motor_options

    def value_within_range(self, value):
        """Ensure the value is within the defined range."""
        return max(self.__value_Min, min(self.__value_Max, int(value))) # Asegurar que el valor esté en el rango 0-200
    
    def stop(self, name="Motor"):
        """Stop the motor by sending the stop command."""
        self.__value_SP_Motor = self.__value_Stop # Guardar el valor del motor
        self.send_command(self._command_I2C, self._motor_options.get("motor_Stop"), self.__value_Stop) # Mandar el comando
        print(f"{name} stopped.")
    
    def Forward(self, value_sp_motor=100):
        """Set the motor to move forward with a specified value."""
        value = self.value_within_range(value_sp_motor)
        self.__value_SP_Motor = value # Guardar el valor del servomotor
        self.send_command(self._command_I2C, self._motor_options.get("motor_Forward"), value) # Mandar el valor por i2c a la esp32
        
    def Reverse(self, value_sp_motor=100):
        """Set the motor to move in reverse with a specified value."""
        value = self.value_within_range(value_sp_motor)
        self.__value_SP_Motor = value #Guardar el valor del servomotor
        self.send_command(self._command_I2C, self._motor_options.get("motor_Reverse"), value) # Mandar el valor por i2c a la esp32