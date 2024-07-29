import time
from queue import Queue
from gpiozero import DistanceSensor

class UltrasonicSensor:
    def __init__(self, echo_pin: int, trigger_pin: int, name: str, max_sizeQueue=3):
        self.sensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin)
        self.queue = Queue(maxsize=max_sizeQueue)
        self._running = True
        self.name = name

    def start_reading(self, _delayUltrasonico_=0.05):
        delay = _delayUltrasonico_
        while self._running:
            try:
                distance_cm = self.sensor.distance * 100
                data = (self.name, distance_cm)
                if self.queue.full():
                    self.queue.get() # Remove the oldest data
                self.queue.put(data, block=False)
                time.sleep(delay)
            except Exception as e:
                print(f"{self.name} - Error reading data from: {e}")
                data = (self.name, -1)
                self.queue.put(data)

    def stop(self):
        self._running = False
        print(f"Sensor {self.name} stopped.")

    def get_data(self):
        if not self.queue.empty():
            return self.queue.get()
        else:
            data = (self.name, -2)
            print(f"{self.name} - No data available")
            return data
        