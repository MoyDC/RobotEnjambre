import time
import sys
from queue import Queue
import tfmplus as tfmP # Import the `tfmplus` module v0.1.0
from tfmplus import *  # and command and parameter definitions

#Queue para almacenar los datos del lidar
Queue_datosLidar = Queue(maxsize=3)
# Función para el hilo que lee el sensor LIDAR
def leer_lidar():
    # Configuración del sensor LIDAR
    serialPort = "/dev/ttyAMA0"  # Raspberry Pi normal serial port
    serialRate = 115200          # TFMini-Plus default baud rate

    print("\n\rTFMPlus Module Example - 06SEP2021")

    # - - - Set and Test serial communication - - - -
    print("Serial port: ", end='')
    if tfmP.begin(serialPort, serialRate):
        print("ready.")
    else:
        print("not ready")
        sys.exit()   #  quit the program if serial not ready
    
    # - - Perform a system reset - - - - - - - -
    print("Soft reset: ", end='')
    if tfmP.sendCommand(SOFT_RESET, 0):
        print("passed.")
    else:
        tfmP.printReply()
    # - - - - - - - - - - - - - - - - - - - - - - - -
    time.sleep(0.5)  # allow 500ms for reset to complete

    # - - Get and Display the firmware version - - - - - - -
    print("Firmware version: ", end='')
    if tfmP.sendCommand(GET_FIRMWARE_VERSION, 0):
        print(str(tfmP.version[0]) + '.', end='')  # print three numbers
        print(str(tfmP.version[1]) + '.', end='')  # separated by a dot
        print(str(tfmP.version[2]))
    else:
        tfmP.printReply()
    # - - - - - - - - - - - - - - - - - - - - - - - -
    # - - Set the data-frame rate to 20Hz - - - - - - - -
    print("Data-Frame rate: ", end='')
    if tfmP.sendCommand(SET_FRAME_RATE, FRAME_20):
        print(str(FRAME_20) + 'Hz')
    else:
        tfmP.printReply()
    # - - - - - - - - - - - - - - - - - - - - - - - -
    time.sleep(0.5)     # Wait half a second.
    #contador_datos = 0
    try:
        while True:
            #start_time = time.time()
            time.sleep(0.05)   # Loop delay 50ms to match the 20Hz data frame rate
            # Use the 'getData' function to get data from device
            if( tfmP.getData()):
                # Almacenar datos al Queue
                #print(f"Lidar: {tfmP.dist}")
                datosLidar = ("Lidar", tfmP.dist)
                Queue_datosLidar.put(datosLidar)
            else:                  # If the command fails...
                tfmP.printFrame()    # display the error and HEX data
            #end_time = time.time()
            #elapsed_time = end_time - start_time
            #print(f"Tiempo transcurrido: {elapsed_time} segundos")
    except KeyboardInterrupt:
        print("Proceso de leer datos lidar finalizado.")