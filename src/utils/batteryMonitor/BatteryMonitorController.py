from gpiozero import RGBLED
from time import sleep

class BatteryMonitorController:
    def __init__(self, adc_instance, adc_max_value, adc1_target_value, adc2_target_value, 
                 red_pin_RGB1, green_pin_RGB1, blue_pin_RGB1, red_pin_RGB2, green_pin_RGB2, blue_pin_RGB2):
        self.__is_running = False
        self.__adc_instance = adc_instance
        self.__adc_max_value = adc_max_value
        self.__adc1_target_value = adc1_target_value
        self.__adc2_target_value = adc2_target_value 
        self.__adc1_current_value = adc_max_value
        self.__adc2_current_value = adc_max_value 
        self.__adc1_last_value = adc_max_value
        self.__adc2_last_value = adc_max_value 
        self.__led_RGB1 = RGBLED(red=red_pin_RGB1, green=green_pin_RGB1, blue=blue_pin_RGB1)
        self.__led_RGB2 = RGBLED(red=red_pin_RGB2, green=green_pin_RGB2, blue=blue_pin_RGB2)
        self.__colors_RGB = { # Define el array con los colores
            "green": (0, 1, 0),   # Verde (0, 1, 0)
            "yellow": (1, 1, 0), # Amarillo (1, 1, 0)
            "red": (1, 0, 0)     # Rojo (1, 0, 0)
        }

    def is_voltage_adc1_in_range(self):
        """Checks if the current voltage of ADC1 is above or equal to the target value."""
        if self.__adc1_current_value >= self.__adc1_target_value:
            return True
        return False
    
    def is_voltage_adc2_in_range(self):
        """Checks if the current voltage of ADC2 is above or equal to the target value."""
        if self.__adc2_current_value >= self.__adc2_target_value:
            return True
        return False
    
    def set_color_RGB(self, led_name, color):
        """Sets the color of the specified RGB LED."""
        if not color in self.__colors_RGB:
            print(f"Color '{color}' no reconocido")
            return
        if led_name == "RGB1":
            self.__led_RGB1.color = self.__colors_RGB[color]
        elif led_name == "RGB2":
            self.__led_RGB2.color = self.__colors_RGB[color]
        else:
            print(f"LED '{led_name}' no reconocido")
        #print(f"Color '{color}' reconocido para LED {led_name}")            

    def update_color_based_on_adc(self, led_name, adc_value, adc_max, target_adc):
        """Updates the color of the specified RGB LED based on the ADC value."""
        mid_value = (adc_max + target_adc) / 2
        
        if mid_value <= adc_value <= adc_max:
            self.set_color_RGB(led_name, "green")  # ADC en el rango de target a adc_max
        elif target_adc <= adc_value <= mid_value:
            self.set_color_RGB(led_name, "yellow")  # ADC entre target y la mitad
        else:
            self.set_color_RGB(led_name, "red")  # ADC por debajo del target

    def start(self):
        """Starts the monitoring process and updates LED colors based on ADC values."""
        self.__is_running = True
        while self.__is_running:
            adc1_value = self.__adc_instance.get_dataADC1()
            adc2_value = self.__adc_instance.get_dataADC2()
            adc1_value = int(adc1_value[1])
            adc2_value = int(adc2_value[1])
            self.__adc1_current_value = adc1_value
            self.__adc2_current_value = adc2_value
            self.__adc1_last_value = adc1_value
            self.__adc2_last_value = adc2_value
            self.update_color_based_on_adc("RGB1", adc1_value, self.__adc_max_value, self.__adc1_target_value)
            self.update_color_based_on_adc("RGB2", adc2_value, self.__adc_max_value, self.__adc2_target_value)
            sleep(0.1)

    def indicate_battery_limit(self):
        """Indicates the battery limit status by updating LED colors based on the last ADC values."""
        self.update_color_based_on_adc("RGB1", self.__adc1_last_value, self.__adc_max_value, self.__adc1_target_value)
        self.update_color_based_on_adc("RGB2", self.__adc2_last_value, self.__adc_max_value, self.__adc2_target_value)

    def stop(self):
        """Stops the monitoring process."""
        self.__is_running = False