#include "Motor_PID_Class.h"

// Flag to control the serial print
bool print_Info_PID = true;

// Declare the global mutex
SemaphoreHandle_t xMutex;

// Pin definitions
#define PinPot 34

#define EN_1 17
#define IN1_1 23
#define IN2_1 19
#define PinEncoder_1 25

#define EN_2 16
#define IN1_2 18
#define IN2_2 5
#define PinEncoder_2 27

enum motorOptions {
  Motor_Stop = 1,
  Motor_Forward = 2,
  Motor_Reverse = 3
};

// Global Variables
float Kp_Global = 4.8; // Adjust as needed
float Ki_Global = 3.5; // Adjust as needed
float Kd_Global = 0.0000001; // Adjust as needed
float Tm_Global = 0.1;

// Global variables shared between tasks
volatile int contador_1_Global = 0;
volatile int contador_2_Global = 0;
volatile int setPoint_1_Global = 0;
volatile int setPoint_2_Global = 0;
volatile int optionMotor_1_Global = Motor_Stop;
volatile int optionMotor_2_Global = Motor_Stop;

//---------------------------------------------------------------
// Interrupt service routines
//---------------------------------------------------------------
void IRAM_ATTR encoder_1() {
  contador_1_Global++;
}

void IRAM_ATTR encoder_2() {
  contador_2_Global++;
}

//---------------------------------------------------------------
// Motor PID Controller objects
//---------------------------------------------------------------
MotorPIDController motor1_Controller(Kp_Global, Ki_Global, Kd_Global, Tm_Global);
MotorPIDController motor2_Controller(Kp_Global, Ki_Global, Kd_Global, Tm_Global);

//---------------------------------------------------------------
// Task for PID control of Motor 1
//---------------------------------------------------------------
void PID_Motor1_Task(void *pvParameters) {
  // Local variables
  float setPoint = 0;
  int optionMotor = 0;
  int contEncoder = 0;

  for (;;) {
    if (print_Info_PID) Serial.println("PID_Motor1_Task");

    // Get and send data to global variables
    xSemaphoreTake(xMutex, portMAX_DELAY);
    setPoint = setPoint_1_Global;
    optionMotor = optionMotor_1_Global;
    xSemaphoreGive(xMutex);

    // Update the setpoint
    motor1_Controller.updateSetPoint(setPoint);

    // Read the encoder value
    detachInterrupt(digitalPinToInterrupt(PinEncoder_1));
    contEncoder = contador_1_Global;
    contador_1_Global = 0;
    attachInterrupt(digitalPinToInterrupt(PinEncoder_1), encoder_1, RISING);

    // Perform PID calculations
    int outputPWM = motor1_Controller.calculatePID(contEncoder);
    contEncoder = 0;

    // Send PWM to the motor
    switch(optionMotor){
      case Motor_Stop:
        if (!print_Info_PID) Serial.println("Motor 1 - Stop!!");
        motor1_Controller.Stop();
        break;

      case Motor_Forward:
        if (!print_Info_PID) Serial.println("Motor 1 - Forward!!");
        motor1_Controller.Forward(outputPWM);
        break;

      case Motor_Reverse:
        if (!print_Info_PID) Serial.println("Motor 1 - Reverse!!");
        motor1_Controller.Reverse(outputPWM);
        break;

      default:
        if (print_Info_PID) Serial.println("Invalid Option Motor 1!!");
        break;
    }

    if (print_Info_PID) {
    float sp = motor1_Controller.getSetPoint();
    float pv = motor1_Controller.getProcessVariable();
    Serial.print("sp1:");
    Serial.print(sp);
    Serial.print(" | ");
    Serial.print(" pv1:");
    Serial.print(pv);
    Serial.print(" | ");
    Serial.print(" errorPV1:");
    Serial.print(sp - pv);
    Serial.print(" | ");
    Serial.println(" 0:0");
    }

    // Delay to synchronize PID reading
    vTaskDelay(100 / portTICK_PERIOD_MS); // 100ms delay

    // Imprimir el uso de la pila
    //UBaseType_t stackHighWaterMark = uxTaskGetStackHighWaterMark(NULL);
    //Serial.printf("PID_Motor1_Task - Stack High Water Mark for PID_Motor1_Task: %u bytes\n", stackHighWaterMark);
  }
  vTaskDelay(10); // Avoid watchdog warning
}

