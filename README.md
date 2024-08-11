# Robot Enjambre

### Camera Raspberry Pi Libraries

1. Crear entorno virtual
2. Buscar archivo `pyvenv.cfg`
3. Cambiar esta línea a true: `include-system-site-packages = true`
   - **Nota:** `numpy==1.24.2` y `picamera2==0.3.18` se importan cambiando el comando anterior a `true`
4. Activar entorno virtual en la terminal
5. Ejecutar `sudo apt update`
6. Ejecutar `sudo apt upgrade`
7. Instalar matplotlib: `pip install matplotlib==3.6.3`
8. Instalar OpenCV: `pip install opencv-python==4.6.0.66`

### Instalar en el entorno virtual estas librerías:

- `tfmplus==0.1.0`
- `simple-pid==2.0.1`
