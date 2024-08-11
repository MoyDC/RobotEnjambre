import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../sensores')))
from led import LedController
from ultrasonicos import UltrasonicSensor
from lidar import LidarSensor
from infrarrojo import SensorInfrarrojo
from brujula import Brujula_MechaQMC5883
from adcESP32 import adc_ESP32

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../actuadores')))
from motor_SpeedController_PID import create_motor_controller#, data_queue1, data_queue2
from servomotor import ServoController

#---------------------------------------------------------------------------------------------------------------

# Crear una instancia de LedController para el led Programa
pinLed = 18
delayBlink = 0.25
Led_Programa = LedController(pinLed, delayBlink)

print("*** Led Program - setup completed. ***")

#---------------------------------------------------------------------------------------------------------------

#Crear estancia del sensor Lidar
lidar_sensor = LidarSensor(serial_port="/dev/ttyAMA0", baud_rate=115200, max_queue_size=3)
lidar_sensor.initialize(frame_rate=50)

print("*** Lidar Sensor - setup completed. ***")

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

print("*** Ultrasonic Sensors - setup completed. ***")

#---------------------------------------------------------------------------------------------------------------

# Crear instancia para el sensor infrarrojo
sensor_Infrarrojo = SensorInfrarrojo(pin=20)

print("*** Infrared sensor - setup completed. ***")

#---------------------------------------------------------------------------------------------------------------

# Crear instancia para el sensor de la brujula digital
sensorBrujula = Brujula_MechaQMC5883()
sensorBrujula.init()

print("*** Compass sensor - setup completed. ***")

#---------------------------------------------------------------------------------------------------------------

# Crear instancia para leer el adc de la esp32
readADC_ESP32 = adc_ESP32(bus_number=1, address=0x08, delay=0.01)

print("*** ADC sensor - setup completed. ***")

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

print("*** Motor 1 - setup completed. ***")
print("*** Motor 2 - setup completed. ***")

#---------------------------------------------------------------------------------------------------------------

# Configuración de los servomotores
pinServo1 = 4
pinServo2 = 13
pinServo3 = 15
servo1 = ServoController(bus_number=1, address=0x08)
servo2 = ServoController(bus_number=1, address=0x08)
servo3 = ServoController(bus_number=1, address=0x08)

servo1.setup_servo(servo1.get_servo_name_by_pin(pinServo1), 0)
servo2.setup_servo(servo2.get_servo_name_by_pin(pinServo2), 0)
servo3.setup_servo(servo3.get_servo_name_by_pin(pinServo3), 0)

print("*** Servomotor 1 - setup completed. ***")
print("*** Servomotor 2 - setup completed. ***")
print("*** Servomotor 3 - setup completed. ***")

#---------------------------------------------------------------------------------------------------------------

