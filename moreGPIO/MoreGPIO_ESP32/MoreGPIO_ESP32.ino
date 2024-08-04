#include <Wire.h>
#include <ESP32Servo.h>

#define I2C_SLAVE_ADDRESS 0x08

volatile bool processing = false;
volatile int currentCommandRequest = -1;
volatile int idADC_CommandRequest = -1;

// Macros Receive - I2C
enum Command {
  Command_Output = 100,
  Command_PWM = 101,
  Command_Servomotor = 102,
  Command_ADC = 103,
  Command_RST = 104
};

// Pines Output
const int outputPins[] = {23, 19, 18, 5};

// Pines PWM
const int pwmPins[] = {12, 14, 27, 26, 25, 33, 17, 16};
const int pwmChannels[] = {5, 6, 7, 8, 9, 10, 11, 12};
const int pwmFrequencies[] = {1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000};
const int pwmResolutions[] = {8, 8, 8, 8, 8, 8, 8, 8};

// Pines servomotores
const int servoPins[] = {4, 13, 15};
Servo servos[3];

// Pines ADC
const int adcPins[] = {36, 39, 34, 35};

// Definir el pin donde está conectado el LED
#define LED_PIN 2
unsigned long previousMillis = 0;  // Almacena el tiempo de la última actualización del LED
const long interval = 250;         // Intervalo de tiempo entre cambios de estado del LED (en milisegundos)

void setup() {
  Serial.begin(115200);
  Serial.println("\nInit More GPIO with ESP32 - I2C");
  
  Wire.begin(I2C_SLAVE_ADDRESS);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
  
  for (int pin : outputPins) {
    pinMode(pin, OUTPUT);
  }

  for (int i = 0; i < sizeof(pwmPins)/sizeof(pwmPins[0]); i++) {
    ledcAttachChannel(pwmPins[i], pwmFrequencies[i], pwmResolutions[i], pwmChannels[i]);
  }

  for (int i = 0; i < sizeof(servoPins)/sizeof(servoPins[0]); i++) {
    servos[i].attach(servoPins[i]);
  }

  // Configurar el pin LED como salida
  pinMode(LED_PIN, OUTPUT);

}//End setup

void loop() {

  //*****BLINK*****
  unsigned long currentMillis = millis();  
  if (currentMillis - previousMillis > interval) {  
    previousMillis = currentMillis; 
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));  // Cambiar el estado del LED
  }

}//End loop

void receiveEvent(int howMany) {
  if (Wire.available() >= 3) {
    int command = Wire.read();
    int pin = Wire.read();
    int value = Wire.read();

    switch (command) {
      case Command_Output:
        handleOutput(pin, value);
        break;

      case Command_PWM:
        handlePWM(pin, value);
        break;

      case Command_Servomotor:
        handleServo(pin, value);
        break;

      case Command_ADC:
        handleADC(pin, value);
        break;

      case Command_RST:
        ESP.restart();  // Reinicia la ESP32
        break;

      default:
        Serial.println("Receive - Wrong Command!!");
        break;
    }
  }
}

void handleOutput(int pin, int value) {
  int id = checkPin(pin, outputPins, sizeof(outputPins) / sizeof(outputPins[0]));
  if (id >= 0 && (value == 0 || value == 1)) {
    digitalWrite(outputPins[id], value);
    Serial.printf("Pin output '%d' - value: %s\n", outputPins[id], value ? "HIGH" : "LOW");
  } else {
    Serial.println("Invalid output pin or value");
  }
}

void handlePWM(int pin, int value) {
  int id = checkPin(pin, pwmPins, sizeof(pwmPins) / sizeof(pwmPins[0]));
  if (id >= 0 && value >= 0 && value <= 255) {
    ledcWrite(pwmPins[id], value);
    Serial.printf("Pin PWM '%d' - value: %d\n", pwmPins[id], value);
  } else {
    Serial.println("Invalid PWM pin or value");
  }
}

void handleServo(int pin, int value) {
  int id = checkPin(pin, servoPins, sizeof(servoPins) / sizeof(servoPins[0]));
  if (id >= 0 && value >= 0 && value <= 180) {
    servos[id].write(value);
    Serial.printf("Pin servomotor '%d' - value: %d\n", servoPins[id], value);
  } else {
    Serial.println("Invalid servomotor pin or value");
  }
}

void handleADC(int pin, int value) {
  if (processing) {
    //Serial.println("ESP32 is busy processing another request.");
    return; // Skip processing if already handling a request
  }
  processing = true;

  int id = checkPin(pin, adcPins, sizeof(adcPins) / sizeof(adcPins[0]));
  if (id >= 0) {
    currentCommandRequest = Command_ADC;
    idADC_CommandRequest = id;
    
  } else {
    Serial.println("Invalid ADC pin");
    processing = false;
  }
}

void requestEvent() {
  //unsigned long startTime = micros(); // Start timer
  if (currentCommandRequest == Command_ADC) {
    if(idADC_CommandRequest >= 0){
      int data = analogRead(adcPins[idADC_CommandRequest]);
      //int data = 4095;
      Wire.write(data & 0xFF);
      Wire.write((data >> 8) & 0xFF);
      Wire.write(adcPins[idADC_CommandRequest]);
      Serial.printf("Pin ADC %d - valueADC: %d\n", adcPins[idADC_CommandRequest], data);
    }
    else{
      Serial.println("Request - Wrong Id!!");
    }
  } else {
    Serial.println("Request - Wrong Command!!");
  }

  currentCommandRequest = -1;
  idADC_CommandRequest = -1;
  processing = false; // Release the lock
}

int checkPin(int pin, const int array[], int size) {
  for (int i = 0; i < size; i++) {
    if (pin == array[i]) return i;
  }
  return -1;
}

