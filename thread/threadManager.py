import threading
import time

class ThreadManager:
    def __init__(self, Thread_motor1_speedController=None, Thread_motor2_speedController=None,
                 Thread_Led_Programa=None, Thread_lidar_sensor=None, Thread_sensors=None,
                 Thread_sensor_Infrarrojo=None, Thread_sensorBrujula=None, Thread_readADC_ESP32=None,
                 Thread_PrintDataSensors=None, Thread_Camara=None):
        self.threads = {}  # Diccionario para almacenar referencias de hilos
        self.motor1_speedController = Thread_motor1_speedController
        self.motor2_speedController = Thread_motor2_speedController
        self.Led_Programa = Thread_Led_Programa
        self.lidar_sensor = Thread_lidar_sensor
        self.sensors = Thread_sensors if Thread_sensors is not None else {}
        self.sensor_Infrarrojo = Thread_sensor_Infrarrojo
        self.sensorBrujula = Thread_sensorBrujula
        self.readADC_ESP32 = Thread_readADC_ESP32
        self.PrintDataSensors = Thread_PrintDataSensors
        self.Camara = Thread_Camara

    def init_thread(self, name, target, *args):
        if name not in self.threads:
            thread = threading.Thread(target=target, args=args)
            thread.start()
            self.threads[name] = thread
        else:
            print(f"Thread {name} is already running.")

    def init_all_threads(self):
        
        self.init_thread("Led_Programa", self.Led_Programa.blink)
        self.init_thread("lidar_sensor", self.lidar_sensor.start_reading)

        self.print_dots_with_delay(0.1)
        
        for name, sensor in self.sensors.items():
            self.init_thread(name, sensor.start_reading)
        
        self.print_dots_with_delay(0.5)
        
        self.init_thread("sensor_Infrarrojo", self.sensor_Infrarrojo.start_reading)
        self.init_thread("sensorBrujula", self.sensorBrujula.start_reading)
        self.init_thread("readADC_ESP32", self.readADC_ESP32.start)
        self.init_thread("motor1_speedController", self.motor1_speedController.control_loop)
        self.init_thread("motor2_speedController", self.motor2_speedController.control_loop)
        
        self.print_dots_with_delay(0.5)
        
        self.init_thread("Camara", self.Camara.start)
        
        self.print_dots_with_delay(0.5)
        
        self.init_thread("PrintDataSensors", self.PrintDataSensors.start)

    def print_dots_with_delay(self, delay):
        start_time = time.time()
        while time.time() - start_time < delay:
            print("Starting" + "." * int((time.time() - start_time) * 10), end='\r')
            time.sleep(0.1)
        print("Starting" + "." * int(delay * 10))  # Print final state

    def stop_thread(self, name):
        if name in self.threads:
            thread = self.threads.pop(name)
            # Aquí deberías implementar una manera segura de detener el hilo
            # Por ejemplo, si el hilo está en un bucle, usa una variable de condición
            thread.join()  # Espera a que el hilo termine su ejecución
            print(f"Thread {name} has been stopped.")
        else:
            print(f"Thread {name} is not running.")

    def stop_all_threads(self):
        for name in list(self.threads.keys()):
            self.stop_thread(name)
            #name.join()
        #for thread in self.threads:
            #thread.join()

# Uso del ThreadManager
# Asegúrate de pasar las instancias necesarias al inicializar el ThreadManager
# motor1_speedController, motor2_speedController, Led_Programa, lidar_sensor, sensors, sensor_Infrarrojo, sensorBrujula, readADC_ESP32, PrintDataSensors
#thread_manager = ThreadManager(motor1_speedController, motor2_speedController, Led_Programa, lidar_sensor, sensors, sensor_Infrarrojo, sensorBrujula, readADC_ESP32, PrintDataSensors)

# Iniciar los hilos
#thread_manager.init_all_threads(data_queue1, data_queue2)

# Para detener un hilo específico
# thread_manager.stop_thread("sensor_Infrarrojo")

# Para detener todos los hilos
# thread_manager.stop_all_threads()
