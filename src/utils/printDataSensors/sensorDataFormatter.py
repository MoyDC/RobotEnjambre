import time

# Clase para formatear y imprimir los datos de los sensores
class SensorDataFormatter:
    def __init__(self, sensors, lidar_sensor, sensor_Infrarrojo, sensorBrujula, readADC, sensorsNames):
        self.sensors = sensors
        self.lidar_sensor = lidar_sensor
        self.sensor_Infrarrojo = sensor_Infrarrojo
        self.sensorBrujula = sensorBrujula
        self.readADC = readADC
        self.sensorsNames = sensorsNames  # Almacenar sensorsNames
        self.contador_datos = 0
        self._is_running = False
        self._thread = None

    def format_data(self):
        """Format the sensor data into a readable string."""
        self.contador_datos += 1
        S1 = self.sensors.get(self.sensorsNames[0]).get_data()
        S2 = self.sensors.get(self.sensorsNames[1]).get_data()
        S3 = self.sensors.get(self.sensorsNames[2]).get_data()
        S4 = self.sensors.get(self.sensorsNames[3]).get_data()
        Lidar_cm = self.lidar_sensor.get_data()
        Infrarrojo = self.sensor_Infrarrojo.get_data()
        AngBrujula = self.sensorBrujula.get_data()
        SensorLDR1 = self.readADC.get_dataADC_LDR1()
        SensorLDR2 = self.readADC.get_dataADC_LDR2()
        ADC1 = self.readADC.get_dataADC1()
        ADC2 = self.readADC.get_dataADC2()
        formatted_data = (
            f"Cont {self.contador_datos}: "
            f"{S1[0]}: {S1[1]:.2f} cm - "
            f"{S2[0]}: {S2[1]:.2f} cm - "
            f"{S3[0]}: {S3[1]:.2f} cm - "
            f"{S4[0]}: {S4[1]:.2f} cm - "
            f"Lidar: {Lidar_cm[1]} cm - "
            f"Infra: {Infrarrojo[1]} - "
            f"Bruj: {AngBrujula[1]:.2f} - "
            f"LDR1: {SensorLDR1[1]} - "
            f"LDR2: {SensorLDR2[1]} - "
            f"ADC1: {ADC1[1]} - "
            f"ADC2: {ADC2[1]}"
        )
        return formatted_data

    def start(self, delay=0.1, Run=True):
        """Start the data formatting and printing loop."""
        self._is_running = True
        time.sleep(0.5)
        while self._is_running and Run:
            formatted_data = self.format_data()
            print(formatted_data)
            time.sleep(delay)  # Ajusta el tiempo de espera según sea necesario

    def stop(self):
        """Stop the data formatting process."""
        self._is_running = False
        print("SensorDataFormatter stopped.")