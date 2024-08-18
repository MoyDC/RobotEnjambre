#include <Wire.h>
#include <ESP32Servo.h>

// I2C Address
#define I2C_SLAVE_ADDRESS 0x08

// Global flags and variables
bool print_Info_I2C = !print_Info_PID;
volatile bool processing = false;
volatile int currentCommandRequest = -1;
volatile int idADC_CommandRequest = -1;

// I2C command macros
enum Command {
  Command_Servomotor = 101,
  Command_ADC = 102,
  Command_Motor_1 = 103,
  Command_Motor_2 = 104,
  Command_RST = 255
};

//---------------------------------------------------------------
// Pin definitions
//---------------------------------------------------------------
// Servomotor pins
const int servoPins[] = {4, 13, 15};
Servo servos[3];

// ADC pins
const int adcPins[] = {36, 39, 34, 35};

//---------------------------------------------------------------
// Utility functions
//---------------------------------------------------------------
int checkPin(int pin, const int array[], int size) {
  for (int i = 0; i < size; i++) {
    if (pin == array[i]) return i;
  }
  return -1;
}

//---------------------------------------------------------------
// Command handlers
//---------------------------------------------------------------
void handleServo(int pin, int value) {
  int id = checkPin(pin, servoPins, sizeof(servoPins) / sizeof(servoPins[0]));
  if (id >= 0 && value >= 0 && value <= 180) {
    servos[id].write(value);
    if (print_Info_I2C) Serial.printf("Pin servomotor '%d' - value: %d\n", servoPins[id], value);
  } else {
    if (print_Info_I2C) Serial.println("Invalid servomotor pin or value");
  }
}

void handleADC(int pin, int value) {
  if (processing) return;  // Skip processing if already handling a request

  processing = true;
  int id = checkPin(pin, adcPins, sizeof(adcPins) / sizeof(adcPins[0]));
  if (id >= 0) {
    currentCommandRequest = Command_ADC;
    idADC_CommandRequest = id;
  } else {
    if (print_Info_I2C) Serial.println("Invalid ADC pin");
    processing = false;
  }
}

bool handleMotor(int option, int value, int numMotor) {
  //int id = checkPin(option, motorOptions, sizeof(motorOptions) / sizeof(motorOptions[0]));
  if (option >= 0 && value >= 0 && value <= 255) {
    if (print_Info_I2C) Serial.printf("Option motor  %d '%d' - value: %d\n", numMotor, option, value);
    return true;
  } else {
    if (print_Info_I2C) Serial.println("Invalid motor option or value");
    Serial.println("Invalid motor option or value");
    return false;
  }
}

//---------------------------------------------------------------
// I2C event handlers
//---------------------------------------------------------------
void receiveEvent(int howMany) {
  if (Wire.available() >= 3) {
    int command = Wire.read();
    int pin = Wire.read();
    int value = Wire.read();

    switch (command) {
      case Command_Servomotor:
        handleServo(pin, value);
        break;

      case Command_ADC:
        handleADC(pin, value);
        break;

      case Command_Motor_1:
        if (handleMotor(pin, value, 1)) {
          // Get and send data to global variables
          xSemaphoreTake(xMutex, portMAX_DELAY);
          setPoint_1_Global = value; 
          optionMotor_1_Global = pin;
          xSemaphoreGive(xMutex);
        }
        break;

      case Command_Motor_2:
        if (handleMotor(pin, value, 2)) {
          // Get and send data to global variables
          xSemaphoreTake(xMutex, portMAX_DELAY);
          setPoint_2_Global = value; 
          optionMotor_2_Global = pin;
          xSemaphoreGive(xMutex);
        }
        break;
            
      case Command_RST:
        ESP.restart();  // Restart the ESP32
        break;

      default:
        if (print_Info_I2C) Serial.println("Receive - Wrong Command!!");
        break;
    }
  }
}

void requestEvent() {
  if (currentCommandRequest == Command_ADC && idADC_CommandRequest >= 0) {
    int data = analogRead(adcPins[idADC_CommandRequest]);
    Wire.write(data & 0xFF);
    Wire.write((data >> 8) & 0xFF);
    Wire.write(adcPins[idADC_CommandRequest]);

    if (print_Info_I2C) Serial.printf("Pin ADC %d - valueADC: %d\n", adcPins[idADC_CommandRequest], data);
  } else {
    if (print_Info_I2C) Serial.println("Request - Wrong Command or ID!!");
  }

  // Reset processing flags
  currentCommandRequest = -1;
  idADC_CommandRequest = -1;
  processing = false;
}

//---------------------------------------------------------------
// Initialization function
//---------------------------------------------------------------
void init_ESP32_Slave_I2C() {
  // Initialize I2C with the slave address
  Wire.begin(I2C_SLAVE_ADDRESS);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);

  // Attach servomotors to the respective pins
  for (int i = 0; i < sizeof(servoPins) / sizeof(servoPins[0]); i++) {
    servos[i].attach(servoPins[i]);
  }
}