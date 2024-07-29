import time
import queue
import tfmplus as tfmP # Import the tfmplus module v0.1.0
from tfmplus import *  # and command and parameter definitions

class LidarSensor:
    def __init__(self, serial_port="/dev/ttyAMA0", baud_rate=115200, max_queue_size=3):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.data_queue = queue.Queue(maxsize=max_queue_size)
        self._is_running = False
        self.__initializeOkay = False
        self.__FrameRate = 20

    def initialize(self, frame_rate=20):
        self.__FrameRate = frame_rate
        # Initialization code for the LIDAR sensor
        print("Initializing LIDAR sensor...")
        if tfmP.begin(self.serial_port, self.baud_rate):
            print("Serial port ready.")
            self.__initializeOkay = True
        else:
            print("Failed to initialize LIDAR sensor.")
            self.__initializeOkay = False
            return False
        
        print("Performing system reset...")
        if not tfmP.sendCommand(tfmP.SOFT_RESET, 0):
            print("Failed to reset the sensor.")
            self.__initializeOkay = False
            return False
        
        time.sleep(0.5)
        print("Setting frame rate...")
        if not tfmP.sendCommand(tfmP.SET_FRAME_RATE, frame_rate):
            print("Failed to set frame rate.")
            self.__initializeOkay = False
            return False
        
        self.__initializeOkay = True
        return True
    
    def start_reading(self):
        self._is_running = True
        _delayReading_ = 1/self.__FrameRate
        while self._is_running:
            time.sleep(_delayReading_)  # Adjust based on your frame rate
            try:
                if self.__initializeOkay==True:
                    tfmP.getData()
                    data = ("Lidar", tfmP.dist)
                    self._add_data_to_queue(data)
                else:
                    #tfmP.printFrame()
                    data = ("Lidar", -1)
                    self._add_data_to_queue(data)
                    print("Sensor lidar - Error reading data")
            except Exception as e:
                print(f"Sensor lidar - Error reading data: {e}")

    def stop_reading(self):
        self._is_running = False
        print("Sensor lidar stopped.")

    def _add_data_to_queue(self, data):
        if self.data_queue.full():
            self.data_queue.get()  # Remove the oldest data
        self.data_queue.put(data, block=False)  # Add new data

    def get_data(self):
        # Get and remove the oldest data from the queue
        if not self.data_queue.empty():
            return self.data_queue.get()# Remove and return the oldest data
        else:
            data = ("Lidar", -2)
            print("Sensor lidar - No data available")
            return data
