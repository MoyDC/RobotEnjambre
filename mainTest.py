import multiprocessing
import time
from initPines.init_Pines import Led_Programa, lidar_sensor, sensorsNames, sensors, sensor_Infrarrojo, sensorBrujula, readADC_ESP32, motor1_speedController, motor2_speedController, servo1, servo2, servo3
from sensores.camara.objectDetection import ObjectDetection
from sensores.printDataSensors.sensorDataFormatter import SensorDataFormatter
from thread.threadManager import ThreadManager
from More_GPIO_ESP32 import MoreGpio_ESP32

# Global flag to indicate if a KeyboardInterrupt was received
interruption_received = multiprocessing.Event()
    
def proceso_principal():
    I2C_ESP32 = MoreGpio_ESP32(bus_number=1, address=0x08)
    #camara = ObjectDetection(display_width=640, display_height=480, show_feed=False)
    
    # Crear instancia para imprimir los datos de los sensores
    PrintDataSensors = SensorDataFormatter(sensors, lidar_sensor, sensor_Infrarrojo, sensorBrujula, readADC_ESP32, sensorsNames)
    print("Print data sensors - setup completed.")
    
    # Manage all threads
    thread_manager = ThreadManager(
        Thread_motor1_speedController = motor1_speedController,
        Thread_motor2_speedController = motor2_speedController,
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
        motor1_speedController.set_setpoint(150)
        motor2_speedController.set_setpoint(150)
        
        # Configuracion inicial servos
        servo1.control_servo(0)
        servo2.control_servo(0)
        servo3.control_servo(0)
        
        #PrintDataSensors.stop()
        #camara.stop()
        
        cont = 0
        while running_main_while:
            data1 = motor1_speedController.get_data()
            data2 = motor2_speedController.get_data()
            if data1[1] != -2 and data2[1] != -2:
                setpoint1, pv1 = data1
                setpoint2, pv2 = data2
                #print(f"Setpoint1: {setpoint1:.2f}, PV1: {pv1:.2f} | Setpoint2: {setpoint2:.2f}, PV2: {pv2:.2f}")
                
            # Control de servos
            cont += 1
            if cont > 180:
                cont = 0
            servo1.control_servo(cont)
            servo2.control_servo(cont)
            servo3.control_servo(cont)
            
            time.sleep(0.1)
            
            if interruption_received.is_set():
                running_main_while  = False
                
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
        if motor1_speedController is not None:
            motor1_speedController.stop(name="Motor 1")
        if motor2_speedController is not None:
            motor2_speedController.stop(name="Motor 2")
        #if camara is not None:
            #camara.stop()
        print("Cleaning up threads...")
        thread_manager.stop_all_threads()
        I2C_ESP32.send_command(I2C_ESP32._command_RSTesp32, 0, 0)
        print("Programa terminado limpiamente.")
        
def proceso_pid_motores():
    # codigo proceso 2
    pass

def proceso_camara_deteccion():
    # codigo proceso 3
    pass


if __name__ == "__main__":
    
    # Crear los procesos
    proceso1 = multiprocessing.Process(target=proceso_principal)
    proceso2 = multiprocessing.Process(target=proceso_pid_motores)
    proceso3 = multiprocessing.Process(target=proceso_camara_deteccion)
    
    try:
        # Iniciar los procesos
        proceso1.start()
        proceso2.start()
        proceso3.start()
        
    
        # Esperar a que los procesos terminen
        proceso1.join()
        proceso2.join()
        proceso3.join()

        print("Todos los procesos han terminado.")
        
    except KeyboardInterrupt:
        print("\nDeteniendo procesos...\n")
        interruption_received.set()  # Set the flag to indi
    
    finally:
        time.sleep(5)
        
        proceso1.terminate()
        proceso2.terminate()
        proceso3.terminate()
        
        proceso1.join()
        proceso2.join()
        proceso3.join()
        print("\nTodos los procesos han terminado limpiamente.")