import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../actuadores')))
from pwmESP32 import pwm_ESP32
from outputESP32 import output_ESP32

# Definición de la clase Motor
class Motor(pwm_ESP32, output_ESP32):
    def __init__(self, bus_number=1, address=0x08):
        super().__init__(bus_number, address)
        self.__PinEN = None
        self.__PinIN1 = None
        self.__PinIN2 = None
    
    def setup_motor(self, pin_pwm_number_EN, pin_number_IN1, pin_number_IN2):
        self.__PinEN = pin_pwm_number_EN
        self.__PinIN1 = pin_number_IN1
        self.__PinIN2 = pin_number_IN2
        self.stop()
    
    def stop(self):
        if self.__PinEN is not None and self.__PinIN1 is not None and self.__PinIN2 is not None:
            pwm_pin_name = self.get_pwm_name_by_pin(self.__PinEN)
            output_pin_name1 = self.get_output_name_by_pin(self.__PinIN1)
            output_pin_name2 = self.get_output_name_by_pin(self.__PinIN2)
            
            if pwm_pin_name and output_pin_name1 and output_pin_name2:
                self.setup_pwm(pwm_pin_name, 0)
                self.setup_output(output_pin_name1, 0)
                self.setup_output(output_pin_name2, 0)
            else:
                print("Invalid pin configuration.")
        else:
            print("Motor pins are not properly set up.")
    
    def forward(self, pwm, StateIN1=1, StateIN2=0):
        if self.__PinEN is not None and self.__PinIN1 is not None and self.__PinIN2 is not None:
            pwm_pin_name = self.get_pwm_name_by_pin(self.__PinEN)
            output_pin_name1 = self.get_output_name_by_pin(self.__PinIN1)
            output_pin_name2 = self.get_output_name_by_pin(self.__PinIN2)
            
            if pwm_pin_name and output_pin_name1 and output_pin_name2:
                self.setup_pwm(pwm_pin_name, pwm)
                self.setup_output(output_pin_name1, StateIN1)
                self.setup_output(output_pin_name2, StateIN2)
            else:
                print("Invalid pin configuration.")
        else:
            print("Motor pins are not properly set up.")
    
    def reverse(self, pwm, StateIN1=0, StateIN2=1):
        if self.__PinEN is not None and self.__PinIN1 is not None and self.__PinIN2 is not None:
            pwm_pin_name = self.get_pwm_name_by_pin(self.__PinEN)
            output_pin_name1 = self.get_output_name_by_pin(self.__PinIN1)
            output_pin_name2 = self.get_output_name_by_pin(self.__PinIN2)
            
            if pwm_pin_name and output_pin_name1 and output_pin_name2:
                self.setup_pwm(pwm_pin_name, pwm)
                self.setup_output(output_pin_name1, StateIN1)
                self.setup_output(output_pin_name2, StateIN2)
            else:
                print("Invalid pin configuration.")
        else:
            print("Motor pins are not properly set up.")
