class MotorPIDController {
  private:
    float sp;
    float pv;
    float cv;
    float cv1;
    float error;
    float error1;
    float error2;
    float Kp;
    float Ki;
    float Kd;
    float Tm;
    int IN1;
    int IN2;
    int EN;

  public:
    MotorPIDController(float kp, float ki, float kd, float tm)
      : sp(0), pv(0), cv(0), cv1(0), error(0), error1(0), error2(0),
        Kp(kp), Ki(ki), Kd(kd), Tm(tm) , IN1(-1), IN2(-1), EN(-1) {}

    // Métodos getter
    float getSetPoint() const {
      return this->sp;
    }

    float getProcessVariable() const {
      return this->pv;
    }

    // Método para inicializar los pines
    void initPins(int EN_Pin, int pwmChannel, int IN1_Pin, int IN2_Pin) {
      this->EN = EN_Pin;
      this->IN1 = IN1_Pin;
      this->IN2 = IN2_Pin;
      ledcAttachChannel(EN_Pin, 1000, 8, pwmChannel);
      pinMode(IN1_Pin, OUTPUT);
      pinMode(IN2_Pin, OUTPUT);
    }

    void updateSetPoint(float newSp) {
      // Restrict setpoint to the range 0 to 200
      if (newSp < 0) {
          this->sp = 0;
      } else if (newSp > 200) {
          this->sp = 200;
      } else {
          this->sp = newSp;
      }
    }

    int calculatePID(float encoderValue) {
      // Calcular las rpm
      this->pv = calculate_RPM(encoderValue);

      // Calcular el error
      float rawError = this->sp - this->pv;

      // Ecuación de diferencias
      calculate_PID_Differential_Equation(rawError);

      // Salida Motor
      return output();
    }

    void Stop(){
      ledcWrite(this->EN, 0);
      digitalWrite(this->IN1, LOW);
      digitalWrite(this->IN2, LOW);
    }

    void Forward(int pwm){
      ledcWrite(this->EN, pwm);
      digitalWrite(this->IN1, HIGH);
      digitalWrite(this->IN2, LOW);
    }

    void Reverse(int pwm){
      ledcWrite(this->EN, pwm);
      digitalWrite(this->IN1, LOW);
      digitalWrite(this->IN2, HIGH);
    }

  private:
    //Funcion para calcular las RPM que lee el encoder
    float calculate_RPM(float encoderValue) {
      float ppr = 374.0;  // Pulses per revolution
      float factor = 10.0;
      return factor * encoderValue * (60.0 / ppr); // Calcula el valor en RPM
    }

    // Función que calcula la ecuación diferencial del PID
    void calculate_PID_Differential_Equation(float rawError) {
      this->cv = this->cv1 + (this->Kp + this->Kd / this->Tm) * rawError +
                 (-this->Kp + this->Ki * this->Tm - 2 * this->Kd / this->Tm) * this->error1 +
                 (this->Kd / this->Tm) * this->error2;
                 
      this->cv1 = this->cv;
      this->error2 = this->error1;
      this->error1 = rawError;
    }

    // Funcion para saturar y calcular la salida 
    int output(void){
      float valMax_SaturarSalida = 500.0;
      float valMin_SaturarSalida = 30.0;
      float valMax_PWM = 255;

      if (this->cv > valMax_SaturarSalida) {
        this->cv = valMax_SaturarSalida;
      }
      if (this->cv < valMin_SaturarSalida) {
        this->cv = valMin_SaturarSalida;
      }

      return this->cv * (valMax_PWM / valMax_SaturarSalida);
    }
};