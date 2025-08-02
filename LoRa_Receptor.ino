#include <SPI.h>
#include <LoRa.h>

// Pines del LoRa
#define ss 27
#define rst 14
#define dio0 2

void setup() {
  Serial.begin(115200);
  while (!Serial);
  Serial.println("LoRa Receiver");

  // Configura los pines del LoRa
  LoRa.setPins(ss, rst, dio0);

  // Inicializa LoRa en 433 MHz
  while (!LoRa.begin(433E6)) {
    Serial.println(".");
    delay(500);
  }

  LoRa.setSyncWord(0xF3);  // Debe coincidir con el emisor
  Serial.println("LoRa Inicializado y listo para recibir!");
}

void loop() {
  // Comprueba si llegó un paquete
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    Serial.print("Paquete recibido: ");

    // Leer el contenido
    while (LoRa.available()) {
      String message = LoRa.readString();
      Serial.println(message);
    }

    // También puedes leer RSSI (nivel de señal)
    Serial.print("RSSI: ");
    Serial.println(LoRa.packetRssi());
  }
}
