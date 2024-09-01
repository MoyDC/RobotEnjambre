import sys
import os
import time
from queue import Queue
from threading import Thread
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../hardware')))
from hardware.moreGPIO.More_GPIO_ESP32 import MoreGpio_ESP32

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
        """Get the ADC pin number by pin_name."""
        return self._adc_pins.get(pin_name)

    def get_adc_name_by_pin(self, pin_number):
        """Get the ADC pin name by pin_number."""
        for name, pin in self._adc_pins.items():
            if pin == pin_number:
                return name
        return None
    
    def get_all_adc_pins(self):
        """Get all ADC pin names and their corresponding numbers."""
        return self._adc_pins
    
    def __add_data_to_Queue(self, pin_name, sensor_value):
        """Add sensor data to the appropriate queue."""
        if pin_name not in self.queues: # Ensure the queue exists for the given pin_name
            return (f"No queue found for pin name: {pin_name}")
        queue = self.queues[pin_name]
        if queue.full(): 
            queue.get()  # Remove the oldest data if queue is full
        queue.put((pin_name, sensor_value), block=False)
    
    def read_adc(self, cont=0, delay=0.00001, Pin=None):
        """Read data from an ADC pin."""
        if Pin is None:
            print("ADC pin not set.")
            return None, None
        command = self._command_adc
        sensor_value, idPinReturn = self.read_command(command, Pin, cont, delay)
        return sensor_value, idPinReturn

    def start(self, contADC=0, delayADC_I2C=0.00001):
        """Start reading ADC data continuously."""
        self._is_running = True
        while self._is_running:
            for pin_name, pin in self._adc_pins.items():
                sensor_value, _ = self.read_adc(cont=contADC, delay=delayADC_I2C, Pin=pin)
                if sensor_value is not None: self.__add_data_to_Queue(pin_name, sensor_value)
                time.sleep(self.__delay)    
                
    def stop(self):
        """Stop reading ADC data."""
        self._is_running = False
        print("ADC readings stopped.")

    def get_dataADC_LDR1(self):
        """Get the latest data from ADC pin 36."""
        if self.queues["ADCPin36"].empty():
            print("ADC LDR1 - No data available")
            return ("ADCPin36", -2)   
        return self.queues["ADCPin36"].get()

    def get_dataADC_LDR2(self):
        """Get the latest data from ADC pin 39."""
        if self.queues["ADCPin39"].empty():
            print("ADC LDR2 - No data available")
            return ("ADCPin39", -2)
        return self.queues["ADCPin39"].get()        

    def get_dataADC1(self):
        """Get the latest data from ADC pin 34."""
        if self.queues["ADCPin34"].empty():
            print("ADC1 - No data available")
            return ("ADCPin34", -2)
        return self.queues["ADCPin34"].get()    

    def get_dataADC2(self):
        """Get the latest data from ADC pin 35."""
        if self.queues["ADCPin35"].empty():
            print("ADC2 - No data available")
            return ("ADCPin35", -2)
        return self.queues["ADCPin35"].get()
            

