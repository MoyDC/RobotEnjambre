import threading
import time

class ThreadManager:
    def __init__(self, Thread_Led_Programa=None, Thread_lidar_sensor=None, Thread_sensors=None,
                 Thread_sensor_Infrarrojo=None, Thread_sensorBrujula=None, Thread_readADC_ESP32=None,
                 Thread_PrintDataSensors=None, Thread_BatteryMonitor=None): #, Thread_Camara=None, ,
        self.threads = {}  # Diccionario para almacenar referencias de hilos
        self.Led_Programa = Thread_Led_Programa
        self.lidar_sensor = Thread_lidar_sensor
        self.sensors = Thread_sensors if Thread_sensors is not None else {}
        self.sensor_Infrarrojo = Thread_sensor_Infrarrojo
        self.sensorBrujula = Thread_sensorBrujula
        self.readADC_ESP32 = Thread_readADC_ESP32
        self.PrintDataSensors = Thread_PrintDataSensors
        self.BatteryMonitor = Thread_BatteryMonitor

    def init_thread(self, name, target, *args):
        if name not in self.threads:
            print(f"Start thread: {name}")
            thread = threading.Thread(target=target, args=args)
            thread.start()
            self.threads[name] = thread
        else:
            print(f"Thread {name} is already running.")

    def init_all_threads(self):
        """Initialize and start all threads if their corresponding objects are not None."""
        # Check if each thread object is not None before initializing
        if self.Led_Programa is None:
            print("Led_Programa is None, skipping initialization.")
            return False
        self.init_thread("Led_Programa", self.Led_Programa.blink)

        if self.lidar_sensor is None:
            print("lidar_sensor is None, skipping initialization.")
            return False
        self.init_thread("lidar_sensor", self.lidar_sensor.start_reading)

        self.print_dots_with_delay(0.1)
        for name, sensor in self.sensors.items():
            if sensor is None:
                print(f"Sensor {name} is None, skipping initialization.")
                return False
            self.init_thread(name, sensor.start_reading)  

        self.print_dots_with_delay(0.5)
        if self.sensor_Infrarrojo is None:
            print("sensor_Infrarrojo is None, skipping initialization.")
        self.init_thread("sensor_Infrarrojo", self.sensor_Infrarrojo.start_reading)

        if self.sensorBrujula is None:
            print("sensorBrujula is None, skipping initialization.")
            return False
        self.init_thread("sensorBrujula", self.sensorBrujula.start_reading)  

        if self.readADC_ESP32 is None:
            print("readADC_ESP32 is None, skipping initialization.")
            return False
        self.init_thread("readADC_ESP32", self.readADC_ESP32.start)

        self.print_dots_with_delay(0.5)
        if self.PrintDataSensors is None:
            print("PrintDataSensors is None, skipping initialization.")
            return False
        self.init_thread("PrintDataSensors", self.PrintDataSensors.start) 
        
        if self.BatteryMonitor is None:
            print("BatteryMonitor is None, skipping initialization.")
            return False
        self.init_thread("BatteryMonitor", self.BatteryMonitor.start) 

        return True

    def print_dots_with_delay(self, delay):
        start_time = time.time()
        while time.time() - start_time < delay:
            print("Starting" + "." * int((time.time() - start_time) * 10), end='\r')
            time.sleep(0.1)
        print("Starting" + "." * int(delay * 10))  # Print final state

    def stop_thread(self, name):
        if name in self.threads:
            thread = self.threads.pop(name)
            thread.join()  # Espera a que el hilo termine su ejecución
            print(f"Thread {name} has been stopped.")
        else:
            print(f"Thread {name} is not running.")

    def stop_all_threads(self):
        if self.Led_Programa is not None:
            self.Led_Programa.stop()
        if self.lidar_sensor is not None:
            self.lidar_sensor.stop()
        for name, sensor in self.sensors.items():
            if sensor is not None:
                sensor.stop()
        if self.sensor_Infrarrojo is not None:
            self.sensor_Infrarrojo.stop()
        if self.sensorBrujula is not None:
            self.sensorBrujula.stop()
        if self.readADC_ESP32 is not None:
            self.readADC_ESP32.stop()
        if self.PrintDataSensors is not None:
            self.PrintDataSensors.stop()
        if self.BatteryMonitor is not None:
            self.BatteryMonitor.stop()
            
        print(" ")
        for name in list(self.threads.keys()):
            self.stop_thread(name)
        print(" ")

