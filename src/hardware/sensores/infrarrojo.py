import time
from gpiozero import DigitalInputDevice
from queue import Queue

class SensorInfrarrojo:
    def __init__(self, pin: int, max_sizeQueue=3):
        self.sensor = DigitalInputDevice(pin=pin)
        self.queue = Queue(maxsize=max_sizeQueue)
        self._running = True
        self.__pin = pin

    def __add_data_to_Queue(self, data):
        """Add sensor data to the queue."""
        if self.queue.full():
            self.queue.get()  # Remove the oldest data to maintain the size
        self.queue.put(data)

    def start_reading(self, delay_Reading=0.05):
        """Continuously read data from the sensor and add it to the queue."""
        while self._running:
            try:
                if not self.sensor.value:
                    datosSensorInfrarrojo = ("SensorObstaculos", 1)
                else:
                    datosSensorInfrarrojo = ("SensorObstaculos", 0)
                self.__add_data_to_Queue(datosSensorInfrarrojo) # Almacenar datos al Queue
                time.sleep(delay_Reading)  # Espera para no saturar la lectura

            except Exception as e:
                print(f"Error en la lectura del sensor infrarrojo: {e}")
                self.queue.put(("SensorObstaculos", -1))  # Agrega un valor de error

    def stop(self):
        """Stop the sensor reading loop."""
        self._running = False
        print(f"Sensor infrared pin {self.__pin} stopped")

    def get_data(self):
        """Retrieve data from the queue."""
        if self.queue.empty():
            print(f"SensorObstaculos pin {self.__pin} - No data available")
            return ("SensorObstaculos", -2)
        return self.queue.get()
            
