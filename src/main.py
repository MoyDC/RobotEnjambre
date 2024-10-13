import time
import multiprocessing
from utils.initPines.init_Pines import Led_Programa, lidar_sensor, sensorsNames, sensors, sensor_Infrarrojo, sensorBrujula, readADC_ESP32, motor1, motor2, servo1, servo2, servo3, batteryMonitor, robot_rules
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
        Thread_PrintDataSensors = PrintDataSensors,
        Thread_BatteryMonitor = batteryMonitor)
    
    

    try:
        running_main_while = True
        I2C_ESP32.send_command(I2C_ESP32._command_RSTesp32,0,0)
        #time.sleep(1)
        
        # Inicializar todos los hilos
        if not thread_manager.init_all_threads(): 
            print("\n***Not all threads were initialized, stopping the program.***")
            running_main_while  = False
        time.sleep(2)
        PrintDataSensors.stop()

        # Iniciar los procesos
        proceso1.start()

        
        cont = 0
        while running_main_while:
            if not I2C_ESP32.test_is_i2c_working():
                running_main_while  = False
                print("I2c communication error")
                break
            
            if interruption_received.is_set():
                running_main_while  = False
                break
            
            #if not batteryMonitor.is_voltage_adc1_in_range():
            #    running_main_while  = False
            #    print("Battery in ADC1 has reached its limit")
            #    break;
            
            #if not batteryMonitor.is_voltage_adc2_in_range():
            #    running_main_while  = False
            #    print("Battery in ADC2 has reached its limit")
            #    break;  
            
            action_in, action = robot_rules.behavior_rules()
            print(f"{action_in} - {action}")

            if action_in == "repulsion_radius":
                if action == "Object_front":
                    print("Stop and turn")
                elif action == "Object_front_and_left":
                    print("Turn right")
                elif action == "Object_front_and_right":
                    print("Turn left")
                elif action == "Object_front_left_right":
                    print("Reverse then turn")
                elif action == "Object_front_left_right_back":
                    print("Stop")
                elif action == "Object_left":
                    print("Turn right")
                elif action == "Object_right":
                    print("Turn left")
                elif action == "Object_left_and_right":
                    print("Forward")
                elif action == "Object_back":
                    print("Forward")
                elif action == "No_object":
                    print("Forward")

            elif action_in == "influence_radius":
                if action == "No_object":
                    print("Forward")
                elif action == "Object_Front_Left":
                    print("Turn right")
                elif action == "Object_Front_Right":
                    print("Turn left")
                elif action == "Object_Front":
                    print("Forward")

            elif action_in == "attraction_radius":
                if action == "Object_front":
                    print("Forward")
                elif action == "Object_front_and_left":
                    print("Turn left")
                elif action == "Object_front_and_right":
                    print("Turn right")
                elif action == "Object_front_left_right":
                    print("Forward")
                elif action == "Object_front_left_right_back":
                    print("Forward")
                elif action == "Object_left":
                    print("Turn left")
                elif action == "Object_right":
                    print("Turn right")
                elif action == "Object_left_and_right":
                    print("Turn right")
                elif action == "Object_back":
                    print("Forward slow")
                elif action == "No_object":
                    print("Look for influence object")

            else:
                print("No action-in")

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
        
        batteryMonitor.indicate_battery_limit()
        input("Press Enter to stop the program: ")
        print("\nAll processes have finished cleanly.")     