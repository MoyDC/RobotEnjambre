import time
import smbus2
import math
from queue import Queue

# Define constants
QMC5883_ADDR = 0x0D
# REG CONTROL
Mode_Standby = 0b00000000
Mode_Continuous = 0b00000001
ODR_10Hz = 0b00000000
ODR_50Hz = 0b00000100
ODR_100Hz = 0b00001000
ODR_200Hz = 0b00001100
RNG_2G = 0b00000000
RNG_8G = 0b00010000
OSR_512 = 0b00000000
OSR_256 = 0b01000000
OSR_128 = 0b10000000
OSR_64 = 0b11000000
class MechaQMC5883:
    def __init__(self, address=QMC5883_ADDR, bus=1):
        self.address = address
        self.bus = smbus2.SMBus(bus)

    def set_address(self, addr):
        self.address = addr

    def write_reg(self, reg, val):
        self.bus.write_byte_data(self.address, reg, val)

    def init(self):
        self.write_reg(0x0B, 0x01)
        self.set_mode(Mode_Continuous, ODR_200Hz, RNG_8G, OSR_512)

    def set_mode(self, mode, odr, rng, osr):
        self.write_reg(0x09, mode | odr | rng | osr)

    def soft_reset(self):
        self.write_reg(0x0A, 0x80)

    def read(self):
        self.bus.write_byte(self.address, 0x00)
        data = self.bus.read_i2c_block_data(self.address, 0x00, 7)
        x = int.from_bytes(data[0:2], byteorder='little', signed=True)
        y = int.from_bytes(data[2:4], byteorder='little', signed=True)
        z = int.from_bytes(data[4:6], byteorder='little', signed=True)
        overflow = (data[6] & 0x02) << 2
        return x, y, z, overflow

    def read_with_azimuth_int(self):
        x, y, z, err = self.read()
        a = int(self.azimuth(y, x))
        return x, y, z, a, err

    def read_with_azimuth_float(self):
        x, y, z, err = self.read()
        a = self.azimuth(y, x)
        return x, y, z, a, err

    def azimuth(self, a, b):
        azimuth = math.atan2(a, b) * 180.0 / math.pi
        return azimuth if azimuth >= 0 else 360 + azimuth
#Queue para almacenar los datos de la brujula
Queue_BlujulaDigital = Queue(maxsize=3)
def BlujulaDigital():
    sensor = MechaQMC5883()
    sensor.init()
    try:
        while True:
            #start_time = time.time()
            #declinacion = 4.23;  # declinacion desde pagina: http://www.magnetic-declination.com/
            x, y, z, azimuth, err = sensor.read_with_azimuth_float()
            #geografico = acimut + declinacion; # acimut geografico como suma del magnetico y declinacion
            #if geografico < 0:
            #    geografico = geografico + 360
            datosBrujulaDigital = ("BrujulaDigital", azimuth)
            # Almacenar datos al Queue
            Queue_BlujulaDigital.put(datosBrujulaDigital)
            #print(f"x: {x}, y: {y}, z: {z}, Azimuth: {azimuth}")
            time.sleep(0.05)
            #end_time = time.time()
            #elapsed_time = end_time - start_time
            #print(f"Tiempo transcurrido: {elapsed_time} segundos")
    except Exception as e:
        print(f"Error al leer el sensor: {e}")