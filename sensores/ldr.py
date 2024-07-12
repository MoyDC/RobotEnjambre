import time
from queue import Queue
from adcESP32 import adc_ESP2
         
# Crear una instancia del módulo MoreGpio_ESP32
Sensor1 = adc_ESP2(bus_number=1, address=0x08)
Sensor2 = adc_ESP2(bus_number=1, address=0x08)

# Define el pin GPIO donde está conectado el sensor (ajústalo según tu configuración)
pin_sensorLDR1 = 36
pin_sensorLDR2 = 39

Sensor1.setup_adc_pin(Sensor1.get_adc_name_by_pin(pin_sensorLDR1))
Sensor2.setup_adc_pin(Sensor2.get_adc_name_by_pin(pin_sensorLDR2))

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
            sensor1_value, idPin_Return1 = Sensor1.read_adc(cont)
            if sensor1_value is not None:
                #print(f"{cont} - Sensor 1 Value: {sensor1_value}")
                datosSensorLDR1 = ("LDR1", sensor1_value)
                Queue_sensorLDR1.put(datosSensorLDR1)
            
            #LDR 2
            sensor2_value, idPin_Return2 = Sensor2.read_adc(cont)
            if sensor2_value is not None:
                #print(f"{cont} - Sensor 2 Value: {sensor2_value}")
                datosSensorLDR2 = ("LDR2", sensor2_value)
                Queue_sensorLDR2.put(datosSensorLDR2)
             
            end_time = time.time()
            elapsed_time = end_time - start_time
            #print(f"Tiempo transcurrido: {elapsed_time} segundos")

    except KeyboardInterrupt:
        print("\nLectura de sensor terminada.")
        