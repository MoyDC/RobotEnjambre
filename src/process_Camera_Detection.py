import time
import threading
from sensores.camara.objectDetection import ObjectDetection

def Process_Camera_Detection():
    from main import interruption_received
    
    # codigo proceso_camara_deteccion
    try:
        camara = ObjectDetection(display_width=640, display_height=480, show_feed=True)
        camara_thread = threading.Thread(target=camara.start)
        camara_thread.start()
        
        running_process_while = True
        
        while running_process_while:
            #print("Proceso - proceso_camara_deteccion")
            time.sleep(0.5)
            
            
            if interruption_received.is_set():
                running_process_while  = False
                print("Flag recibida - proceso_camara_deteccion")
                
    finally:
        if camara is not None:
            camara.stop()
        
        if camara_thread.is_alive():
            camara_thread.join()
            
        print("End proceso_camara_deteccion")