class RobotController_StateMachine:
    def __init__(self):
        # Estado inicial
        self.current_state = "Inicio"
        self.error = False
        self.zona_objeto_encontrado = False
        self.zona_nido_encontrada = False
        self.luz_maxima = False

    def estado_inicio(self):
        # Comprobación de errores en la configuración inicial
        print("Estado: Inicio")
        self.error = self.check_for_errors()
        if self.error:
            print("Error detectado. No se puede continuar.")
            return
        # Si no hay errores, avanza al siguiente estado
        self.current_state = "Buscar Zona Objetos"

    def estado_buscar_zona_objetos(self):
        # Buscar la zona de objetos con la cámara
        print("Estado: Buscar Zona Objetos")
        self.zona_objeto_encontrado = self.buscar_zona_objetos()
        if self.zona_objeto_encontrado:
            self.current_state = "Zona Objetos"
        else:
            self.current_state = "Zona Cercana de Mayor Luz 1"

    def estado_zona_cercana_de_mayor_luz_1(self):
        # Buscar la zona cercana con mayor luz usando los sensores LDR
        print("Estado: Zona Cercana de Mayor Luz 1")
        self.luz_maxima = self.buscar_luz_maxima()
        self.current_state = "Buscar Zona Objetos"

    def estado_zona_objetos(self):
        # Comprobar si se ha llegado a la zona de objetos
        print("Estado: Zona Objetos")
        if self.comprobar_llegada_zona_objetos():
            self.current_state = "Buscar Nido"
        else:
            print("No se ha llegado a la zona de objetos, seguir avanzando")

    def estado_buscar_nido(self):
        # Buscar el nido con la cámara
        print("Estado: Buscar Nido")
        self.zona_nido_encontrada = self.buscar_zona_nido()
        if self.zona_nido_encontrada:
            self.current_state = "Zona Nido"
        else:
            self.current_state = "Zona Cercana de Mayor Luz 2"

    def estado_zona_cercana_de_mayor_luz_2(self):
        # Buscar la zona cercana con mayor luz nuevamente
        print("Estado: Zona Cercana de Mayor Luz 2")
        self.luz_maxima = self.buscar_luz_maxima()
        self.current_state = "Buscar Nido"

    def estado_zona_nido(self):
        # Comprobar si se ha llegado a la zona del nido
        print("Estado: Zona Nido")
        if self.comprobar_llegada_zona_nido():
            self.current_state = "Buscar Zona Objetos"
        else:
            print("No se ha llegado a la zona del nido, seguir avanzando")

    # Métodos auxiliares para simular la lógica de cada estado
    def check_for_errors(self):
        # Simulación de la verificación de errores
        return False  # No hay errores

    def buscar_zona_objetos(self):
        # Simulación de la detección de objetos
        return True  # Supongamos que encontró objetos

    def buscar_luz_maxima(self):
        # Simulación de la búsqueda de la zona con mayor luz
        return True  # Supongamos que encontró la zona de mayor luz

    def comprobar_llegada_zona_objetos(self):
        # Simulación de la comprobación de la llegada a la zona de objetos
        return True  # Supongamos que llegó a la zona de objetos

    def buscar_zona_nido(self):
        # Simulación de la búsqueda del nido
        return True  # Supongamos que encontró el nido

    def comprobar_llegada_zona_nido(self):
        # Simulación de la comprobación de la llegada a la zona del nido
        return True  # Supongamos que llegó a la zona del nido

