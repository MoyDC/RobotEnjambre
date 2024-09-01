import time
from queue import Queue
from gpiozero import DistanceSensor

class UltrasonicSensor:
    def __init__(self, echo_pin, trigger_pin, name, max_sizeQueue=3):
        self.sensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin)
        self.queue = Queue(maxsize=max_sizeQueue)
        self._running = True
        self.name = name

    def __add_data_to_Queue(self, data):
        """Add sensor data to the queue."""
        if self.queue.full():
            self.queue.get()  # Remove the oldest data to maintain the size
        self.queue.put(data) 

    def start_reading(self, _delayUltrasonico_=0.05):
        """Start reading data from the Ultrasonic sensors."""
        delay = _delayUltrasonico_
        while self._running:
            try:
                distance_cm = self.sensor.distance * 100
                data = (self.name, distance_cm)
                self.__add_data_to_Queue(data)
                time.sleep(delay)
            except Exception as e:
                print(f"{self.name} - Error reading data from: {e}")
                data = (self.name, -1)
                self.queue.put(data)

    def stop(self):
        """Stop the reading process."""
        self._running = False
        print(f"Sensor {self.name} stopped.")

    def get_data(self):
        """Get the latest data from the queue."""
        if self.queue.empty():
            print(f"{self.name} - No data available")
            return (self.name, -2)
        return self.queue.get()
            
        