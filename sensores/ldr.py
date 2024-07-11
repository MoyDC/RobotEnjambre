import sys
import os
import time
from queue import Queue
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../moreGPIO')))
from More_GPIO_ESP32 import MoreGpio_ESP32

# Crear una instancia del módulo MoreGpio_ESP32
readSensor1 = MoreGpio_ESP32(bus_number=1, address=0x08)
readSensor2 = MoreGpio_ESP32(bus_number=1, address=0x08)

# Define el pin GPIO donde está conectado el sensor (ajústalo según tu configuración)
pin_sensorLDR1 = MoreGpio_ESP32.ADCPin36
pin_sensorLDR2 = MoreGpio_ESP32.ADCPin39

#Queue para almacenar los datos del sensor
Queue_sensorLDR1 = Queue(maxsize=3)
Queue_sensorLDR2 = Queue(maxsize=3)

def sensorLDR():
    datosSensorLDR1 = 0
    datosSensorLDR2 = 0
    cont = 0
    try:
        while True:
            start_time = time.time()
            cont += 1
            
            #LDR1
            sensor1_value, idPin_Return1= readSensor1.readSensor(MoreGpio_ESP32._Command_ADC_, pin_sensorLDR1, cont)
            if sensor1_value is not None:
                #print(f"{cont} - Sensor 1 Value: {sensor1_value}")
                datosSensorLDR1 = ("LDR1", sensor1_value)
                Queue_sensorLDR1.put(datosSensorLDR1)
            
            #LDR 2
            sensor2_value, idPin_Return2 = readSensor2.readSensor(MoreGpio_ESP32._Command_ADC_, pin_sensorLDR2, cont)
            if sensor2_value is not None:
                #print(f"{cont} - Sensor 2 Value: {sensor2_value}")
                datosSensorLDR2 = ("LDR2", sensor2_value)
                Queue_sensorLDR2.put(datosSensorLDR2)
             
            end_time = time.time()
            elapsed_time = end_time - start_time
            #print(f"Tiempo transcurrido: {elapsed_time} segundos")

    except KeyboardInterrupt:
        print("\nLectura de sensor terminada.")
        