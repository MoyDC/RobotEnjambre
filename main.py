import time
import threading
from threading import Thread
from sensores.led import LedController
from sensores.ultrasonicos import UltrasonicSensor
from sensores.lidar import LidarSensor
from sensores.infrarrojo import SensorInfrarrojo
from sensores.brujula import Brujula_MechaQMC5883
from sensores.ldr import SensorADC
from actuadores.motor_SpeedController_PID import create_motor_controller, data_queue1, data_queue2
from actuadores.servomotor import ServoController

#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
# Función para formatear y imprimir los datos de los sensores
class SensorDataFormatter:
    def __init__(self, sensors, lidar_sensor, sensor_Infrarrojo, sensorBrujula, LDR_Der, LDR_Izq):
        self.sensors = sensors
        self.lidar_sensor = lidar_sensor
        self.sensor_Infrarrojo = sensor_Infrarrojo
        self.sensorBrujula = sensorBrujula
        self.LDR_Der = LDR_Der
        self.LDR_Izq = LDR_Izq
        self.contador_datos = 0
        self._is_running = False
        self._thread = None

    def format_data(self):
        self.contador_datos += 1

        S1 = self.sensors.get(sensorsNames[0]).get_data()
        S2 = self.sensors.get(sensorsNames[1]).get_data()
        S3 = self.sensors.get(sensorsNames[2]).get_data()
        S4 = self.sensors.get(sensorsNames[3]).get_data()
        Lidar_cm = self.lidar_sensor.get_data()
        Infrarrojo = self.sensor_Infrarrojo.get_data()
        AngBrujula = self.sensorBrujula.get_data()
        SensorLDR1 = self.LDR_Der.get_data()
        SensorLDR2 = self.LDR_Izq.get_data()

        formatted_data = (
            f"Cont {self.contador_datos}: "
            f"{S1[0]}: {S1[1]:.2f} cm - "
            f"{S2[0]}: {S2[1]:.2f} cm - "
            f"{S3[0]}: {S3[1]:.2f} cm - "
            f"{S4[0]}: {S4[1]:.2f} cm - "
            f"Lidar: {Lidar_cm[1]} cm - "
            f"Infra: {Infrarrojo[1]} - "
            f"Bruj: {AngBrujula[1]:.2f} - "
            f"LDR1: {SensorLDR1[1]} - "
            f"LDR2: {SensorLDR2[1]}"
        )
        return formatted_data

    def run(self, delay=0.05, Run=True):
        self._is_running = True
        time.sleep(0.5)
        while self._is_running and Run==True:
            start_time = time.time()
            formatted_data = self.format_data()
            print(formatted_data)
            time.sleep(delay)  # Ajusta el tiempo de espera según sea necesario
            end_time = time.time()
            elapsed_time = end_time - start_time
            #print(f"Tiempo transcurrido: {elapsed_time} segundos")  # Tiempo aproximado 0.05s

    def start(self):
        if not self._thread or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.run)
            self._thread.start()

    def stop(self):
        self._is_running = False
        if self._thread:
            self._thread.join()
        print("Proceso de recopilación de datos detenido.")
        
        

#---------------------------------------------------------------------------------------------------------------
        
# Funciona para inicializar todos los hilos
threads = [] # Lista global para almacenar referencias de hilos
def init_threads():
    thread_controlSpeed1 = threading.Thread(target=motor1_speedController.control_loop, args=(data_queue1,))
    thread_controlSpeed2 = threading.Thread(target=motor2_speedController.control_loop, args=(data_queue2,))

    thread_controlSpeed1.start()
    thread_controlSpeed2.start()
    threads.extend([thread_controlSpeed1, thread_controlSpeed2])
    
     # Iniciar el hilo del LED
    thread_ledPrograma= threading.Thread(target=Led_Programa.blink)
    thread_ledPrograma.start()
    threads.append(thread_ledPrograma)
    
    # Iniciar el hilo de lectura del sensor lidar
    thread_lidar = Thread(target=lidar_sensor.start_reading)
    thread_lidar.start()
    threads.append(thread_lidar)
    
    time.sleep(0.5)
    
    # Iniciar hilos para leer los datos de los sensores
    for name, sensor in sensors.items():
        thread = Thread(target=sensor.start_reading)
        thread.start()
        threads.append(thread)
    
    time.sleep(0.5)
    
    # Iniciar el hilo de lectura del sensor infrarrojo
    thread_sensorInfrarrojo = Thread(target=sensor_Infrarrojo.start_reading)
    thread_sensorInfrarrojo.start()
    threads.append(thread_sensorInfrarrojo)
    
    # Iniciar el hilo de lectura de la brujula digital
    thread_BlujulaDigital = Thread(target=sensorBrujula.start_reading)
    thread_BlujulaDigital.start()
    threads.append(thread_BlujulaDigital)
    
    # Iniciar el hilo de lectura del sensor LDR
    thread_sensorLDR1 = Thread(target=LDR_Der.start)
    thread_sensorLDR2 = Thread(target=LDR_Izq.start)
    
    thread_sensorLDR1.start()
    thread_sensorLDR2.start()
    #threads.append(thread_sensorLDR1)
    threads.extend([thread_sensorLDR1, thread_sensorLDR2])
    
    # Iniciar el hilo de impresión de datos
    thread_print_data = Thread(target=PrintDataSensors.start)
    thread_print_data.start()
    threads.append(thread_print_data)

