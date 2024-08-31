import time
from gpiozero import DigitalInputDevice
from queue import Queue
from threading import Thread, Lock

class SensorInfrarrojo:
    def __init__(self, pin: int, max_sizeQueue=3):
        self.sensor = DigitalInputDevice(pin=pin)
        self.queue = Queue(maxsize=max_sizeQueue)
        self._running = True
        self.__pin = pin

    def start_reading(self, delay_Reading=0.05):
        while self._running:
            try:
                if not self.sensor.value:
                    datosSensorInfrarrojo = ("SensorObstaculos", 1)
                else:
                    datosSensorInfrarrojo = ("SensorObstaculos", 0)
                
                # Almacenar datos al Queue
                if self.queue.full():
                    self.queue.get()  # Remove the oldest data
                self.queue.put(datosSensorInfrarrojo)
                
                time.sleep(delay_Reading)  # Espera para no saturar la lectura
            except Exception as e:
                print(f"Error en la lectura del sensor infrarrojo: {e}")
                self.queue.put(("SensorObstaculos", -1))  # Agrega un valor de error

    def stop(self):
        self._running = False
        print(f"Sensor infrared pin {self.__pin} stopped")

    def get_data(self):
        if not self.queue.empty():
            return self.queue.get()
        else:
            data = ("SensorObstaculos", -2)
            print(f"SensorObstaculos pin {self.__pin} - No data available")
            return data
