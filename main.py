import time
import threading
from threading import Thread
from sensores.led import control_led
from sensores.ultrasonicos import leer_sensor, sensores, nombres_sensores, Queue_datosUltrasonicos
from sensores.lidar import leer_lidar, Queue_datosLidar
from sensores.infrarrojo import sensorInfrarrojo, Queue_sensorInfrarrojo
from sensores.brujula import BlujulaDigital, Queue_BlujulaDigital
from sensores.ldr import sensorLDR, Queue_sensorLDR1, Queue_sensorLDR2
from actuadores.motor_SpeedController_PID import create_motor_controller, data_queue1, data_queue2
from actuadores.servomotor import ServoController

#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------

# Función para formatear y imprimir los datos de los sensores
def format_sensor_data():
    contador_datos = 0
    S1_cm = 0
    S2_cm = 0
    S3_cm = 0
    S4_cm = 0
    Lidar_cm = 0
    Infrarrojo = 0
    AngBrujula = 0
    SensorLDR1 = 0
    SensorLDR2 = 0
    time.sleep(0.1)
    try:
        while True:
            start_time = time.time()
            time.sleep(0.01)
            
            # Lectura de sensores
            S1_cm = Queue_datosUltrasonicos["S1"].get()  
            S2_cm = Queue_datosUltrasonicos["S2"].get()
            S3_cm = Queue_datosUltrasonicos["S3"].get()
            S4_cm = Queue_datosUltrasonicos["S4"].get()
            Lidar_cm = Queue_datosLidar.get()
            Infrarrojo = Queue_sensorInfrarrojo.get();
            AngBrujula = Queue_BlujulaDigital.get();
            SensorLDR1 = Queue_sensorLDR1.get();
            SensorLDR2 = Queue_sensorLDR2.get();
            
            # Incrementar contador de datos
            contador_datos += 1

            # Imprimir datos formateados
            formatted_data = (
                f"Cont {contador_datos}: "
                f"{nombres_sensores[0]}: {S1_cm:.2f} cm - "
                f"{nombres_sensores[1]}: {S2_cm:.2f} cm - "
                f"{nombres_sensores[2]}: {S3_cm:.2f} cm - "
                f"{nombres_sensores[3]}: {S4_cm:.2f} cm - "
                f"Lidar: {Lidar_cm[1]} cm - "
                f"Infra: {Infrarrojo[1]} - "
                f"Bruj: {AngBrujula[1]:.2f} - "
                f"LDR1: {SensorLDR1[1]} - "
                f"LDR2: {SensorLDR2[1]}"
            )
            #print(formatted_data)
            #tamaño = Queue_sensorLDR1.qsize()
            #print(f"tamaño: {tamaño}")
            end_time = time.time()
            elapsed_time = end_time - start_time
            #print(f"Tiempo transcurrido: {elapsed_time} segundos") #Tiempo aproximado 0.05s
    except KeyboardInterrupt:
        print("Proceso de impresión de datos finalizado.")     

#---------------------------------------------------------------------------------------------------------------
        
# Funciona para inicializar todos los hilos
threads = [] # Lista global para almacenar referencias de hilos
def init_threads():
    controlSpeed_thread1 = threading.Thread(target=motor1_speedController.control_loop, args=(data_queue1,))
    controlSpeed_thread2 = threading.Thread(target=motor2_speedController.control_loop, args=(data_queue2,))

    controlSpeed_thread1.start()
    controlSpeed_thread2.start()
    threads.extend([controlSpeed_thread1, controlSpeed_thread2])
    
     # Iniciar el hilo del LED
    thread_led = Thread(target=control_led)
    thread_led.start()
    threads.append(thread_led)
    
    # Iniciar el hilo de lectura del sensor lidar
    thread_lidar = Thread(target=leer_lidar)
    thread_lidar.start()
    threads.append(thread_lidar)
    
    time.sleep(1)
    
    # Iniciar los hilos de lectura de sensores ultrasónicos
    for sensor, nombre_sensor in zip(sensores, nombres_sensores):
        thread_sensor = Thread(target=leer_sensor, args=(sensor, nombre_sensor))
        thread_sensor.start()
        threads.append(thread_sensor)
    
    # Iniciar el hilo de lectura del sensor infrarrojo
    thread_sensorInfrarrojo = Thread(target=sensorInfrarrojo)
    thread_sensorInfrarrojo.start()
    threads.append(thread_sensorInfrarrojo)
    
    # Iniciar el hilo de lectura de la brujula digital
    thread_BlujulaDigital = Thread(target=BlujulaDigital)
    thread_BlujulaDigital.start()
    threads.append(thread_BlujulaDigital)
    
    # Iniciar el hilo de lectura del sensor LDR
    thread_sensorLDR = Thread(target=sensorLDR)
    thread_sensorLDR.start()
    threads.append(thread_sensorLDR)
    
    # Iniciar el hilo de impresión de datos
    thread_print_data = Thread(target=format_sensor_data)
    thread_print_data.start()
    threads.append(thread_print_data)

#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
    
# Configuración del sistema de control de motores usando PID
Kp = 2
Ki = 6
Kd = 0.01
max_output = 500
#Pines motor 1
EN_1 = 17
IN1_1 = 23
IN2_1 = 19
PinEncoder_1 = 27
#Pines motor 2
EN_2 = 16
IN1_2 = 18
IN2_2 = 5
PinEncoder_2 = 10
motor1_speedController = create_motor_controller(1, 0x08, EN_1, IN1_1, IN2_1, PinEncoder_1, Kp, Ki, Kd, max_output)
motor2_speedController = create_motor_controller(1, 0x08, EN_2, IN1_2, IN2_2, PinEncoder_2, Kp, Ki, Kd, max_output)

#---------------------------------------------------------------------------------------------------------------

# Configuración de los servomotores
pinServo1 = 4
pinServo2 = 13
pinServo3 = 15
servo1 = ServoController(bus_number=1, address=0x08)
servo2 = ServoController(bus_number=1, address=0x08)
servo3 = ServoController(bus_number=1, address=0x08)

#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------

# Main
if __name__ == "__main__":
    try:
        #Inicializar todos los hilos
        init_threads()
        
        # Configuracion inicial motores
        motor1_speedController.set_setpoint(150)
        motor2_speedController.set_setpoint(150)
        
        # Configuracion inicial servos
        servo1.setup_servo(servo1.get_servo_name_by_pin(pinServo1), 10)
        servo2.setup_servo(servo2.get_servo_name_by_pin(pinServo2), 150)
        servo3.setup_servo(servo3.get_servo_name_by_pin(pinServo3), 100)

        while True:
            if not data_queue1.empty() and not data_queue2.empty():
                setpoint1, pv1 = data_queue1.get()
                setpoint2, pv2 = data_queue2.get()
                print(f"Setpoint1: {setpoint1:.2f}, PV1: {pv1:.2f} | Setpoint2: {setpoint2:.2f}, PV2: {pv2:.2f}")
                
            #print(f"Servo1: {servo1.get_servo_value()}, Servo2: {servo2.get_servo_value()} | Servo3: {servo3.get_servo_value()}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("Interrupción recibida, deteniendo todos los hilos...")
        motor1_speedController.set_setpoint(0)
        motor2_speedController.set_setpoint(0)
        
    finally:
        for thread in threads:
            thread.join()
        print("Programa terminado limpiamente.")
        
#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------