#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------

# Crear una instancia de LedController para el led Programa
pinLed = 18
delayBlink = 0.25
Led_Programa = LedController(pinLed, delayBlink)
    
#---------------------------------------------------------------------------------------------------------------

#Crear estancia del sensor Lidar
lidar_sensor = LidarSensor(serial_port="/dev/ttyAMA0", baud_rate=115200, max_queue_size=3)
lidar_sensor.initialize(frame_rate=50)

#---------------------------------------------------------------------------------------------------------------

# Configuración de los sensores Ultrasonicos
sensorsNames = ["S1", "S2", "S3", "S4"]
sensor_configs = [
    {"name": sensorsNames[0], "echo": 16, "trigger": 26},
    {"name": sensorsNames[1], "echo": 5, "trigger": 6},
    {"name": sensorsNames[2], "echo": 7, "trigger": 1},
    {"name": sensorsNames[3], "echo": 25, "trigger": 8}
]
# Crear instancias de los sensores y almacenarlas en un diccionario
sensors = {config['name']: UltrasonicSensor(config['echo'], config['trigger'], config['name']) for config in sensor_configs}

#---------------------------------------------------------------------------------------------------------------

# Inicializar el sensor infrarrojo
sensor_Infrarrojo = SensorInfrarrojo(pin=20)

#---------------------------------------------------------------------------------------------------------------

sensorBrujula = Brujula_MechaQMC5883()
sensorBrujula.init()

#---------------------------------------------------------------------------------------------------------------

# Configuración de los sensores
LDR_Der = SensorADC(bus_number=1, address=0x08, pin_sensor=36)
LDR_Izq = SensorADC(bus_number=1, address=0x08, pin_sensor=39)

#---------------------------------------------------------------------------------------------------------------

PrintDataSensors = SensorDataFormatter(sensors, lidar_sensor, sensor_Infrarrojo, sensorBrujula, LDR_Der, LDR_Izq)

#---------------------------------------------------------------------------------------------------------------  
    
# Configuración del sistema de control de motores usando PID
Kp = 2
Ki = 6
Kd = 0.01
max_output = 500
#Pines motor 1
EN_1 = 17
IN1_1 = 23
IN2_1 = 19
PinEncoder_1 = 27
#Pines motor 2
EN_2 = 16
IN1_2 = 18
IN2_2 = 5
PinEncoder_2 = 10
motor1_speedController = create_motor_controller(1, 0x08, EN_1, IN1_1, IN2_1, PinEncoder_1, Kp, Ki, Kd, max_output)
motor2_speedController = create_motor_controller(1, 0x08, EN_2, IN1_2, IN2_2, PinEncoder_2, Kp, Ki, Kd, max_output)

#---------------------------------------------------------------------------------------------------------------

# Configuración de los servomotores
pinServo1 = 4
pinServo2 = 13
pinServo3 = 15
servo1 = ServoController(bus_number=1, address=0x08)
servo2 = ServoController(bus_number=1, address=0x08)
servo3 = ServoController(bus_number=1, address=0x08)

#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------

# Main
if __name__ == "__main__":
    try:
        #Inicializar todos los hilos
        init_threads()
        #
        
        # Configuracion inicial motores
        motor1_speedController.set_setpoint(150)
        motor2_speedController.set_setpoint(150)
        
        # Configuracion inicial servos
        servo1.setup_servo(servo1.get_servo_name_by_pin(pinServo1), 10)
        servo2.setup_servo(servo2.get_servo_name_by_pin(pinServo2), 150)
        servo3.setup_servo(servo3.get_servo_name_by_pin(pinServo3), 100)
        
        PrintDataSensors.stop()

        while True:
            if not data_queue1.empty() and not data_queue2.empty():
                setpoint1, pv1 = data_queue1.get()
                setpoint2, pv2 = data_queue2.get()
                print(f"Setpoint1: {setpoint1:.2f}, PV1: {pv1:.2f} | Setpoint2: {setpoint2:.2f}, PV2: {pv2:.2f}")
                
            #print(f"Servo1: {servo1.get_servo_value()}, Servo2: {servo2.get_servo_value()} | Servo3: {servo3.get_servo_value()}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nInterrupción recibida (Ctrl + C), deteniendo todos los hilos...")
        PrintDataSensors.stop()
        Led_Programa.stop()
        lidar_sensor.stop_reading()
        sensors.get(sensorsNames[0]).stop()
        sensors.get(sensorsNames[1]).stop()
        sensors.get(sensorsNames[2]).stop()
        sensors.get(sensorsNames[3]).stop()
        sensor_Infrarrojo.stop()
        sensorBrujula.stop()
        LDR_Der.stop()
        LDR_Izq.stop()
        motor1_speedController.stop(name="Motor 1")
        motor2_speedController.stop(name="Motor 2")
        
    finally:
        for thread in threads:
            thread.join()
        print("Programa terminado limpiamente.")
        
#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------