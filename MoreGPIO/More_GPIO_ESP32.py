from smbus2 import SMBus
import time

class MoreGpio_ESP32:
    # Atributos 
    _Command_Output_ = 100
    _Command_PWM_ = 101
    _Command_Servomotor_ = 102
    _Command_ADC_ = 103
    ADCPin36 = 36
    ADCPin39 = 39
    ADCPin34 = 34
    ADCPin35 = 35
    
    def __init__(self, bus_number=1, address=0x08):
        self.bus = SMBus(bus_number)
        self.address = address

    def set_address(self, new_address):
        self.address = new_address

    def send_command(self, command, pin, value):
        data = [pin, value]
        # Crear un bloque de datos con el comando y los datos
        block = [command] + data
        self.bus.write_i2c_block_data(self.address, command, data)
        #print(f"Data sent: {block}")

    def read_command(self, command, pin, value=0,_delay_=0.05):
        try:
            self.send_command(command, pin, value)  # Enviar el comando para solicitar los datos del sensor específico
            time.sleep(_delay_)  # Esperar un momento para que el esclavo procese la solicitud
            # Leer tres bytes del esclavo
            data = self.bus.read_i2c_block_data(self.address, 0, 3)
            # Combinar los bytes en un valor de 16 bits
            sensor_value = data[0] | (data[1] << 8)
            idPinReturn = data[2]
            return sensor_value, idPinReturn
        except Exception as e:
            print(f"I2C communication error: {e}")
            return None
        
    def readSensor(self, command, pin, cont, delay=0.01):
        while True:
            sensor_value, idPinReturn = self.read_command(command, pin, cont, delay)
            #print(f"{pin} - {idPinReturn}")
            if pin == idPinReturn:
                return sensor_value, idPinReturn
                break;