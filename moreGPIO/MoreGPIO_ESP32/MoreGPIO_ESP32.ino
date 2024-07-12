#include <Wire.h>
#include <ESP32Servo.h>

#define I2C_SLAVE_ADDRESS 0x08

// 
int currentCommandRequest = -1;
int idADC_CommandRequest = -1;

// Macros Receive - I2C
#define _Command_Output_ 100
#define _Command_PWM_ 101
#define _Command_Servomotor_ 102
#define _Command_ADC_ 103

// Pines Output
int outputPins[4] = {5, 17, 16, 4};

// Pines PWM
const int maxChannels = 8;    // Número máximo de canales PWM disponibles en la ESP32
int pwmPins[maxChannels] = {13, 12, 14, 27, 26, 25, 19, 18};  // Inicializar todos los pines como no asignados
int pwmChannels[maxChannels] = {5, 6, 7, 8, 9, 10, 11, 12};  // Inicializar todos los canales como no asignados
int pwmFrequencies[maxChannels] = {5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000};   // Frecuencia del PWM en Hz (por defecto 5000)
int pwmResolutions[maxChannels] = {8, 8, 8, 8, 8, 8, 8, 8};      // Resolución del PWM (por defecto 8 bits)

// Pines servomotores
int servoPins[3] = {0, 2, 15};
Servo servos[3];

// Pines ADC
int adcPins[4] = {36, 39, 34, 35};
int adcValues[4];
int adcValueAux[4];
//-------------------------------------------------------------
int checkPin(int pin, int array[], int tamañoArray, String command) {
  for (int i = 0; i < tamañoArray; i++) {
    if (pin == array[i]) {
      return i;
    }
  }
  Serial.print("Pin '");
  Serial.print(pin);
  Serial.print("' does not exist as ");
  Serial.println(command);
  return -1;
  return -1;
}
//-------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  Serial.println("\nInit More GPIO with ESP32 - I2C");
  Wire.begin(I2C_SLAVE_ADDRESS);  // Iniciar la ESP32 como esclavo con dirección 0x08
  Wire.onReceive(receiveEvent);   // Registrar evento de recepción
  Wire.onRequest(requestEvent);   // Registrar evento de solicitud
  
  // Configuracion pines output
  for (int i = 0; i < sizeof(outputPins) / sizeof(outputPins[0]); i++) {
    pinMode(outputPins[i], OUTPUT);
  }

  // Inicializar los canales PWM
  for (int i = 0; i < maxChannels; i++) {
    ledcAttachChannel(pwmPins[i], pwmFrequencies[i], pwmResolutions[i], pwmChannels[i]);
  }

  // Configurar servomotores
  for (int i = 0; i < sizeof(servos) / sizeof(servos[0]); i++) {
    servos[i].attach(servoPins[i]);
  }
}

void loop() {
  // Hacer otras tareas aquí
}

void receiveEvent(int howMany) {
  if (Wire.available() >= 3) {  // Asegurarse de que hay suficientes bytes disponibles
    int command = Wire.read();   // Leer el comando
    int pin = Wire.read();       // Leer el primer dato (pin)
    int value = Wire.read();     // Leer el segundo dato (valor)
    int id = -1;

    switch (command) {
      case _Command_Output_:
        id = checkPin(pin, outputPins, sizeof(outputPins) / sizeof(outputPins[0]), "output!!");
        if (id >= 0) {
          if((value == 1 || value == 0)){
            //--------------
            digitalWrite(outputPins[id], value);
            //--------------
            Serial.print("Pin output '");
            Serial.print(outputPins[id]);
            Serial.print("' - value: ");
            Serial.println(value ? "HIGH" : "LOW");
          }
          else{
            Serial.print("Value of output, Pin ");
            Serial.print(outputPins[id]);
            Serial.println(", is wrong!!");
          }
        }
        break;

      case _Command_PWM_:
        id = checkPin(pin, pwmPins, sizeof(pwmPins) / sizeof(pwmPins[0]), "PWM!!");
        if (id >= 0) {
          if(value >= 0 && value <= 255){
            //--------------
            ledcWrite(pwmPins[id], value);
            //--------------
            Serial.print("Pin PWM '");
            Serial.print(pwmPins[id]);
            Serial.print("' - value: ");
            Serial.println(value);
          }
          else{
            Serial.print("Value of PWM, Pin ");
            Serial.print(pwmPins[id]);
            Serial.println(", is wrong!!");
          }
        }
        break;

      case _Command_Servomotor_:
        id = checkPin(pin, servoPins, sizeof(servoPins) / sizeof(servoPins[0]), "servomotor!!");
        if (id >= 0) {
          if(value >= 0 && value <= 180){
            //--------------
            servos[id].write(value);
            //--------------
            Serial.print("Pin servomotor '");
            Serial.print(servoPins[id]);
            Serial.print("' - value: ");
            Serial.println(value);
          }
          else{
            Serial.print("Value of servomotor, Pin ");
            Serial.print(outputPins[id]);
            Serial.println(", is wrong!!");
          }
        }
        break;

      case _Command_ADC_:
        id = checkPin(pin, adcPins, sizeof(adcPins) / sizeof(adcPins[0]), "ADC!!");
        if (id >= 0) {
          currentCommandRequest = _Command_ADC_;
          idADC_CommandRequest = id;
          adcValueAux[idADC_CommandRequest] = value;
        }
        break;

      default:
        Serial.println("Receive - Wrong Command!!");
        break;
    }
  }
}//End void receiveEvent(int howMany)

void requestEvent() {
  int Data = 0;

  switch(currentCommandRequest){
    case _Command_ADC_:
      //--------------
      //adcValues[idADC_CommandRequest] = ;
      Data = analogRead(adcPins[idADC_CommandRequest]);
      //adcValues[idADC_CommandRequest]
      //--------------
      Serial.print("Pin ADC ");
      Serial.print(adcPins[idADC_CommandRequest]);
      Serial.print(" - valueADC: ");
      Serial.print(Data);
      Serial.print(" - valueRaspberry: ");
      Serial.println(adcValueAux[idADC_CommandRequest]);

      //Serial.println("Enviando Datos");
      //Enviar Datos
      Wire.write(Data & 0xFF);       // Enviar byte bajo
      Wire.write((Data >> 8) & 0xFF); // Enviar byte alto
      Wire.write(adcPins[idADC_CommandRequest]); // Enviar byte bajo
      //Serial.println("Enviandos");
      break;
      
    default:
      Serial.println("Request - Wrong Command!!");
      break;
  }
  
  //Reiniciar variables
  currentCommandRequest = -1;
  idADC_CommandRequest = -1;

  
  
}
 
