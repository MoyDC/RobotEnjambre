import time
import threading
import multiprocessing
import cv2
import numpy as np
from hardware.sensores.camera import Camera_Picamera2
from imageProcessing.detectColors_Leds import DetectColors_Leds


# Global flag to indicate if a KeyboardInterrupt was received
interruption_received = multiprocessing.Event() 
detect_color1 = multiprocessing.Event() # green
detect_color2 = multiprocessing.Event() # blue



max_size = 3
queue_data_object_in_Camara = multiprocessing.Queue(3)

def add_to_queue_multiprocesos(data1, data2, data3):
    data = [data1, data2, data3];
    if queue_data_object_in_Camara.qsize() >= max_size:
        queue_data_object_in_Camara.get()  # Eliminar el dato más antiguo si está llena
    queue_data_object_in_Camara.put(data)
    #print("Estado de la Queue:", queue_data_object_in_Camara.get())


#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
def Process_Camera_Detection():    
    # codigo proceso_camara_deteccion
    
    try:
        camera = Camera_Picamera2(display_width=640, display_height=480, show_feed=True)
        camara_thread = threading.Thread(target=camera._capture_frames, args=(0.05,))
        camara_thread.start()

        led_Detect = DetectColors_Leds(camera)
        led_Detect_thread = threading.Thread(target=led_Detect.create_blue_led_detection_overlays)
        led_Detect_thread.start()

        green_led_Detect = threading.Thread(target=led_Detect.create_green_led_detection_overlays)
        green_led_Detect.start()

        running_process_while = True
        time.sleep(2)
        cont = 0
        while running_process_while:
            #print("Proceso - proceso_camara_deteccion")
            start_time = time.time() # Inicia el temporizador
            time.sleep(0.01)
            
            if detect_color1.is_set():
                state_hold_GreenLed = False
            else:
                state_hold_GreenLed = True
                
            if detect_color2.is_set():
                state_hold_BlueLed = False
            else:
                state_hold_BlueLed = True

            led_Detect.hold(state_greenLed = state_hold_GreenLed, state_blueLed = state_hold_BlueLed)

            led_overlay = led_Detect.get_led_overlay()
            frame = led_overlay[0]
            mask_led_overlay = led_overlay[1]

            if frame is None or mask_led_overlay is None:
                #print("No frame to show in window")
                time.sleep(0.1)
                continue  # Si no hay frame u overlay, pasa a la siguiente iteración del ciclo
            
            color_object = led_overlay[2]
            mask_original = led_overlay[3]
            result, percentage, area = led_Detect.analyze_position_object_in_mask(mask_original)
            #print(result)
            add_to_queue_multiprocesos(result, percentage, area);

            frame_led = cv2.addWeighted(frame, 0.4, mask_led_overlay, 0.6, 0) # Superponer la imagen del color detectado sobre el frame original
            camera.show_frame(frame_led, 1)
            time.sleep(0.1)
            
            cont = cont + 1
            end_time = time.time() # Finaliza el temporizador
            elapsed_time = end_time - start_time # Calcula el tiempo transcurrido
            #print(f"\n{cont} - Mostrar frame - Time: {elapsed_time}\n")
            
            if interruption_received.is_set():
                running_process_while  = False
                print("Flag recibida - proceso_camara_deteccion")

    except KeyboardInterrupt:
        print("\nInterrupción recibida en proceso de cámara...\n")

    finally:
        if camera is not None:
            camera.stop()
        if led_Detect is not None:
            led_Detect.stop()
        
        if camara_thread.is_alive():
            camara_thread.join()
        if led_Detect_thread.is_alive():
            led_Detect_thread.join()
        if green_led_Detect.is_alive():
            green_led_Detect.join()

        cv2.destroyAllWindows()
        print("End proceso_camara_deteccion")
