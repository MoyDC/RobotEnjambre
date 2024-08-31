from picamera2 import Picamera2
import cv2

class ObjectDetection:
    def __init__(self, display_width=640, display_height=480, show_feed=False):
        self.display_width = display_width
        self.display_height = display_height
        self.show_feed = show_feed  # Add a flag to control visualization
        self.picamera2 = Picamera2()
        self.camera_config = self.picamera2.create_still_configuration()
        self.camera_config["size"] = (self.display_width, self.display_height)
        self.picamera2.configure(self.camera_config)
        self.picamera2.start()
        self.picamera2.set_controls({
            'ExposureTime': 50000,
            'Brightness': 0.2
        })
        self._is_running = False
        
    def read_frame(self):
        frame = self.picamera2.capture_array()
        if frame is None:
            raise Exception("No se pudo capturar el frame de la camara")
        return frame
    
    def show_frame(self, frame):
        if self.show_feed:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame_resized = cv2.resize(frame, (self.display_width, self.display_height))
            cv2.imshow('Camera', frame_resized)

    def start(self):
        self._is_running = True
        try:
            while self._is_running:
                frame = self.read_frame()
                self.show_frame(frame)
                cv2.waitKey(1)
        except Exception as e:
            print(f"Camara - Error reading data: {e}")
        finally:
            cv2.destroyAllWindows()

    def stop(self):
        self._is_running = False
        self.picamera2.close()
        cv2.destroyAllWindows()
        print("Camara stopped.")

        
def main():
    # Crea una instancia de ObjectDetection con las dimensiones deseadas
    camera = ObjectDetection(display_width=640, display_height=480, show_feed=True)
    
    # Variables para medir FPS
#    fps = 0
#    prev_time = time.time()
    
    
    
    try:
        while True:
            print("En   el while")
            
            camera.start()
            #frame = camera.read_frame()

            # Muestra el frame
            #camera.show_frame(frame)
            
            # Calcula el tiempo actual
#            curr_time = time.time()

            # Calcula el tiempo transcurrido y actualiza el FPS
#            time_elapsed = curr_time - prev_time
#            fps += 1
            
#            if time_elapsed >= 1.0:  # Actualiza el FPS cada segundo
#                print(f"FPS: {fps}")
#                fps = 0
#                prev_time = curr_time
                
            # Sale del bucle si se presiona la tecla 'q'
#            if cv2.waitKey(1) & 0xFF == ord('q'):
#                break
            
    except KeyboardInterrupt:
        print("End1")
        
    except Exception as e:
       print(f"Error: {e}")
        
    finally:
        camera.stop()
        print("End2")
        
if __name__ == "__main__":
    main()