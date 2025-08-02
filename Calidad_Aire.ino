#define Voltage_Resolution 5
#define pin A0                  //Pin analogico de arduino
#define type "MQ-135"           //Tipo de sensor
#define ADC_Bit_Resolution 10   // Para arduino UNO/MEGA/NANO
#define RatioMQ135CleanAir 3.6  //RS / R0 = 3.6 ppm  Factor de correccion

MQUnifiedsensor MQ135(placa, Voltage_Resolution, ADC_Bit_Resolution, pin, type);  //Declara el sensor

void setup() {
  Serial.begin(9600);
  MQ135.setRegressionMethod(1);  //Metodo para calcular PPM =  a*ratio^b
  MQ135.setA(110.47);
  MQ135.setB(-2.862);
  MQ135.init();
  //Calibración
  float calcR0 = 0;
  for (int i = 1; i <= 10; i++) {
    MQ135.update();  //  Se actualizan la lectura analogica
    calcR0 += MQ135.calibrate(RatioMQ135CleanAir);
    Serial.print(".");
  }
  MQ135.setR0(calcR0 / 10);
  ////
}

void loop() {
  MQ135.update();  // Se actualizan la lectura analogica
  Serial.print("V= " + String(MQ135.getVoltage()));
  Serial.println("\t PPM= " + String(MQ135.readSensor()+400));
  delay(500);
}
