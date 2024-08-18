import time
import queue
from queue import Queue
from typing import Tuple
from gpiozero import DigitalInputDevice
from simple_pid import PID
import os
import sys
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../actuadores')))
from motor import Motor

class Motor_SpeedController_PID:
    def __init__(self, motor: Motor, pid: PID, encoder: DigitalInputDevice, max_output: float, delayLoopPID=0.1, max_sizeQueue=3):
        self.motor = motor
        self.pid = pid
        self.encoder = encoder
        self.max_output = max_output
        self.contador = 0
        self.setpoint = 0.0
        self.pv = 0.0
        self.delayPID = delayLoopPID
        self.encoder.when_activated = self.increment_counter
        self._is_running = False
        self.data_queue = Queue(maxsize=max_sizeQueue)

    def increment_counter(self):
        self.contador += 1

    def calculate_rpm(self) -> float:
        ppr = 374  # Pulses per revolution
        factor = 10
        return factor * self.contador * (60.0 / ppr)

    def control_loop(self):
        self._is_running = True
        cont = 0
        while self._is_running:
            start_time = time.time()
            self.pv = self.calculate_rpm()
            cont = cont+1
            #print(f"Cont: {cont} - {self.contador}")
            self.contador = 0
            self.pid.setpoint = self.setpoint
            control_value = self.pid(self.pv)
            pwm_value = int(control_value * 255 / self.max_output)
            self.motor.forward(pwm_value)
            
            if self.data_queue.full():
                self.data_queue.get()
            self.data_queue.put((self.setpoint, self.pv), block=False)
            time.sleep(self.delayPID)
            end_time = time.time()
            elapsed_time = end_time - start_time
            #print(f"Tiempo transcurrido: {elapsed_time} segundos")
        self.motor.stop()

    def set_setpoint(self, setpoint: float):
        self.setpoint = max(0, min(200, setpoint))  # Ensure setpoint is between 0 and 200

    def get_setpoint(self) -> float:
        return self.setpoint

    def get_pv(self) -> float:
        return self.pv
    
    def get_data(self) -> Tuple[float, float]:
        if not self.data_queue.empty():
            return self.data_queue.get()
        else:
            return (self.setpoint, -2)  # Return an error value if queue is empty
    
    def stop(self, name="Motor"):
        self.motor.stop()
        self._is_running = False
        print(f"{name} stopped.")

# Función para crear instancias de controladores de motor
def create_motor_controller(bus_number: int, address: int, EN: int, IN1: int, IN2: int, pin_encoder: int, Kp: float, Ki: float, Kd: float, max_output: float, delayLoopPID=0.1) -> Motor_SpeedController_PID:
    motor = Motor(bus_number=bus_number, address=address)
    motor.setup_motor(EN, IN1, IN2)
    pid = PID(Kp, Ki, Kd, setpoint=0)
    pid.output_limits = (0, max_output)
    encoder = DigitalInputDevice(pin_encoder)
    return Motor_SpeedController_PID(motor, pid, encoder, max_output, delayLoopPID)

