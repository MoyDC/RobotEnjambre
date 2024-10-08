import time
import smbus2
import math
from queue import Queue

# Define constants
QMC5883_ADDR = 0x0D
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

class Brujula_MechaQMC5883:
    def __init__(self, address=QMC5883_ADDR, bus=1, max_sizeQueue=3, delay=0.04):
        self.address = address
        self.bus = smbus2.SMBus(bus)
        self.delay = delay
        self._is_running = False
        self.queue = Queue(maxsize=max_sizeQueue)

    def __write_reg(self, reg, val):
        """Write a value to a specific register."""
        self.bus.write_byte_data(self.address, reg, val)

    def init(self):
        """Initialize the sensor with default settings."""
        self.__soft_reset()
        self.__write_reg(0x0B, 0x01)
        self.__set_mode(Mode_Continuous, ODR_200Hz, RNG_8G, OSR_512)

    def __set_mode(self, mode, odr, rng, osr):
        """Set the operation mode of the sensor."""
        self.__write_reg(0x09, mode | odr | rng | osr)

    def __soft_reset(self):
        """Perform a soft reset of the sensor."""
        self.__write_reg(0x0A, 0x80)

    def __read(self):
        """Read raw data from the sensor."""
        self.bus.write_byte(self.address, 0x00)
        data = self.bus.read_i2c_block_data(self.address, 0x00, 7)
        x = int.from_bytes(data[0:2], byteorder='little', signed=True)
        y = int.from_bytes(data[2:4], byteorder='little', signed=True)
        z = int.from_bytes(data[4:6], byteorder='little', signed=True)
        overflow = (data[6] & 0x02) << 2
        return x, y, z, overflow

    def __azimuth(self, a, b):
        """Calculate the azimuth angle from X and Y axis values."""
        azimuth = math.atan2(a, b) * 180.0 / math.pi
        return azimuth if azimuth >= 0 else 360 + azimuth

    def __read_with_azimuth_float(self):
        """Read data from the sensor and calculate azimuth angle."""
        x, y, z, err = self.__read()
        a = self.__azimuth(y, x)
        return x, y, z, a, err

    def __add_data_to_Queue(self, datosBrujulaDigital):
        """Add sensor data to the queue."""
        if self.queue.full():
            self.queue.get()  # Remove the oldest data to maintain the size
        self.queue.put(datosBrujulaDigital)

    def start_reading(self):
        """Start continuous reading from the sensor."""
        self._is_running = True
        while self._is_running:
            try:
                x, y, z, azimuth, err = self.__read_with_azimuth_float()
                datosBrujulaDigital = ("BrujulaDigital", azimuth)
                self.__add_data_to_Queue(datosBrujulaDigital)
                time.sleep(self.delay)
            except Exception as e:
                print(f"Error al leer el sensor: {e}")

    def stop(self):
        """Stop continuous reading from the sensor."""
        self._is_running = False
        print("Sensor Brujula MechaQMC5883 stopped.")

    def get_data(self):
        """Get the latest data from the queue."""
        if self.queue.empty():
            print("BrujulaDigital - No data available")
            return ("BrujulaDigital", -2)
        return self.queue.get()
            
