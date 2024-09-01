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

    def __initialize_serial_port(self):
        """Initialize the serial port for the LIDAR sensor."""
        if not tfmP.begin(self.serial_port, self.baud_rate):
            print("Failed to initialize LIDAR sensor.")
            return False
        print("Serial port ready.")
        return True
            
    def __perform_system_reset(self):
        """Perform a system reset on the LIDAR sensor."""
        if not tfmP.sendCommand(tfmP.SOFT_RESET, 0):
            print("Failed to reset the sensor.")
            return False
        return True
            
    def __set_frame_rate(self, frame_rate):
        """Set the frame rate for the LIDAR sensor."""
        if not tfmP.sendCommand(tfmP.SET_FRAME_RATE, frame_rate):
            print("Failed to set frame rate.")
            return False
        return True         

    def initialize(self, frame_rate=20):
        """Initialize the LIDAR sensor by performing all necessary setup tasks."""
        self.__FrameRate = frame_rate
        print("Initializing LIDAR sensor...")
        if not self.__initialize_serial_port():
            self.__initializeOkay = False
            return False
        print("Performing system reset...")
        if not self.__perform_system_reset():
            return False
        time.sleep(0.5)
        print("Setting frame rate...")
        if not self.__set_frame_rate(frame_rate):
            return False
        self.__initializeOkay = True
        return True
    
    def _add_data_to_queue(self, data):
        """Add new data to the queue."""
        if self.data_queue.full():
            self.data_queue.get()  # Remove the oldest data
        self.data_queue.put(data, block=False)  # Add new data
        
    def start_reading(self):
        """Start reading data from the LIDAR sensor."""
        self._is_running = True
        _delayReading_ = 1/self.__FrameRate
        while self._is_running:
            time.sleep(_delayReading_)  # Adjust based on your frame rate
            try:
                if not self.__initializeOkay:
                    data = ("Lidar", -1)
                    self._add_data_to_queue(data)
                    print("Sensor lidar - Error reading data")
                    continue
                tfmP.getData()
                data = ("Lidar", tfmP.dist)
                self._add_data_to_queue(data)      
            except Exception as e:
                print(f"Sensor lidar - Error reading data: {e}")

    def stop(self):
        """Stop the reading process."""
        self._is_running = False
        print("Sensor lidar stopped.")

    def get_data(self):
        """Get the latest data from the queue."""
        if self.data_queue.empty():
            print("Sensor lidar - No data available")
            return ("Lidar", -2)
        return self.data_queue.get() 
            
