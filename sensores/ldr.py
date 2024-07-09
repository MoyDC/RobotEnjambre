import time
from gpiozero import DigitalInputDevice
from queue import Queue

# Define el pin GPIO donde está conectado el sensor (ajústalo según tu configuración)
pin_sensorLDR1 = 22
pin_sensorLDR2 = 27
# Crea el dispositivo de entrada digital para el sensor
sensor_LDR1 = DigitalInputDevice(pin=pin_sensorLDR1)
sensor_LDR2 = DigitalInputDevice(pin=pin_sensorLDR2)
#Queue para almacenar los datos del sensor
Queue_sensorLDR1 = Queue(maxsize=3)
Queue_sensorLDR2 = Queue(maxsize=3)
def sensorLDR():
    datosSensorLDR1 = 0
    datosSensorLDR2 = 0
    try:
        while True:
            #start_time = time.time()
            #LDR 1
            if not sensor_LDR1.value:
                #print("LDR 1 HIGH")
                datosSensorLDR1 = ("LDR1", 1)
            else:
                #print("LDR 1 LOW")
                datosSensorLDR1 = ("LDR1", 0)
            # Almacenar datos al Queue
            Queue_sensorLDR1.put(datosSensorLDR1)
            
            #LDR 2
            if not sensor_LDR2.value:
                #print("LDR 2 HIGH")
                datosSensorLDR2 = ("LDR2", 1)
            else:
                #print("LDR 2 LOW")
                datosSensorLDR2 = ("LDR2", 0)
            # Almacenar datos al Queue
            Queue_sensorLDR2.put(datosSensorLDR2)
            
            # Espera para no saturar la lectura
            time.sleep(0.05)  
            #end_time = time.time()
            #elapsed_time = end_time - start_time
            #print(f"Tiempo transcurrido: {elapsed_time} segundos")

    except KeyboardInterrupt:
        print("\nLectura de sensor terminada.")