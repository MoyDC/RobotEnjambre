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

    def _capture_frames(self):
        self._is_running_capture_frames = True
        while self._is_running_capture_frames:
            frame = self.picamera2.capture_array()
            if frame is not None:
                with self.queue_lock:
                    if self.frame_queue.full():
                        self.frame_queue.get()  # Remove the oldest frame if queue is full
                    self.frame_queue.put(frame)  # Add the new frame to the queue
    
    def get_frame(self):
        """Public method to get a frame from the queue."""
        with self.queue_lock:
            if not self.frame_queue.empty():
                size = self.frame_queue.qsize()
                print(f"Queue size: {size}")
                return self.frame_queue.get()
            else:
                return None

    def show_frame(self, frame):
        if frame is not None:
            if self.show_feed:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                frame_resized = cv2.resize(frame, (self.display_width, self.display_height))
                cv2.imshow('Camera', frame_resized)
                cv2.waitKey(200)
        else:
            print("No frames to show.")

    def stop(self):
        self._is_running_capture_frames = False
        self.picamera2.close()
        cv2.destroyAllWindows()
        print("Camera stopped.")

class ObjectDetector:
    def __init__(self, object_detection):
        self.object_detection = object_detection

    def detect_objects(self):
        while True:
            frame = self.object_detection.get_frame()
            if frame is not None:
                # Aquí puedes realizar la detección de objetos
                print("Processing frame for object detection...")
                # Por ejemplo, podrías usar OpenCV para la detección
                # processed_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                # Realizar la detección de objetos en processed_frame
                time.sleep(0.5)
            else:
                print("No frames to process.")
            time.sleep(0.1)  # Pequeño retraso para evitar un bucle demasiado rápido


if __name__ == "__main__":
    camera = Camera_Picamera2(display_width=640, display_height=480, show_feed=False)
    
    # Crear e iniciar el hilo para capturar frames
    capture_thread = threading.Thread(target=camera._capture_frames)
    capture_thread.start()
    
    # Agregar un pequeño retraso para dar tiempo a que la cámara empiece a capturar frames
    time.sleep(1)  # Ajusta este tiempo según sea necesario

    # Crear una instancia de ObjectDetector y pasarle la instancia de ObjectDetection
    detector = ObjectDetector(camera)
    
    # Crear e iniciar el hilo para la detección de objetos
    detection_thread = threading.Thread(target=detector.detect_objects)
    detection_thread.start()
    
    # Crear e iniciar el hilo principal para mostrar frames
    #main_thread = threading.Thread(target=detection.start)
    #main_thread.start()
    
    try:
        # Esperar a que el hilo principal termine
        #main_thread.join()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        # Asegurarse de que los hilos también terminen
        camera.stop()
        capture_thread.join()
        detection_thread.join()
