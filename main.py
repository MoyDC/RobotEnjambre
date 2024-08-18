import time
import multiprocessing
import threading
from initPines.init_Pines import Led_Programa, lidar_sensor, sensorsNames, sensors, sensor_Infrarrojo, sensorBrujula, readADC_ESP32, motor1, motor2, servo1, servo2, servo3
from sensores.camara.objectDetection import ObjectDetection
from sensores.printDataSensors.sensorDataFormatter import SensorDataFormatter
from thread.threadManager import ThreadManager
from More_GPIO_ESP32 import MoreGpio_ESP32

# Global flag to indicate if a KeyboardInterrupt was received
interruption_received = multiprocessing.Event()     
        
def proceso_Control_Robot():
    # codigo proceso_Control_Robot 
    try:
        running_process_while = True
        
        while running_process_while:
            #print("Proceso - proceso_pid_motores")
            time.sleep(0.1)
        
            if interruption_received.is_set():
                running_process_while  = False
                print("Flag recibida - proceso_Control_Robot")
                
    finally:
        print("End proceso_Control_Robot")

def proceso_camara_deteccion():
    # codigo proceso_camara_deteccion
    try:
        camara = ObjectDetection(display_width=640, display_height=480, show_feed=True)
        camara_thread = threading.Thread(target=camara.start)
        camara_thread.start()
        
        running_process_while = True
        
        while running_process_while:
            #print("Proceso - proceso_camara_deteccion")
            time.sleep(0.5)
            
            
            if interruption_received.is_set():
                running_process_while  = False
                print("Flag recibida - proceso_camara_deteccion")
                
    finally:
        if camara is not None:
            camara.stop()
        
        if camara_thread.is_alive():
            camara_thread.join()
            
            
        print("End proceso_camara_deteccion")


if __name__ == "__main__":
    # Crear los procesos
    proceso1 = multiprocessing.Process(target=proceso_Control_Robot)
    proceso2 = multiprocessing.Process(target=proceso_camara_deteccion)
    
    I2C_ESP32 = MoreGpio_ESP32(bus_number=1, address=0x08)
    #camara = ObjectDetection(display_width=640, display_height=480, show_feed=False)
    
    # Crear instancia para imprimir los datos de los sensores
    PrintDataSensors = SensorDataFormatter(sensors, lidar_sensor, sensor_Infrarrojo, sensorBrujula, readADC_ESP32, sensorsNames)
    print("Print data sensors - setup completed.")
    
    # Manage all threads
    thread_manager = ThreadManager(
        #Thread_motor1_speedController = motor1_speedController,
        #Thread_motor2_speedController = motor2_speedController,
        Thread_Led_Programa = Led_Programa,
        Thread_lidar_sensor = lidar_sensor,
        Thread_sensors = sensors,
        Thread_sensor_Infrarrojo = sensor_Infrarrojo,
        Thread_sensorBrujula = sensorBrujula,
        Thread_readADC_ESP32 = readADC_ESP32,
        Thread_PrintDataSensors = PrintDataSensors)#,
        #Thread_Camara = camara)
    
    try:
        running_main_while = True
        I2C_ESP32.send_command(I2C_ESP32._command_RSTesp32,0,0)
        time.sleep(1)
        
        # Inicializar todos los hilos
        thread_manager.init_all_threads()
        
        # Configuracion inicial motores
        motor1.Stop()
        time.sleep(0.001)
        motor2.Stop()
        time.sleep(0.001)
        
        # Configuracion inicial servos
        servo1.control_servo(0)
        time.sleep(0.001)
        servo2.control_servo(0)
        time.sleep(0.001)
        servo3.control_servo(0)
        time.sleep(0.001)
        
        # Iniciar los procesos
        proceso1.start()
        proceso2.start()
        
        #PrintDataSensors.stop()
        #camara.stop()
        
        
        # Esperar a que los procesos terminen
        #proceso2.join()
        #proceso3.join()

        #print("Todos los procesos han terminado.") 
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
        interruption_received.set()  # Set the flag to indi
    
    finally:
        #stop_threads_proceso_principal()
        print("\nInterrupion recibida (Ctrl+C), deteniendo todos los hilos procesos principal...")
        if PrintDataSensors is not None:
            PrintDataSensors.stop()
        if Led_Programa is not None:
            Led_Programa.stop()
        if lidar_sensor is not None:
            lidar_sensor.stop_reading()
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
            motor1.Stop()
        if motor2 is not None:
            motor2.Stop()
        #if camara is not None:
            #camara.stop()
        print("Cleaning up threads...")
        thread_manager.stop_all_threads()
        I2C_ESP32.send_command(I2C_ESP32._command_RSTesp32, 0, 0)
        print("Programa terminado limpiamente.")
        
        time.sleep(1)
        
        proceso1.terminate()
        proceso2.terminate()
        
        proceso1.join()
        proceso2.join()
        print("\nTodos los procesos han terminado limpiamente.")