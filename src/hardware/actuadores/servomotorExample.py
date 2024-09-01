from servomotor import ServoController

# Objetos ServoController
servo1 = ServoController(bus_number=1, address=0x08)
servo2 = ServoController(bus_number=1, address=0x08)
servo3 = ServoController(bus_number=1, address=0x08)

# Pines para los servos
pinServo1 = 4
pinServo2 = 13
pinServo3 = 15

# Configuracion Inicial Servos
servo1.setup_servo(servo1.get_servo_name_by_pin(pinServo1), 10)
servo2.setup_servo(servo2.get_servo_name_by_pin(pinServo2), 10)
servo3.setup_servo(servo3.get_servo_name_by_pin(pinServo3), 10)

# Control Servos
servo1.control_servo(40)
servo2.control_servo(50)
servo3.control_servo(100)