//---------------------------------------------------------------
// Task for PID control of Motor 2
//---------------------------------------------------------------
void PID_Motor2_Task(void *pvParameters) {
  // Local variables
  float setPoint = 0;
  int optionMotor = 0;
  int contEncoder = 0;

  for (;;) {
    if (print_Info_PID) Serial.println("PID_Motor2_Task");

    // Get and send data to global variables
    xSemaphoreTake(xMutex, portMAX_DELAY);
    setPoint = setPoint_2_Global;
    optionMotor = optionMotor_2_Global;
    xSemaphoreGive(xMutex);

    // Update the setpoint
    motor2_Controller.updateSetPoint(setPoint);

    // Read the encoder value
    detachInterrupt(digitalPinToInterrupt(PinEncoder_2));
    contEncoder = contador_2_Global;
    contador_2_Global = 0;
    attachInterrupt(digitalPinToInterrupt(PinEncoder_2), encoder_2, RISING);

    // Perform PID calculations
    int outputPWM = motor2_Controller.calculatePID(contEncoder);
    contEncoder = 0;

    // Send PWM to the motor
    switch(optionMotor){
      case Motor_Stop:
        if (!print_Info_PID) Serial.println("Motor 2 - Stop!!");
        motor2_Controller.Stop();
      break;

      case Motor_Forward:
        if (!print_Info_PID) Serial.println("Motor 2 - Forward!!");
        motor2_Controller.Forward(outputPWM);
      break;

      case Motor_Reverse:
        if (!print_Info_PID) Serial.println("Motor 2 - Reverse!!");
        motor2_Controller.Reverse(outputPWM);
      break;

      default:
        if (print_Info_PID) Serial.println("Invalid Option Motor 2!!");
      break;
    }

    if (print_Info_PID) {
    float sp = motor2_Controller.getSetPoint();
    float pv = motor2_Controller.getProcessVariable();
    Serial.print("sp2:");
    Serial.print(sp);
    Serial.print(" | ");
    Serial.print(" pv2:");
    Serial.print(pv);
    Serial.print(" | ");
    Serial.print(" errorPV2:");
    Serial.print(sp - pv);
    Serial.print(" | ");
    Serial.println(" 0:0");
    }

    // Delay to synchronize PID reading
    vTaskDelay(100 / portTICK_PERIOD_MS); // 100ms delay

    // Imprimir el uso de la pila
    //UBaseType_t stackHighWaterMark = uxTaskGetStackHighWaterMark(NULL);
    //Serial.printf("PID_Motor2_Task - Stack High Water Mark for PID_Motor1_Task: %u bytes\n", stackHighWaterMark);
  }
  vTaskDelay(10); // Avoid watchdog warning
}

//---------------------------------------------------------------
// Initialization function
//---------------------------------------------------------------
void init_Motors_with_PID() {
  // Motor 1 setup
  motor1_Controller.initPins(EN_1, 11, IN1_1, IN2_1);
  motor1_Controller.Stop();
  pinMode(PinEncoder_1, INPUT);
  attachInterrupt(digitalPinToInterrupt(PinEncoder_1), encoder_1, RISING);

  // Motor 2 setup
  motor2_Controller.initPins(EN_2, 12, IN1_2, IN2_2);
  motor2_Controller.Stop();
  pinMode(PinEncoder_2, INPUT);
  attachInterrupt(digitalPinToInterrupt(PinEncoder_2), encoder_2, RISING);

  // Create the mutex
  xMutex = xSemaphoreCreateMutex();

  // Create the tasks with adjusted priorities
  xTaskCreate(PID_Motor1_Task, "PID_Motor1_Task", 4096, NULL, 10, NULL);
  xTaskCreate(PID_Motor2_Task, "PID_Motor2_Task", 4096, NULL, 10, NULL);
}