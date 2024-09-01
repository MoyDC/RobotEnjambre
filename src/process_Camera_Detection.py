import time
import threading
import multiprocessing
from hardware.sensores.camera import Camera_Picamera2

# Global flag to indicate if a KeyboardInterrupt was received
interruption_received = multiprocessing.Event() 

def Process_Camera_Detection():    
    # codigo proceso_camara_deteccion
    try:
        camera = Camera_Picamera2(display_width=640, display_height=480, show_feed=True)
        camara_thread = threading.Thread(target=camera._capture_frames)
        camara_thread.start()
        
        running_process_while = True
        time.sleep(2)
        
        while running_process_while:
            #print("Proceso - proceso_camara_deteccion")
            time.sleep(0.01)
            frame = camera.get_frame()
            camera.show_frame(frame)
            
            if interruption_received.is_set():
                running_process_while  = False
                print("Flag recibida - proceso_camara_deteccion")

    except KeyboardInterrupt:
        print("\nInterrupción recibida en proceso de cámara...\n")

    finally:
        if camera is not None:
            camera.stop()
        
        if camara_thread.is_alive():
            camara_thread.join()
            
        print("End proceso_camara_deteccion")