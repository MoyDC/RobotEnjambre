import time
import queue
from queue import Queue
from typing import Tuple
from gpiozero import DigitalInputDevice
from simple_pid import PID
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../actuadores')))
from motor import Motor

# Crear los queues de comunicación
data_queue1: Queue[Tuple[float, float]] = queue.Queue(maxsize=3)
data_queue2: Queue[Tuple[float, float]] = queue.Queue(maxsize=3)

class Motor_SpeedController_PID:
    def __init__(self, motor: Motor, pid: PID, encoder: DigitalInputDevice, max_output: float, delayLoopPID=0.1):
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

    def increment_counter(self):
        self.contador += 1

    def calculate_rpm(self) -> float:
        ppr = 374  # Pulses per revolution
        factor = 10
        return factor * self.contador * (60.0 / ppr)

    def control_loop(self, data_queue: Queue[Tuple[float, float]]):
        self._is_running = True
        while self._is_running:
            self.pv = self.calculate_rpm()
            self.contador = 0
            self.pid.setpoint = self.setpoint
            control_value = self.pid(self.pv)
            pwm_value = int(control_value * 255 / self.max_output)
            self.motor.forward(pwm_value)
            
            if data_queue.full():
                data_queue.get()
            data_queue.put((self.setpoint, self.pv), block=False)
            time.sleep(self.delayPID)

    def set_setpoint(self, setpoint: float):
        self.setpoint = max(0, min(200, setpoint))  # Ensure setpoint is between 0 and 200

    def get_setpoint(self) -> float:
        return self.setpoint

    def get_pv(self) -> float:
        return self.pv
    
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
