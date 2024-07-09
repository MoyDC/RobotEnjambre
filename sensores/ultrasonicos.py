import time
from gpiozero import DistanceSensor
from queue import Queue

# Configuración de los sensores ultrasónicos
sensores = [
    DistanceSensor(echo=16, trigger=26),
    DistanceSensor(echo=5, trigger=6),
    DistanceSensor(echo=7, trigger=1),
    DistanceSensor(echo=25, trigger=8)
]
# Nombres de los sensores para imprimir
nombres_sensores = ["S1", "S2", "S3", "S4"]
# Diccionario para las colas de datos de cada sensor
Queue_datosUltrasonicos = {nombre_sensor: Queue(maxsize=3) for nombre_sensor in nombres_sensores}
# Variable global para contar los datos
contador_datos = 0
# Función para el hilo que lee los sensores ultrasónicos
def leer_sensor(sensor, nombre_sensor):
    global contador_datos
    delayUltrasonicos = 0.05 # Delay entre lecturas de los sensores ultrasónicos
    try:
        while True:
            #start_time = time.time()
            distancia_cm = sensor.distance * 100  # Convertir a centímetros
            
            # Agregar datos al Queue correspondiente
            Queue_datosUltrasonicos[nombre_sensor].put(distancia_cm)
            
            time.sleep(delayUltrasonicos)
            
            #end_time = time.time()
            #elapsed_time = end_time - start_time
            #if nombre_sensor == "S4":
                #print(f"Tiempo transcurrido: {elapsed_time} segundos - Sensor: {distancia_cm} cm")

    except KeyboardInterrupt:
        print(f"Lectura del {nombre_sensor} finalizada.")