#include <Arduino.h>
#include  "Motor.h"
#include  "ESP32_Slave_I2C.h"

//---------------------------------------------------------------
// Task led blink
void BlinkLed_Task(void *pvParameters) {
  int LED_BUILTIN = 2;
  pinMode(LED_BUILTIN, OUTPUT);
  for (;;) {
    // Blink LED en una línea de código
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));

    // Delay para ceder tiempo a otras tareas
    vTaskDelay(250 / portTICK_PERIOD_MS); 

    //UBaseType_t stackHighWaterMark = uxTaskGetStackHighWaterMark(NULL);
    //Serial.printf("BlinkLed_Task - Stack High Water Mark for PID_Motor1_Task: %u bytes\n", stackHighWaterMark);
  }
  vTaskDelay(10); // Evitar advertencia de watchdog
}
//---------------------------------------------------------------

void setup() {
  Serial.begin(115200);

  Serial.println("\nInit More GPIO with ESP32 - I2C");

  Serial.println("init_ESP32_Slave_I2C");
  init_ESP32_Slave_I2C();

  Serial.println("init_Motors_with_PID");
  init_Motors_with_PID();
  
  Serial.println("");
  xTaskCreate(BlinkLed_Task, "BlinkLed_Task", 4096, NULL, 5, NULL);

}

void loop() {
  //Nothing
}

