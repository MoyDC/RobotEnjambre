import time
import cv2
import numpy as np
import threading
import queue

class DetectColors_Leds:
    def __init__(self, instance_camera):
        self.camera = instance_camera
        self.__lock = threading.Lock()  # Initialize a Lock object
        self.__running_create_blue_led_detection_overlay = False
        self.__running_create_green_led_detection_overlay = True
        self.__blue_led_overlay_queue = queue.Queue(maxsize=3) # Create a queue to hold frames with a max size of 3
        self.__led_overlay_queue = queue.Queue(maxsize=6)

    def __add_to_queue(self, queue_obj, data, delay_reduce_CPU=0.0001):
        """Add data to the specified queue."""
        time.sleep(delay_reduce_CPU) # Sleep to reduce CPU usage
        with self.__lock:
            if queue_obj.full():
                queue_obj.get()  # Remove the oldest data to maintain the size
            queue_obj.put(data)

    def __get_frame_in_HSV(self, frame, delay_reduce_CPU=0.0001):
        """Converts the given frame to HSV color space and stores it."""
        time.sleep(delay_reduce_CPU) # Sleep to reduce CPU usage
        return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    def analyze_position_object_in_mask(self, mask):
        """Analyzes the position of the object in relation to the center of the image."""

        # Calculate moments to obtain the center of mass
        M = cv2.moments(mask)
        if M["m00"] != 0:  # Check if an area is detected
            cX = int(M["m10"] / M["m00"])  # X coordinate of the center of mass
            cY = int(M["m01"] / M["m00"])  # Y coordinate of the center of mass

            # Get the dimensions of the mask
            height, width = mask.shape

            # Calculate the position of the reference vertical line (midpoint of the image)
            mid_line_x = width // 2

            # Calculate the distance from the center of mass to the reference line
            distance = cX - mid_line_x

            # Calculate the percentage of the distance relative to the midpoint of the image
            percentage = (distance / mid_line_x) * 100

            # Determine the direction
            if distance < 0:
                return f"Camera - Object is on the left", abs(percentage)
            elif distance > 0:
                return f"Camera - Object is on the right", percentage
            else:
                return "Camera - Object is at the midpoint ", 0.0
        else:
            return "Camera - No Object", None
            
    def create_blue_led_detection_overlays(self, delay_reduce_CPU = 0.2):
        time.sleep(2)
        # HSV color range values for the blue led 
        lower_1 = np.array([0, 0, 230])
        upper_1 = np.array([100, 30, 255])

        lower_2 = np.array([70, 175, 240])
        upper_2 = np.array([120, 220, 255])

        lower_3 = np.array([110, 180, 240])
        upper_3 = np.array([120, 205, 255]) 

        self.__running_create_blue_led_detection_overlay = True
        while self.__running_create_blue_led_detection_overlay:
            start_time = time.time() # Inicia el temporizador
            time.sleep(delay_reduce_CPU) # Sleep to reduce CPU usage

            frame = self.camera.get_frame()
            if frame is None:
                print("No frame in create_blue_led_detection_overlays")
                continue
            
            frame_in_HSV = self.__get_frame_in_HSV(frame)     

            # Crear mascara para los colores
            mask2_blue = cv2.inRange(frame_in_HSV, lower_3, upper_3)
            mask_combined_3_channels = cv2.cvtColor(mask2_blue, cv2.COLOR_GRAY2BGR)

            mask_combined = mask_combined_3_channels
            data_to_store = (frame, mask_combined, "Blue Led", mask2_blue)
            self.__add_to_queue(self.__led_overlay_queue, data_to_store)

            end_time = time.time() # Finaliza el temporizador
            elapsed_time = end_time - start_time # Calcula el tiempo transcurrido
            #print(f"Time create_led_blue_detection_overlays: {elapsed_time}")

    def create_green_led_detection_overlays(self, delay_reduce_CPU = 0.2):
        time.sleep(2)
        # HSV color range values for the green led 
        lower_1 = np.array([0, 0, 230])
        upper_1 = np.array([100, 30, 255])

        lower_2 = np.array([60, 200, 250])
        upper_2 = np.array([110, 220, 255])

        lower_3 = np.array([60, 200, 240])
        upper_3 = np.array([80, 210, 255]) 

        self.__running_create_green_led_detection_overlay = True
        while self.__running_create_green_led_detection_overlay:
            start_time = time.time() # Inicia el temporizador
            time.sleep(delay_reduce_CPU) # Sleep to reduce CPU usage

            frame = self.camera.get_frame()
            if frame is None:
                print("No frame in create_blue_led_detection_overlays")
                continue
            
            frame_in_HSV = self.__get_frame_in_HSV(frame)     

            # Crear mascara para los colores
            mask2_green_1 = cv2.inRange(frame_in_HSV, lower_2, upper_2)
            mask2_green_2 = cv2.inRange(frame_in_HSV, lower_3, upper_3)

            # Crear mascara combinada usando AND lÃ³gico entre mask2 y mask3
            mask_combined_green = cv2.bitwise_and(mask2_green_1, mask2_green_2)
            mask_combined_3_channels = cv2.cvtColor(mask_combined_green, cv2.COLOR_GRAY2BGR)

            mask_combined = mask_combined_3_channels
            data_to_store = (frame, mask_combined, "Green Led", mask_combined_green)
            self.__add_to_queue(self.__led_overlay_queue, data_to_store)

            end_time = time.time() # Finaliza el temporizador
            elapsed_time = end_time - start_time # Calcula el tiempo transcurrido
            #print(f"Time create_led_blue_detection_overlays: {elapsed_time}")

    def get_led_overlay(self):
        """Retrieve data from the queue."""
        with self.__lock:
            if self.__led_overlay_queue.empty():
                return None, None
            return self.__led_overlay_queue.get() 

    def stop(self):
        self.__running_create_blue_led_detection_overlay = False
        self.__running_create_green_led_detection_overlay = False
        print("Create overlays for leds stopped.")

