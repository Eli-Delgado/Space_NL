#include <SPI.h>
#include <LoRa.h>

// Pines del LoRa
#define ss 27     // CS
#define rst 14    // RESET
#define dio0 2    // DIO0 (interrupción)

// Contador opcional de paquetes enviados
int counter = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial);
  Serial.println("LoRa Sender (Texto fijo)");

  // Configura pines del LoRa
  LoRa.setPins(ss, rst, dio0);

  // Inicializa LoRa a 433 MHz
  while (!LoRa.begin(433E6)) {
    Serial.println(".");
    delay(500);
  }

  LoRa.setSyncWord(0xF3);  // Sync Word para evitar interferencia
  Serial.println("LoRa Inicializado correctamente!");
}

void loop() {
  // Texto fijo que se enviará
  String message = "Hola desde el ESP32 #" + String(counter);

  Serial.print("Enviando paquete: ");
  Serial.println(message);

  // Enviar paquete LoRa
  LoRa.beginPacket();
  LoRa.print(message);
  LoRa.endPacket();

  counter++;

  delay(1000);  // Esperar 1 segundo entre envíos
}