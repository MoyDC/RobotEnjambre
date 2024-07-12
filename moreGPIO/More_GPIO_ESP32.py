from smbus2 import SMBus
import time

class MoreGpio_ESP32:
    def __init__(self, bus_number=1, address=0x08):
        self._bus = SMBus(bus_number)
        self._address = address
        self._command_output = 100
        self._command_pwm = 101
        self._command_servomotor = 102
        self._command_adc = 103

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
        data = [pin, value]
        block = [command] + data
        self._bus.write_i2c_block_data(self._address, command, data)

    def read_commandAux(self, command, pin, value=0, _delay_=0.05):
        try:
            self.send_command(command, pin, value)
            time.sleep(_delay_)
            data = self._bus.read_i2c_block_data(self._address, 0, 3)
            value = data[0] | (data[1] << 8)
            idPinReturn = data[2]
            return value, idPinReturn
        except Exception as e:
            print(f"I2C communication error: {e}")
            return None

    def read_command(self, command, pin_id, ValueSend=0, delay=0.01):
        while True:
            valueReturn, idPinReturn = self.read_commandAux(command, pin_id, ValueSend, delay)
            if pin_id == idPinReturn:
                return valueReturn, idPinReturn
                break