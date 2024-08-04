import sys
import os
import time
from queue import Queue
from threading import Thread
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../moreGPIO')))
from More_GPIO_ESP32 import MoreGpio_ESP32

class adc_ESP32(MoreGpio_ESP32):
    def __init__(self, bus_number=1, address=0x08, max_sizeQueue=3, delay=0.009):
        super().__init__(bus_number, address)
        self._adc_pins = {
            "ADCPin36": 36,
            "ADCPin39": 39,
            "ADCPin34": 34,
            "ADCPin35": 35
        }
        self.queues = {pin: Queue(maxsize=max_sizeQueue) for pin in self._adc_pins}
        self._is_running = False
        self.__delay = delay
        
    def get_adc_pin(self, pin_name):
        return self._adc_pins.get(pin_name)

    def get_adc_name_by_pin(self, pin_number):
        for name, pin in self._adc_pins.items():
            if pin == pin_number:
                return name
        return None
    
    def get_all_adc_pins(self):
        return self._adc_pins
    
    def read_adc(self, cont=0, delay=0.00001, Pin=None):
        if Pin is None:
            print("ADC pin not set.")
            return None
        else:
            start_time = time.time()
            command = self.command_adc
            sensor_value, idPinReturn = self.read_command(command, Pin, cont, delay)
            end_time = time.time()
            elapsed_time = end_time - start_time
            #print(f"{sensor_value} - Tiempo transcurrido: {elapsed_time} segundos")  
            return sensor_value, idPinReturn

    def start(self, contADC=0, delayADC_I2C=0.00001):
        self._is_running = True
        while self._is_running:
            start_time = time.time()
            for pin_name, pin in self._adc_pins.items():
                sensor_value, _ = self.read_adc(cont=contADC, delay=delayADC_I2C, Pin=pin)
                if sensor_value is not None:
                    if self.queues[pin_name].full():
                        self.queues[pin_name].get()  # Remove the oldest data if queue is full
                    self.queues[pin_name].put((pin_name, sensor_value), block=False)
                time.sleep(self.__delay)
            end_time = time.time()
            elapsed_time = end_time - start_time
            #print(f"Tiempo transcurrido: {elapsed_time} segundos")
    
    def stop(self):
        self._is_running = False
        print("ADC readings stopped.")

    def get_dataADC_LDR1(self):
        if not self.queues["ADCPin36"].empty():
            return self.queues["ADCPin36"].get()
        else:
            data = ("ADCPin36", -2)
            print("ADC LDR1 - No data available")
            return data

    def get_dataADC_LDR2(self):
        if not self.queues["ADCPin39"].empty():
            return self.queues["ADCPin39"].get()
        else:
            data = ("ADCPin39", -2)
            print("ADC LDR2 - No data available")
            return data

    def get_dataADC1(self):
        if not self.queues["ADCPin34"].empty():
            return self.queues["ADCPin34"].get()
        else:
            data = ("ADCPin34", -2)
            print("ADC1 - No data available")
            return data

    def get_dataADC2(self):
        if not self.queues["ADCPin35"].empty():
            return self.queues["ADCPin35"].get()
        else:
            data = ("ADCPin35", -2)
            print("ADC2 - No data available")
            return data

