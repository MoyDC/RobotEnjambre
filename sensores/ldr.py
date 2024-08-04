import sys
import os
import time
from queue import Queue
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../sensores')))
from adcESP32 import adc_ESP32  # Asegúrate de que el módulo adcESP32 esté disponible

class SensorADC:
    def __init__(self, bus_number, address, pin_sensor, max_sizeQueue=3, delay=0.02):
        self.sensor = adc_ESP32(bus_number=bus_number, address=address)
        self.pin_sensor = pin_sensor
        self.queue = Queue(maxsize=max_sizeQueue)
        self.sensor.setup_adc_pin(self.sensor.get_adc_name_by_pin(pin_sensor))
        self._is_running = False
        self.__delay = delay
        
    def start(self):
        self._is_running = True
        while self._is_running:
            sensor_value, _ = self.sensor.read_adc()
            if sensor_value is not None:
                data = (f"LDR{self.pin_sensor}", sensor_value)
                if self.queue.full():
                    self.queue.get()  # Remove the oldest data if queue is full
                self.queue.put(data)
            time.sleep(self.__delay)  # Adjust as needed

    def stop(self):
        self._is_running = False
        print(f"LDR sensor pin {self.pin_sensor} stopped.")

    def get_data(self):
        if not self.queue.empty():
            return self.queue.get()
        else:
            data = ("LDR pin {self.pin_sensor}", -2)
            print("LDR pin {self.pin_sensor} - No data available")
            return data

