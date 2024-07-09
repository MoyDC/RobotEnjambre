import time
from gpiozero import LED

# Configuración del LED en el pin GPIO 18
led = LED(18) 
# Función para el hilo que controla el LED
def control_led():
    delayLed = 0.25
    try:
        while True:
            #start_time = time.time()
            led.on()  # Enciende el LED
            time.sleep(delayLed)
            led.off()  # Apaga el LED
            time.sleep(delayLed)
            #end_time = time.time()
            #elapsed_time = end_time - start_time
            #print(f"Tiempo transcurrido: {elapsed_time} segundos")
    except KeyboardInterrupt:
        print(f"Blink led finalizado.")