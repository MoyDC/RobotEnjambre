class BehaviorRulesRobot:
    def __init__(self, instance_lidar_sensor, instance_sensors, sensorsNames, instance_readADC, 
                 value_repulsion_radius, value_orientation_radius, value_attraction_radius, value_influence_radius):
        self._lidar_sensor = instance_lidar_sensor
        self._sensors = instance_sensors
        self._sensorsNames = sensorsNames  # Almacenar sensorsNames
        self._readADC = instance_readADC
        self._S1_Data = 0
        self._S2_Data = 0
        self._Lidar_Data = 0
        self._SensorLDR1 = 0
        self._SensorLDR2 = 0
        self._repulsion_radius = value_repulsion_radius
        self._orientation_radius = value_orientation_radius
        self._attraction_radius = value_attraction_radius
        self._influence_radius = value_influence_radius
        # Tabla de comportamientos
        self._behaviors_within_radius = {
            # Front, Left, Right, Back
            (True, False, False, False): "Object_front",                     # Object in front
            (True, True, False, False): "Object_front_and_left",             # Object in front and to the left
            (True, False, True, False): "Object_front_and_right",            # Object in front and to the right
            (True, True, True, False): "Object_front_left_right",            # Object in front, left, and right
            (True, True, True, True): "Object_front_left_right_back",        # Object in front, left, right and back
            (False, True, False, False): "Object_left",                      # Object only to the left
            (False, False, True, False): "Object_right",                     # Object only to the right
            (False, True, True, False): "Object_left_and_right",             # Object to the left and right
            (False, False, False, True): "Object_back",                      # Object behind
            (False, False, False, False): "No_object"                        # No object
        }
        self._behaviors_within_influence_radius = {
            # Front-Left, Front-Right,
            (False, False): "No_object",            # No object
            (True, False): "Object_Front_Left",     # Object in Front and Left
            (False, True): "Object_Front_Right",    # Object in Front and Right
            (True, True): "Object_Front",           # Object in Front
        }

    def _retrieve_data_sensors(self):
        self._S1_Data = self._sensors.get(self._sensorsNames[0]).get_data()[1]
        self._S2_Data = self._sensors.get(self._sensorsNames[1]).get_data()[1]
        self._Lidar_Data = self._lidar_sensor.get_data()[1]
        self._SensorLDR1 = self._readADC.get_dataADC_LDR1()[1]
        self._SensorLDR2 = self._readADC.get_dataADC_LDR2()[1]

    def _detect_obstacle(self, sensor_data, radius):
        return sensor_data < radius
    
    def _is_object_within_radius(self, radius):
        value_sensor_front = self._Lidar_Data
        value_sensor_front_left = self._S2_Data
        value_sensor_front_right = self._S1_Data 
        value_sensor_back = 100

        # Estado de los sensores: True si detecta un obstáculo, False si no
        sensor_states = (
            self._detect_obstacle(value_sensor_front, radius),
            self._detect_obstacle(value_sensor_front_left, radius),
            self._detect_obstacle(value_sensor_front_right, radius),
            self._detect_obstacle(value_sensor_back, radius)
        )

        # Buscar la acción en la tabla de comportamientos
        behavior = self._behaviors_within_radius.get(sensor_states, "No_object")

        # Retornar un tuple: (True/False, comportamiento)
        if behavior == "No_object":
            return False, behavior  # Retorna False y el comportamiento "No_object"
        else:
            return True, behavior   # Retorna True y el comportamiento encontrado
        
    def _is_object_within_influence_radius(self, radius):
        value_sensor_Front_Left = self._SensorLDR1
        value_sensor_Front_Right = self._SensorLDR2

        sensor_states = (
            self._detect_obstacle(value_sensor_Front_Left, radius),
            self._detect_obstacle(value_sensor_Front_Right, radius),
        )

        # Buscar la acción en la tabla de comportamientos
        behavior = self._behaviors_within_influence_radius.get(sensor_states, "No_object")

        # Retornar un tuple: (True/False, comportamiento)
        if behavior == "No_object":
            return False, behavior  # Retorna False y el comportamiento "No_object"
        else:
            return True, behavior   # Retorna True y el comportamiento encontrado
        
    def behavior_rules(self):
        self._retrieve_data_sensors()

        is_object_within_repulsion_radius, action_within_repulsion_radius = self._is_object_within_radius(self._repulsion_radius)
        is_object_within_attraction_radius, action_within_attraction_radius = self._is_object_within_radius(self._attraction_radius)
        is_object_within_influence_radius, action_within_influence_radius = self._is_object_within_radius(self._influence_radius)

        if is_object_within_repulsion_radius:
            action_in = "repulsion_radius"
            action = action_within_repulsion_radius
            return action_in, action
        elif is_object_within_influence_radius:
            action_in = "influence_radius"
            action = action_within_influence_radius
            return action_in, action
        elif is_object_within_attraction_radius:
            action_in = "attraction_radius"
            action = action_within_attraction_radius
            return action_in, action
        else:
            return "No_action_in", "No_object"
        
    