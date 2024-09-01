import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../hardware')))
from hardware.sensores.led import LedController
from hardware.sensores.ultrasonicos import UltrasonicSensor
from hardware.sensores.lidar import LidarSensor
from hardware.sensores.infrarrojo import SensorInfrarrojo
from hardware.sensores.brujula import Brujula_MechaQMC5883
from hardware.sensores.adcESP32 import adc_ESP32

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../hardware')))
from hardware.actuadores.motor import Motor#, data_queue1, data_queue2
from hardware.actuadores.servomotor import ServoController

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../hardware')))
from hardware.moreGPIO.More_GPIO_ESP32 import MoreGpio_ESP32

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
commandMotor = MoreGpio_ESP32(bus_number=1, address=0x08)
motor1 = Motor(bus_number=1, address=0x08, command_motor_I2C = commandMotor._command_Motor_1)
motor2 = Motor(bus_number=1, address=0x08, command_motor_I2C = commandMotor._command_Motor_2)

# Configuracion inicial motores
motor1.stop()
time.sleep(0.001)
motor2.stop()
time.sleep(0.001)

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

# Configuracion inicial servos
servo1.control_servo(0)
time.sleep(0.001)
servo2.control_servo(0)
time.sleep(0.001)
servo3.control_servo(0)
time.sleep(0.001)

print("*** Servomotor 1 - setup completed. ***")
print("*** Servomotor 2 - setup completed. ***")
print("*** Servomotor 3 - setup completed. ***")

#---------------------------------------------------------------------------------------------------------------


