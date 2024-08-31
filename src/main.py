import time
import multiprocessing
from initPines.init_Pines import Led_Programa, lidar_sensor, sensorsNames, sensors, sensor_Infrarrojo, sensorBrujula, readADC_ESP32, motor1, motor2, servo1, servo2, servo3
from sensores.printDataSensors.sensorDataFormatter import SensorDataFormatter
from thread.threadManager import ThreadManager
from moreGPIO.More_GPIO_ESP32 import MoreGpio_ESP32
from process_Camera_Detection import Process_Camera_Detection

# Global flag to indicate if a KeyboardInterrupt was received
interruption_received = multiprocessing.Event()  

if __name__ == "__main__":
    # Crear los procesos
    proceso1 = multiprocessing.Process(target=Process_Camera_Detection)
    
    # Resetear ESP32
    I2C_ESP32 = MoreGpio_ESP32(bus_number=1, address=0x08)
    
    # Crear instancia para imprimir los datos de los sensores
    PrintDataSensors = SensorDataFormatter(sensors, lidar_sensor, sensor_Infrarrojo, sensorBrujula, readADC_ESP32, sensorsNames)
    print("Print data sensors - setup completed.")
    
    # Manage all threads
    thread_manager = ThreadManager(
        Thread_Led_Programa = Led_Programa,
        Thread_lidar_sensor = lidar_sensor,
        Thread_sensors = sensors,
        Thread_sensor_Infrarrojo = sensor_Infrarrojo,
        Thread_sensorBrujula = sensorBrujula,
        Thread_readADC_ESP32 = readADC_ESP32,
        Thread_PrintDataSensors = PrintDataSensors)
  
    try:
        running_main_while = True
        I2C_ESP32.send_command(I2C_ESP32._command_RSTesp32,0,0)
        time.sleep(1)
        
        # Inicializar todos los hilos
        thread_manager.init_all_threads()
        
        # Iniciar los procesos
        proceso1.start()
        
        cont = 0
        while running_main_while:
            start_time = time.time()
            
            motor1.Forward(150)
            time.sleep(0.001)
            motor2.Forward(150)
            time.sleep(0.001)
            
            # Control de servos
            cont += 1
            if cont > 180:
                cont = 0
            servo1.control_servo(cont)
            servo2.control_servo(cont)
            servo3.control_servo(cont)
            
            time.sleep(0.1)
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            #print(f"Tiempo transcurrido: {elapsed_time} segundos")
            
            if interruption_received.is_set():
                running_main_while  = False
                print("Flag recibida - main")
            
        
        
    except KeyboardInterrupt:
        print("\nDeteniendo procesos...\n")
        interruption_received.set()  # Set the flag to stop processes
    
    finally:
        #stop_threads_proceso_principal()
        print("\nInterrupion recibida (Ctrl+C), deteniendo todos los hilos procesos principal...")
        if PrintDataSensors is not None:
            PrintDataSensors.stop()
        if Led_Programa is not None:
            Led_Programa.stop()
        if lidar_sensor is not None:
            lidar_sensor.stop()
        for sensor_name in sensorsNames:
            sensor = sensors.get(sensor_name)
            if sensor is not None:
                sensor.stop()
        if sensor_Infrarrojo is not None:
            sensor_Infrarrojo.stop()
        if sensorBrujula is not None:
            sensorBrujula.stop()
        if readADC_ESP32 is not None:
            readADC_ESP32.stop()
        if motor1 is not None:
            motor1.stop()
        if motor2 is not None:
            motor2.stop()
        print("Cleaning up threads...")
        thread_manager.stop_all_threads()
        I2C_ESP32.send_command(I2C_ESP32._command_RSTesp32, 0, 0)
        print("Programa terminado limpiamente.")
        
        # Delay
        time.sleep(1)
        
        # Detener proceso
        proceso1.terminate()
        proceso1.join()
        
        print("\nTodos los procesos han terminado limpiamente.")