import time
from gpiozero import DigitalInputDevice
from queue import Queue

# Define el pin GPIO donde está conectado el sensor (ajústalo según tu configuración)
pin_sensor = 20
# Crea el dispositivo de entrada digital para el sensor
sensor_Infrarrojo = DigitalInputDevice(pin=pin_sensor)
#Queue para almacenar los datos del sensor de obstaculos
Queue_sensorInfrarrojo = Queue(maxsize=3)
def sensorInfrarrojo():
    datosSensorObstaculos = 0
    try:
        while True:
            #start_time = time.time()
            if not sensor_Infrarrojo.value:
                #print("¡Obstáculo detectado!")
                datosSensorInfrarrojo = ("SensorObstaculos", 1)
                
            else:
                #print("Sin obstáculo")
                datosSensorInfrarrojo = ("SensorObstaculos", 0)
            # Almacenar datos al Queue
            Queue_sensorInfrarrojo.put(datosSensorInfrarrojo)
            time.sleep(0.05)  # Espera para no saturar la lectura
            #end_time = time.time()
            #elapsed_time = end_time - start_time
            #print(f"Tiempo transcurrido: {elapsed_time} segundos")

    except KeyboardInterrupt:
        print("\nLectura de sensor terminada.")