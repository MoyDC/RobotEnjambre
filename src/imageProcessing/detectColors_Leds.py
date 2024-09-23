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

    def __create_mask(self, frame_in_color_HSV, lower, upper, index, masks, delay_reduce_CPU=0.0001):
        """Function to create a mask and store it in the correct index."""
        time.sleep(delay_reduce_CPU) # Sleep to reduce CPU usage

        mask = cv2.inRange(frame_in_color_HSV, lower, upper)
        with self.__lock:
            masks[index] = mask  # Store the mask in the correct index
        end_time = time.time()  # End timer

    def __get_masks_in_Color_HSV(self, frame_in_color_HSV, ranges_color_HSV, delay_reduce_CPU=0.001):
        """Creates masks based on the provided HSV color ranges using threads."""
        time.sleep(delay_reduce_CPU) # Sleep to reduce CPU usage

        masks = [None] * len(ranges_color_HSV)  # Pre-initialize the list with None
        threads = []

        # Create and start a thread for each mask calculation
        for index, (lower, upper) in enumerate(ranges_color_HSV):
            thread = threading.Thread(target=self.__create_mask, args=(frame_in_color_HSV, lower, upper, index, masks))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        
        return masks
    
    def __detect_rectangles(self, mask, index, rectangles_list, delay_reduce_CPU=0.0001):
        """Function to detect rectangles from a mask and store them in the correct index."""
        time.sleep(delay_reduce_CPU) # Sleep to reduce CPU usage

        detected_rectangles = []
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Find contours in the mask

        # Draw rectangles around each contour
        for contour in contours:
            # Get the bounding rectangle of the contour
            x, y, w, h = cv2.boundingRect(contour)
            # Calculate the corners of the rectangle
            top_left = (x, y)
            top_right = (x + w, y)
            bottom_left = (x, y + h)
            bottom_right = (x + w, y + h)
            # Save the corners of the rectangle in the list
            detected_rectangles.append((top_left, top_right, bottom_left, bottom_right))

        with self.__lock:
            rectangles_list[index] = detected_rectangles  # Store the rectangles in the correct index

    def __get_all_rectangles_in_masks(self, mask_array, delay_reduce_CPU=0.001):
        """
        This function receives a list of masks and returns a list of lists,
        where each inner list contains the rectangles detected in the corresponding mask.
        """
        time.sleep(delay_reduce_CPU) # Sleep to reduce CPU usage

        all_rectangles = [None] * len(mask_array)  # Pre-initialize the list with None
        threads = []

        # Create and start a thread for each mask processing
        for index, mask in enumerate(mask_array):
            thread = threading.Thread(target=self.__detect_rectangles, args=(mask, index, all_rectangles))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        return all_rectangles
    
    def __rectangles_intersect(self, rect1, rect2, delay_reduce_CPU=0.00001):
        """
        This function receives two rectangles (each defined by its four corners)
        and checks if they intersect. If they intersect, it returns the corners of the 
        resulting intersection rectangle. Otherwise, it returns None.
        """
        time.sleep(delay_reduce_CPU) # Sleep to reduce CPU usage

        x1_min, y1_min = rect1[0]  # Top-left corner of rectangle 1
        x1_max, y1_max = rect1[3]  # Bottom-right corner of rectangle 1

        x2_min, y2_min = rect2[0]  # Top-left corner of rectangle 2
        x2_max, y2_max = rect2[3]  # Bottom-right corner of rectangle 2

        x_inter_min = max(x1_min, x2_min)
        y_inter_min = max(y1_min, y2_min)
        x_inter_max = min(x1_max, x2_max)
        y_inter_max = min(y1_max, y2_max)

        if x_inter_min < x_inter_max and y_inter_min < y_inter_max:
            top_left = (x_inter_min, y_inter_min)
            top_right = (x_inter_max, y_inter_min)
            bottom_left = (x_inter_min, y_inter_max)
            bottom_right = (x_inter_max, y_inter_max)
            return (top_left, top_right, bottom_left, bottom_right)
        else:
            return None  # No intersection

    def __detect_intersections(self, rects_mask1, rects_mask2, delay_reduce_CPU=0.0001):
        """
        Detects intersections between rectangles from mask1 and mask2.
        Returns a list with the corners of the rectangles from mask2 that intersected with mask1.
        """
        time.sleep(delay_reduce_CPU) # Sleep to reduce CPU usage

        rects_intersections_mask2 = []
        checked_rectangles = set()  # Set to keep track of rectangles that have been checked

        # Create a list to keep track of indices of rectangles that will be removed
        indices_to_remove = []

        for i, rect1 in enumerate(rects_mask1):
            for j, rect2 in enumerate(rects_mask2):
                if (i, j) in checked_rectangles:
                    continue  # Skip if this pair has already been checked

                intersection = self.__rectangles_intersect(rect1, rect2)
                if intersection:
                    # If there is an intersection, save the rectangle from mask2
                    rects_intersections_mask2.append(rect2)
                    checked_rectangles.add((i, j))  # Mark this pair as checked
            
            # Remove rectangles from rects_mask2 that have been intersected with any in rects_mask1
            indices_to_remove.extend([j for j in range(len(rects_mask2)) if (i, j) in checked_rectangles])

        # Remove rectangles that have already been checked
        rects_mask2 = [rect for idx, rect in enumerate(rects_mask2) if idx not in indices_to_remove]

        return rects_intersections_mask2
    
    def __get_led_rectangles_detected(self, mask_array, delay_reduce_CPU=0.001):
        """
        This function receives a list of masks and returns the corners of the rectangles of the blue led 
        from the last mask that intersected with rectangles from the previous masks.
        """
        time.sleep(delay_reduce_CPU) # Sleep to reduce CPU usage

        # Step 1: Get rectangles from all masks
        all_rectangles = self.__get_all_rectangles_in_masks(mask_array)
        
        if not all_rectangles:
            return []

        # Start with rectangles from the last mask
        intersecting_rectangles = all_rectangles[-1]

        # Iterate from the second-to-last mask to the first mask
        for rects in reversed(all_rectangles[:-1]):
            intersecting_rectangles = self.__detect_intersections(intersecting_rectangles, rects)

        return intersecting_rectangles
    
    def __create_led_detection_overlay(self, frame, detected_rectangles, delay_reduce_CPU=0.001):
        """
        Creates an overlay with rectangles drawn around the detected target color LEDs.
        """
        time.sleep(delay_reduce_CPU) # Sleep to reduce CPU usage

        # Create an empty overlay with the same size as the frame
        overlay = np.zeros_like(frame)

        # Draw rectangles on the overlay
        for rect in detected_rectangles:
            top_left, top_right, bottom_left, bottom_right = rect
            # Use the corners to draw a filled rectangle on the overlay
            cv2.rectangle(overlay, top_left, bottom_right, (0, 255, 0), thickness=20)  # White color in the overlay

        return overlay
    
    def __get_Blue_Led_Range_Color_HVS(self):
        """Returns the HSV color range values for the blue led."""
        # HSV color range values for the blue led 
        lower_1 = np.array([0, 0, 230])
        upper_1 = np.array([100, 30, 255])

        lower_2 = np.array([70, 175, 240])
        upper_2 = np.array([110, 220, 255])

        lower_3 = np.array([110, 180, 240])
        upper_3 = np.array([120, 205, 255]) 

        #(lower_1, upper_1), 
        return [(lower_2, upper_2), (lower_3, upper_3)]
    
    def __get_Green_Led_Range_Color_HVS(self):
        """Returns the HSV color range values for the green led."""
        # HSV color range values for the green led 
        lower_1 = np.array([0, 0, 230])
        upper_1 = np.array([100, 30, 255])

        lower_2 = np.array([90, 200, 250])
        upper_2 = np.array([110, 220, 255])

        lower_3 = np.array([60, 200, 240])
        upper_3 = np.array([80, 210, 255]) 

        #(lower_1, upper_1), 
        return [(lower_2, upper_2), (lower_3, upper_3)]

    def get_blue_led_overlay(self):
        """Retrieve data from the queue."""
        with self.__lock:
            if self.__blue_led_overlay_queue.empty():
                return None, None
            return self.__blue_led_overlay_queue.get() 
        
    def create_blue_led_detection_overlays(self, delay_reduce_CPU = 0.1):
        time.sleep(2)
        range_blue_led = self.__get_Blue_Led_Range_Color_HVS()
        #range_green_led = self.__get_Green_Led_Range_Color_HVS()

        self.__running_create_blue_led_detection_overlay = True
        while self.__running_create_blue_led_detection_overlay:
            start_time = time.time() # Inicia el temporizador
            time.sleep(delay_reduce_CPU) # Sleep to reduce CPU usage

            frame = self.camera.get_frame()
            if frame is None:
                print("No frame in create_blue_led_detection_overlays")
                continue
            
            frame_in_HSV = self.__get_frame_in_HSV(frame)     

            masks_blue_led = self.__get_masks_in_Color_HSV(frame_in_HSV, range_blue_led) 
            #masks_green_led = self.__get_masks_in_Color_HSV(frame_in_HSV, range_green_led)   

            blue_led_detected_rectangles = self.__get_led_rectangles_detected(masks_blue_led)
            #green_led_detected_rectangles = self.__get_led_rectangles_detected(masks_green_led)

            blue_led_overlay = self.__create_led_detection_overlay(frame, blue_led_detected_rectangles)
            #green_led_overlay = self.__create_led_detection_overlay(frame, green_led_detected_rectangles)

            #combined_mask_overlay = cv2.bitwise_or(blue_led_overlay, green_led_overlay)

            data_to_store = (frame, blue_led_overlay)
            self.__add_to_queue(self.__blue_led_overlay_queue, data_to_store)

            #data_to_store = (frame, green_led_overlay)
            #self.__add_to_queue(self.__blue_led_overlay_queue, data_to_store)

            end_time = time.time() # Finaliza el temporizador
            elapsed_time = end_time - start_time # Calcula el tiempo transcurrido
            print(f"Time create_led_blue_detection_overlays: {elapsed_time}")
    
    def stop(self):
        self.__running_create_blue_led_detection_overlay = False
        self.__running_create_green_led_detection_overlay = False
        print("Create overlays for leds stopped.")

