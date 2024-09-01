import time
import multiprocessing
from utils.initPines.init_Pines import Led_Programa, lidar_sensor, sensorsNames, sensors, sensor_Infrarrojo, sensorBrujula, readADC_ESP32, motor1, motor2, servo1, servo2, servo3
from utils.printDataSensors.sensorDataFormatter import SensorDataFormatter
from utils.thread.threadManager import ThreadManager
from hardware.moreGPIO.More_GPIO_ESP32 import MoreGpio_ESP32
from process_Camera_Detection import Process_Camera_Detection, interruption_received

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
        if not thread_manager.init_all_threads(): 
            print("\n***Not all threads were initialized, stopping the program.***")
            running_main_while  = False
        
        # Iniciar los procesos
        proceso1.start()

        #PrintDataSensors.stop()
        cont = 0
        while running_main_while:
            if not I2C_ESP32.test_is_i2c_working():
                running_main_while  = False
                print("I2c communication error")
                break
            
            if interruption_received.is_set():
                running_main_while  = False
                break

            #print("Working")
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
        
    except KeyboardInterrupt:
        print("\nDeteniendo procesos...\n")
        interruption_received.set()  # Set the flag to stop processes
    
    finally:
        print("\nInterrupion recibida (Ctrl+C), deteniendo todos los hilos procesos principal...")
        thread_manager.stop_all_threads()
        print("Cleaning up threads...")
        
        I2C_ESP32.send_command(I2C_ESP32._command_RSTesp32, 0, 0)
        
        # Delay
        time.sleep(1)
        
        # Detener proceso
        if proceso1.is_alive():
            proceso1.terminate()
            proceso1.join()
            print("Proceso 1 terminado.")

        print("\nTodos los procesos han terminado limpiamente.")