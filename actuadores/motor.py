import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../moreGPIO')))
from More_GPIO_ESP32 import MoreGpio_ESP32

class Motor(MoreGpio_ESP32):
    def __init__(self, bus_number=1, address=0x08, command_motor_I2C=0):
        super().__init__(bus_number, address)
        self._command_I2C = command_motor_I2C
        self._motor_options = {
            "motor_Stop": 1,
            "motor_Forward": 2,
            "motor_Reverse": 3
        }
        self.__value_SP_Motor = 0
        self._motor_configs = {}
        
    def get_motor_value(self) -> int:
        return self.__value_SP_Motor
    
    def get_motor_option(self, option_name):
        return self._motor_options.get(option_name)
    
    def get_motor_option_by_number(self, option_number):
        for name, pin in self._motor_options.items():
            if pin == option_number:
                return name
        return None  # Retornar None si no se encuentra el pin
    
    def get_all_motor_options(self):
        return self._motor_options

    #def setup_servo(self, motor_option, initial_value):
        # Asegurar que el valor esté en el rango 0-180
        #value = max(0, min(200, int(initial_value)))
        
        #Guardar el valor del servomotor
        #self.__value_SP_Motor = value
        
        # configurar el pin y mandar valor por i2c a la esp32
        #option = self._motor_options(motor_option)
        #if option is not None:
        #    self._motor_configs[motor_option] = {'option': option, 'value': value}
        #    self.send_command(self._command_I2C, pin, value)
        #else:
        #    print(f"Motor option {motor_option} not found.")

    def Stop(self, name="Motor"):
        # Asegurar que el valor esté en el rango 0-180
        value = 0
        
        #Guardar el valor del servomotor
        self.__value_SP_Motor = value
        
        # Mandar el valor por i2c a la esp32
        #for servo_name, config in self._servo_configs.items():
            #pin = config['pin']
        self.send_command(self._command_I2C, self._motor_options.get("motor_Stop"), value)
        
        print(f"{name} stopped.")
        #self._servo_configs[servo_name]['value'] = value
    
    def Forward(self, value_sp_motor=100):
        # Asegurar que el valor esté en el rango 0-180
        value = max(0, min(200, int(value_sp_motor)))
        
        #Guardar el valor del servomotor
        self.__value_SP_Motor = value
        
        # Mandar el valor por i2c a la esp32
        self.send_command(self._command_I2C, self._motor_options.get("motor_Forward"), value)
        
    def Reverse(self, value_sp_motor=100):
        # Asegurar que el valor esté en el rango 0-180
        value = max(0, min(200, int(value_sp_motor)))
        
        #Guardar el valor del servomotor
        self.__value_SP_Motor = value
        
        # Mandar el valor por i2c a la esp32
        self.send_command(self._command_I2C, self._motor_options.get("motor_Reverse"), value)