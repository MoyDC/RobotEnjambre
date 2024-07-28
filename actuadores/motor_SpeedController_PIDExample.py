import time
import threading
from threading import Thread
from motor_SpeedController_PID import create_motor_controller, data_queue1, data_queue2

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

#Creacion de los objetos del control PID del motor
motor1_speedController = create_motor_controller(1, 0x08, EN_1, IN1_1, IN2_1, PinEncoder_1, Kp, Ki, Kd, max_output)
motor2_speedController = create_motor_controller(1, 0x08, EN_2, IN1_2, IN2_2, PinEncoder_2, Kp, Ki, Kd, max_output)

# Crear y arrancar los hilos
if __name__ == "__main__":
    try:
        # Init threads
        controlSpeed_thread1 = threading.Thread(target=motor1_speedController.control_loop, args=(data_queue1,))
        controlSpeed_thread2 = threading.Thread(target=motor2_speedController.control_loop, args=(data_queue2,))

        controlSpeed_thread1.start()
        controlSpeed_thread2.start()
    
        # Configuracion inicial motores
        motor1_speedController.set_setpoint(100)
        motor2_speedController.set_setpoint(100)
        
        
        while True:
            if not data_queue1.empty() and not data_queue2.empty():
                setpoint1, pv1 = data_queue1.get()
                setpoint2, pv2 = data_queue2.get()
                print(f"Setpoint1: {setpoint1:.2f}, PV1: {pv1:.2f} | Setpoint2: {setpoint2:.2f}, PV2: {pv2:.2f}")
        
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("Interrupción recibida, deteniendo todos los hilos...")
        motor1_speedController.set_setpoint(0)
        motor2_speedController.set_setpoint(0)
        
    finally:
        controlSpeed_thread1.join()
        controlSpeed_thread2.join()
        print("Programa terminado limpiamente.")