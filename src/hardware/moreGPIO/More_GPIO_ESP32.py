from smbus2 import SMBus
import time
import threading

class MoreGpio_ESP32:
    def __init__(self, bus_number=1, address=0x08):
        self._bus_number = bus_number
        self._address = address
        self._bus = None
        self._command_servomotor = 101
        self._command_adc = 102
        self._command_Motor_1 = 103
        self._command_Motor_2 = 104
        self._command_RSTesp32 = 255
        self.i2c_lock = threading.Lock()  # Lock for I2C access
        self._initialize_bus()

    def _initialize_bus(self):
        """Initialize the I2C bus."""
        try:
            self._bus = SMBus(self._bus_number)
            return True
        except Exception as e:
            print(f"Failed to open I2C bus: {e}")
            self._bus = None
            return False

    def _is_i2c_connected(self):
        """Check if the I2C device is connected and accessible."""
        if self._bus is not None:
            return True
        if not self._initialize_bus():
            return False
        return True
    
    def test_is_i2c_working(self):
        """Test if the I2C connection is working by sending a dummy command."""
        return self.send_command(0, 0, 0)

    def send_command(self, command, pin, value):
        """Send a command to the I2C device."""
        with self.i2c_lock:
            if not self._is_i2c_connected():
                print("I2C device is not connected. Cannot send command.")
                return False
            try:
                data = [pin, value]
                self._bus.write_i2c_block_data(self._address, command, data)
                return True
            except Exception as e:
                print(f"I2C communication error during send_command: {e}")
                return False

    def _send_command_and_get_response(self, command, pin, value=0, _delay_=0.05):
        """Send a command and read the response from the I2C device."""
        try:
            is_i2c_connected = self.send_command(command, pin, value)
            if not is_i2c_connected:
                return None, None
            time.sleep(_delay_)
            data = self._bus.read_i2c_block_data(self._address, 0, 3)
            if len(data) == 3:
                value = data[0] | (data[1] << 8)
                idPinReturn = data[2]
                return value, idPinReturn
            else:
                print("Received incomplete data.")
                return None, None
        except Exception as e:
            print(f"I2C communication error: {e}")
            return None, None

    def read_command(self, command, pin_id, ValueSend=0, delay=0.01):
        """Read a command response with retries."""
        for attempt in range(3):  # Try a few times before failing
            valueReturn, idPinReturn = self._send_command_and_get_response(command, pin_id, ValueSend, delay)
            if valueReturn is not None and idPinReturn == pin_id:
                return valueReturn, idPinReturn
            time.sleep(delay)
        return None, None
