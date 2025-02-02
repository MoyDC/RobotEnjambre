import time
import multiprocessing
from utils.initPines.init_Pines import Led_Programa, lidar_sensor, sensorsNames, sensors, sensor_Infrarrojo, sensorBrujula, readADC_ESP32, motor1, motor2, servo1_ejeY_camara, servo2, servo3_ejeX_camara, batteryMonitor, robot_rules, robot
from utils.printDataSensors.sensorDataFormatter import SensorDataFormatter
from utils.thread.threadManager import ThreadManager
from hardware.moreGPIO.More_GPIO_ESP32 import MoreGpio_ESP32
from process_Camera_Detection import Process_Camera_Detection, interruption_received, queue_data_object_in_Camara, detect_color1, detect_color2

current_state = "Inicio"
init_cont_servo_position = 40;
mid_cont_servo_position = 90;
end_cont_servo_position = 140;
cont_servo_position = mid_cont_servo_position
moveCamera = True
move_right_servo = True
move_left_servo = False
move_right_robot = False
move_left_robot = False
orientation_robot_in_BuscarZonaObjetos = 0
speen_motor_ZonaObjetos = 0

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
        
        
        time.sleep(0.01)
        motor1.Forward(0) 
        time.sleep(0.01)
        motor2.Forward(0)  

        #while True:
        #    cont = cont + 1;
        #   print(f"cont: {cont}")
        #    time.sleep(1)

        while running_main_while:
            if not I2C_ESP32.test_is_i2c_working():
                running_main_while  = False
                print("I2c communication error")
                break
            
            if interruption_received.is_set():
                running_main_while  = False
                break

            action_in, action = robot_rules.behavior_rules()
            print(f"action in: {action_in}")
            #if not batteryMonitor.is_voltage_adc1_in_range():
            #    running_main_while  = False
            #    print("Battery LiPo in ADC1 has reached its limit")
            #    break;
            
            #if not batteryMonitor.is_voltage_adc2_in_range():
            #    running_main_while  = False
            #   print("Battery Power Bank in ADC2 has reached its limit")
            #    break;  
            
            #print("Estado de la Queue:", queue_data_object_in_Camara.get())
            #-----------------------------------------------------------------------------------------------------
            if current_state == "Inicio":
                print("Estado: Inicio")
                current_state = "Buscar Zona Objetos"

            #-----------------------------------------------------------------------------------------------------
            elif current_state == "Buscar Zona Objetos":
                print("Estado: Buscar Zona Objetos")
                detect_color1.set()
                detect_color2.clear()

                data_Object_in_Camara = queue_data_object_in_Camara.get()

                position_object_in_camara = data_Object_in_Camara[0]
                percentage_object_in_camara = data_Object_in_Camara[1]

                if position_object_in_camara == "Camera_Object_is_on_the_left":
                    print(f"Porcentaje Left: {percentage_object_in_camara}")
                    servo3_ejeX_camara.control_servo(mid_cont_servo_position)
                    moveCamera = False
                    move_left_robot = True
                    move_right_robot = False

                elif position_object_in_camara == "Camera_Object_is_on_the_right":
                    print(f"Porcentaje Right: {percentage_object_in_camara}")
                    servo3_ejeX_camara.control_servo(mid_cont_servo_position)
                    moveCamera = False
                    move_right_robot = True
                    move_left_robot = False

                elif position_object_in_camara == "Camera_Object_is_at_the_midpoint":
                    print(f"Porcentaje Mitad: {percentage_object_in_camara}")
                    current_state = "Zona Objetos"
                    servo3_ejeX_camara.control_servo(mid_cont_servo_position)
                    orientation_robot_in_BuscarZonaObjetos = round(sensorBrujula.get_data()[1], 2)
                    moveCamera = False
                    move_right_robot = False
                    move_left_robot = False
                    move_right_servo = True
                    move_left_servo = False
                    cont_servo_position = mid_cont_servo_position
                    motor1.stop()
                    motor2.stop()
                    time.sleep(1)
                
                elif position_object_in_camara == "Camera_No_Object":
                    print("No Object")
                    

                # Mover el robot para que quede posicionado el objeto a la mitad de la camara
                if move_right_robot:
                    motor2.stop() 
                    motor1.Forward(25)  
                    time.sleep(0.05)
                    motor1.stop()
                elif move_left_robot:
                    motor1.stop()
                    motor2.Forward(25)  
                    time.sleep(0.05)
                    motor2.stop()

                if moveCamera:
                    time.sleep(0.2)
                    print(f"Servo position: {cont_servo_position}")

                    # Mover la camara con los servos
                    if move_right_servo:
                        cont_servo_position = cont_servo_position - 1
                        servo3_ejeX_camara.control_servo(cont_servo_position)
                        
                        if cont_servo_position < init_cont_servo_position:
                            move_right_servo = False
                            move_left_servo = True

                    elif move_left_servo:
                        cont_servo_position = cont_servo_position + 1
                        servo3_ejeX_camara.control_servo(cont_servo_position)
                        if cont_servo_position > end_cont_servo_position:
                            move_left_servo = False
                    
                    # Sino se encuentra la zona de objetos brincar al estado Zona Cercana de Mayor Luz 1
                    elif not move_right_servo and not move_left_servo:
                        cont_servo_position = mid_cont_servo_position
                        servo3_ejeX_camara.control_servo(mid_cont_servo_position)
                        current_state = "Zona Cercana de Mayor Luz 1"

            #-----------------------------------------------------------------------------------------------------
            elif current_state == "Zona Cercana de Mayor Luz 1":
                time.sleep(0.1)
                print("Estado: Zona Cercana de Mayor Luz 1")
                LDR1 = readADC_ESP32.get_dataADC_LDR1()
                LDR2 = readADC_ESP32.get_dataADC_LDR2()
                data_Object_in_Camara = queue_data_object_in_Camara.get()

                position_object_in_camara = data_Object_in_Camara[0]

                print(LDR1)
                print(LDR2)
                
                if LDR1[1] <= LDR2[1]:
                    print("turn left")
                    motor1.stop()
                    motor2.Forward(25)  
                    time.sleep(0.05)
                    motor2.stop()

                else:
                    print("turn right")
                    motor2.stop()
                    motor1.Forward(25)  
                    time.sleep(0.05)
                    motor1.stop()

                if not position_object_in_camara == "Camera_No_Object":
                    print("Object in camera")
                    current_state = "Buscar Zona Objetos"
                    moveCamera = True
                    motor1.stop()
                    motor2.stop()

            #-----------------------------------------------------------------------------------------------------
            elif current_state == "Zona Objetos":
                print("Estado: Zona Objetos")
                data_Object_in_Camara = queue_data_object_in_Camara.get()
                #LDR1 = readADC_ESP32.get_dataADC_LDR1()
                #LDR2 = readADC_ESP32.get_dataADC_LDR2()
                lidar_cm = lidar_sensor.get_data()[1]
                

                position_object_in_camara = data_Object_in_Camara[0]
                #percentage_object_in_camara = data_Object_in_Camara[1]
                area_object_in_camara = data_Object_in_Camara[2]
                
                print(orientation_robot_in_BuscarZonaObjetos)
                print(round(sensorBrujula.get_data()[1], 2))
                print(area_object_in_camara)
                

                motor1.Forward(30)
                motor2.Forward(30)

                if position_object_in_camara == "Camera_No_Object" or action_in == "repulsion_radius" or lidar_cm < 50: 
                    print("No Object")
                    current_state = "Buscar Zona Objetos"
                    moveCamera = True
                    motor1.stop()
                    motor2.stop()

                if area_object_in_camara > 123550560:
                    print("End test")
                    motor1.stop(0)
                    motor2.stop(0)
                    running_main_while = False
                    

                #speen_motor_ZonaObjetos = speen_motor_ZonaObjetos + 1
                #if speen_motor_ZonaObjetos <= 40:
                #    time.sleep(0.01)
                #    motor1.Forward(speen_motor_ZonaObjetos)
                #else:
                #    time.sleep(0.01)
                #    motor1.Forward(40) 

                #if speen_motor_ZonaObjetos*1.2 <= 40:
                #    time.sleep(0.01)
                #    motor2.Forward(speen_motor_ZonaObjetos*2)
                #else:
                #    time.sleep(0.01)
                #    motor2.Forward(40) 
                
            
            #-----------------------------------------------------------------------------------------------------
            elif current_state == "Buscar Nido":
                print(" ")

            #-----------------------------------------------------------------------------------------------------
            elif current_state == "Zona Cercana de Mayor Luz 2":
                print(" ")
            
            #-----------------------------------------------------------------------------------------------------
            elif current_state == "Zona Nido":
                print(" ")

            #-----------------------------------------------------------------------------------------------------
            else:
                print("Estado desconocido. Saliendo del programa.")
                break
    
            #action_in, action = robot_rules.behavior_rules()
            #print(f"{action_in} - {action}")

            #if action_in == "repulsion_radius":
            #    if action == "Object_front":
            #        print("Stop and turn")
            #    elif action == "Object_front_and_left":
            #        print("Turn right")
            #    elif action == "Object_front_and_right":
            #        print("Turn left")
            #    elif action == "Object_front_left_right":
            #        print("Reverse then turn")
            #    elif action == "Object_front_left_right_back":
            #        print("Stop")
            #    elif action == "Object_left":
            #        print("Turn right")
            #    elif action == "Object_right":
            #        print("Turn left")
            #    elif action == "Object_left_and_right":
            #        print("Forward")
            #    elif action == "Object_back":
            #        print("Forward")
            #    elif action == "No_object":
            #        print("Forward")

            #elif action_in == "influence_radius":
            #    if action == "No_object":
            #        print("Forward")
            #    elif action == "Object_Front_Left":
            #        print("Turn right")
            #    elif action == "Object_Front_Right":
            #        print("Turn left")
            #    elif action == "Object_Front":
            #        print("Forward")

            #elif action_in == "attraction_radius":
            #    if action == "Object_front":
            #        print("Forward")
            #   elif action == "Object_front_and_left":
            #        print("Turn left")
            #    elif action == "Object_front_and_right":
            #        print("Turn right")
            #    elif action == "Object_front_left_right":
            #        print("Forward")
            #    elif action == "Object_front_left_right_back":
            #        print("Forward")
            #    elif action == "Object_left":
            #        print("Turn left")
            #    elif action == "Object_right":
            #        print("Turn right")
            #    elif action == "Object_left_and_right":
            #        print("Turn right")
            #    elif action == "Object_back":
            #        print("Forward slow")
            #    elif action == "No_object":
            #        print("Look for influence object")

            #else:
            #    print("No action-in")

            #print("Working")
            start_time = time.time()
            
            
            #motor1.Forward(150)
            #time.sleep(0.001)
            #motor2.Forward(30)
            #time.sleep(0.001)
            
            # Control de servos
            #cont += 1
            #if cont > 180:
            #    cont = 0
            #servo1.control_servo(cont)
            #servo2.control_servo(cont)
            #servo3.control_servo(cont)
            
            time.sleep(0.1)
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            #print(f"Tiempo transcurrido: {elapsed_time} segundos")  
        
    except KeyboardInterrupt:
        print("\nDeteniendo procesos...\n")
        interruption_received.set()  # Set the flag to stop processes

    finally:
        print("\nInterrupion recibida (Ctrl+C), deteniendo todos los hilos procesos principal...")
        I2C_ESP32.send_command(I2C_ESP32._command_RSTesp32, 0, 0)
        thread_manager.stop_all_threads()
        print("Cleaning up threads...")
        
        
        
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