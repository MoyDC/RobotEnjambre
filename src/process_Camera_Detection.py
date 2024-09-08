import time
import threading
import multiprocessing
from hardware.sensores.camera import Camera_Picamera2
import cv2
import numpy as np

# Global flag to indicate if a KeyboardInterrupt was received
interruption_received = multiprocessing.Event() 

#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
def obtener_rectangulos(mask):
    """
    Esta función recibe una máscara (mask) y devuelve una lista con las esquinas
    de los rectángulos delimitadores de los contornos encontrados.
    """
    #start_time = time.time() # Inicia el temporizador

    # Crear una lista para almacenar las posiciones de las esquinas de los rectángulos
    rectangulos_detectados = []
    
    # Encontrar contornos en la máscara
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Dibujar rectángulos alrededor de cada contorno
    for contour in contours:
        # Obtener el rectángulo delimitador del contorno
        x, y, w, h = cv2.boundingRect(contour)
        
        # Calcular las esquinas del rectángulo
        top_left = (x, y)
        top_right = (x + w, y)
        bottom_left = (x, y + h)
        bottom_right = (x + w, y + h)
        
        # Guardar las esquinas del rectángulo en la lista
        rectangulos_detectados.append((top_left, top_right, bottom_left, bottom_right))
    
    #end_time = time.time() # Finaliza el temporizador
    # Calcula el tiempo transcurrido
    #elapsed_time = end_time - start_time
    #print(f"El código tardó {elapsed_time:.6f} segundos en ejecutarse.")

    # Retornar la lista de rectángulos
    return rectangulos_detectados

#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
def rectangulos_se_intersectan(rect1, rect2):
    """
    Esta función recibe dos rectángulos (cada uno definido por sus cuatro esquinas)
    y verifica si se intersectan. Si se intersectan, devuelve las esquinas del 
    rectángulo resultante de la intersección. De lo contrario, devuelve None.
    """
    x1_min, y1_min = rect1[0]  # Esquina superior izquierda del rectángulo 1
    x1_max, y1_max = rect1[3]  # Esquina inferior derecha del rectángulo 1

    x2_min, y2_min = rect2[0]  # Esquina superior izquierda del rectángulo 2
    x2_max, y2_max = rect2[3]  # Esquina inferior derecha del rectángulo 2

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
        return None  # No hay intersección

def detectar_intersecciones(rects_mask1, rects_mask2):
    """
    Detecta intersecciones entre los rectángulos de mask1 y mask2.
    Retorna un array con las esquinas de los rectángulos de mask2 donde intersectaron con mask1.
    """
    rects_intersecciones_mask2 = []

    for rect1 in rects_mask1:
        for rect2 in rects_mask2:
            interseccion = rectangulos_se_intersectan(rect1, rect2)
            if interseccion:
                # Si hay intersección, guardar el rectángulo de mask2
                rects_intersecciones_mask2.append(rect2)
    
    return rects_intersecciones_mask2

#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
def Process_Camera_Detection():    
    # codigo proceso_camara_deteccion
    try:
        camera = Camera_Picamera2(display_width=640, display_height=480, show_feed=True)
        camara_thread = threading.Thread(target=camera._capture_frames)
        camara_thread.start()
        
        running_process_while = True
        time.sleep(2)
        cont = 0
        while running_process_while:
            start_time = time.time() # Inicia el temporizador

            #print("Proceso - proceso_camara_deteccion")
            time.sleep(0.01)
            frame = camera.get_frame()
        
            if frame is None:
                print("No frame")
                continue
            
            # 0.02 seg
            
            # Convertir a espacio de color HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Definir el rango de colores en HSV (ejemplo para color led azul)
            # primer valor 0-179
            # segundo valor de 0-255
            # tercer valor 0 255
            lower_1 = np.array([0, 0, 230])
            upper_1 = np.array([100, 30, 255])

            lower_2 = np.array([70, 175, 240])
            upper_2 = np.array([110, 220, 255])

            lower_3 = np.array([110, 180, 240])
            upper_3 = np.array([130, 210, 255])

            # 0.05 seg - mas 0.03 seg
            
            # Crear una mascara que detecte el color
            mask1 = cv2.inRange(hsv, lower_1, upper_1)
            mask2 = cv2.inRange(hsv, lower_2, upper_2)
            mask3 = cv2.inRange(hsv, lower_3, upper_3)

            # 0.15 seg - mas 0.1 seg

            rectangles_detected_mask1 = obtener_rectangulos(mask1)
            rectangles_detected_mask2 = obtener_rectangulos(mask2)
            rectangles_detected_mask3 = obtener_rectangulos(mask3)

            # 0.2 seg - mas 0.05 seg
            
            # Detectar intersecciones entre los rectangulos de los mask
            rectangulos_interseccion_mask1y2 = detectar_intersecciones(rectangles_detected_mask1, rectangles_detected_mask2)
            rectangulos_resultantes = detectar_intersecciones(rectangulos_interseccion_mask1y2, rectangles_detected_mask3)

            # 0.27 seg - mas 0.07 seg
            

            # Crear una máscara vacía con el mismo tamaño que el frame
            mask_rectangles = np.zeros_like(frame)
            # Dibujar los rectángulos en la máscara
            for rect in rectangulos_resultantes :
                top_left, top_right, bottom_left, bottom_right = rect
                # Usar las esquinas para crear un rectángulo en la máscara
                cv2.rectangle(mask_rectangles, top_left, bottom_right, (255, 255, 255), thickness=cv2.FILLED)  # Color blanco en la máscara

            # 0.33 seg - mas 0.06 seg

            # Superponer la imagen del color detectado sobre el frame original
            superimposed = cv2.addWeighted(frame, 0.4, mask_rectangles, 0.6, 0)

            # 0.39 seg - mas 0.06 seg

            cont = cont + 1
            camera.show_frame(superimposed)

            # 0. 63 seg - mas 0.24 seg

            end_time = time.time() # Finaliza el temporizador
            elapsed_time = end_time - start_time # Calcula el tiempo transcurrido
            print(f"\n{cont} - Mostrar frame - Time: {elapsed_time}\n")
            
            
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
        cv2.destroyAllWindows()
        print("End proceso_camara_deteccion")