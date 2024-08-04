from smbus2 import SMBus
import time
import threading

class MoreGpio_ESP32:
    def __init__(self, bus_number=1, address=0x08):
        self._bus = SMBus(bus_number)
        self._address = address
        self._command_output = 100
        self._command_pwm = 101
        self._command_servomotor = 102
        self._command_adc = 103
        self._command_RSTesp32 = 104
        self.i2c_lock = threading.Lock()  # Lock for I2C access

    @property
    def command_output(self):
        return self._command_output

    @property
    def command_pwm(self):
        return self._command_pwm

    @property
    def command_servomotor(self):
        return self._command_servomotor

    @property
    def command_adc(self):
        return self._command_adc

    def set_address(self, new_address):
        self._address = new_address

    def send_command(self, command, pin, value):
        with self.i2c_lock:
            data = [pin, value]
            block = [command] + data
            self._bus.write_i2c_block_data(self._address, command, data)

    def read_commandAux(self, command, pin, value=0, _delay_=0.05):
        #with self.i2c_lock:
        try:
            self.send_command(command, pin, value)
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
        for attempt in range(3):  # Try a few times before failing
            valueReturn, idPinReturn = self.read_commandAux(command, pin_id, ValueSend, delay)
            if valueReturn is not None and idPinReturn == pin_id:
                return valueReturn, idPinReturn
            #print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(delay)
        #print("Failed to read from I2C after several attempts.")
        return None, None
