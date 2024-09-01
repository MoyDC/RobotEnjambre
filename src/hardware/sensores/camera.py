from picamera2 import Picamera2
import cv2
import threading
import queue
import time

class Camera_Picamera2:
    def __init__(self, display_width=640, display_height=480, show_feed=False):
        self.display_width = display_width
        self.display_height = display_height
        self.show_feed = show_feed
        self.picamera2 = Picamera2()
        self.camera_config = self.picamera2.create_still_configuration()
        self.camera_config["size"] = (self.display_width, self.display_height)
        self.picamera2.configure(self.camera_config)
        self.picamera2.start()
        self.picamera2.set_controls({
            'ExposureTime': 50000,
            'Brightness': 0.2
        })
        self._is_running_capture_frames = False
        
        # Create a queue to hold frames with a max size of 3
        self.frame_queue = queue.Queue(maxsize=3)
        # Create a Lock for synchronizing access to the queue
        self.queue_lock = threading.Lock()

    def __add_frame_to_Queue(self, frame):
        """Add frame data to the queue."""
        if self.frame_queue.full():
            self.frame_queue.get()  # Remove the oldest data to maintain the size
        self.frame_queue.put(frame)

    def _capture_frames(self, delay_reduce_CPU = 0.005):
        """Capture frames from the camera."""
        self._is_running_capture_frames = True
        while self._is_running_capture_frames:
            time.sleep(delay_reduce_CPU)  # Sleep to reduce CPU usage
            frame = self.picamera2.capture_array()
            if frame is None: continue
            with self.queue_lock:
                self.__add_frame_to_Queue(frame)
            
    def get_frame(self):
        """Retrieve a frame from the queue."""
        with self.queue_lock:
            if self.frame_queue.empty():
                return None
            return self.frame_queue.get() 

    def show_frame(self, frame):
        """Display the frame."""
        if frame is None:
            print("No frames to show.")
            return
        if self.show_feed:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame_resized = cv2.resize(frame, (self.display_width, self.display_height))
            cv2.imshow('Camera', frame_resized)
            cv2.waitKey(200)     

    def stop(self):
        """Stop capturing frames and close the camera."""
        self._is_running_capture_frames = False
        self.picamera2.close()
        cv2.destroyAllWindows()
        print("Camera stopped.")
