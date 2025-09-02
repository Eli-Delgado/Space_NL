# 🚀  Space_NL
Space NL nace como un proyecto ciudadano con el objetivo de diseñar y construir un cohete experimental de bajo costo, accesible y fácil de operar. Su propósito es impulsar la ciencia ciudadana, fomentar el aprendizaje en áreas STEM (ciencia, tecnología, ingeniería y matemáticas) y promover la democratización tecnológica.

# 📡 Sistema de Telemetría de Cohetes

Este proyecto implementa un sistema completo de **telemetría para cohetes experimentales**, compuesto por hardware basado en un **ESP32** y una aplicación de escritorio en **Python (PyQt5)** para la visualización y almacenamiento de datos.

---

## ⚙️ Hardware

El sistema está construido alrededor de un **ESP32**, que se encarga de recolectar información de distintos sensores y transmitirla.

## 🔩 Tabla de componentes:

| **#** | **Nombre**                | **Designador** | **Función / Descripción**                                                                 | **Footprint**                                      | **Cantidad** |
|:-----:|---------------------------|:--------------:|-------------------------------------------------------------------------------------------|---------------------------------------------------|:------------:|
| 1     | Buzzer-12x9               | BUZZER1        | Señalización acústica                                                                     | BUZ-TH_BD12.0-P7.60-D0.6-FD                       | 1            |
| 2     | 100nF                     | C1             | Condensador de desacoplo                                                                  | RAD-0.1                                           | 1            |
| 3     | AUIRF3205-VB              | Q1             | MOSFET de potencia                                                                        | TO-220-3_L10.0-W4.6-P2.54-L                       | 1            |
| 4     | Resistencia 2.7k          | R1             | Divisor de voltaje para medición de batería                                               | R_AXIAL-0.4                                       | 1            |
| 5     | Resistencia 10k           | R2             | Divisor de voltaje para medición de batería                                               | R_AXIAL-0.4                                       | 1            |
| 6     | Resistencia 1k            | R3             | Limitación de corriente para buzzer                                                       | R_AXIAL-0.4                                       | 1            |
| 7     | Servo-1.27                | S1             | Accionamiento mecánico auxiliar                                                           | SERVO-1.27                                        | 1            |
| 8     | Módulo LoRa               | U1             | Comunicación inalámbrica de largo alcance                                                 | LORA-BREAKOUTBOARD                                | 1            |
| 9     | GY-91 (IMU: MPU9250+BMP280)| U2             | Aceleración, giroscopio, magnetómetro y presión/barómetro                                 | GY-91                                             | 1            |
| 10    | GPS NEO-6M                | U8             | Posición y velocidad                                                                      | GY-NEO6MV2                                        | 1            |
| 11    | MicroSD Card Adapter      | U9             | Almacenamiento local de datos                                                             | MICROSD CARD READER                               | 1            |
| 12    | MT3608                    | U10            | Convertidor step-up a 5V                                                                  | MT3608_V2                                         | 1            |
| 13    | TP4056 Module             | U11            | Cargador de batería LiPo                                                                  | TP4056                                            | 1            |
| 14    | ESP32-DEVKITC             | U12            | Microcontrolador principal                                                                | ESP32 DEVKITC V4 ESP32 WROOM 32D                  | 1            |
| 15    | MQ135                     | U13            | Sensor de calidad de aire                                                                 | MQ135                                             | 1            |
| 16    | DHT22                     | U14            | Sensor de temperatura y humedad                                                           | SENSOR-TH_HAIGU_DHT22                             | 1            |


## 🖇️ Diagramas:

### 📷 **Esquemático**:

![Esquematico](./imagenes/Esquematico.svg)

### 📷 **2D**:

![2D](./imagenes/2D.svg)


---

## 🖥️ Software (Arquitectura)

El software de telemetría está diseñado en **Python con PyQt5** y organiza el flujo de datos en varias capas:

### 1. **Capa de Hardware**
- Los sensores (IMU, GPS, MQ135, DHT22) envían datos al **ESP32**, que los empaqueta en formato **JSON/CSV**.

### 2. **Comunicación Serial**
- Un hilo dedicado (**SerialReader Thread**) recibe los datos en tiempo real.  
- El **Data Parser** interpreta la información y la envía al resto de la aplicación mediante señales de Qt.

### 3. **Interfaz Gráfica (MainGUI)**
- Panel de control: selección de puerto, configuración de baudios, estado de conexión.  
- Visualización de datos en tiempo real:  
  - Gráfica de calidad de aire (MQ135).  
  - Gráfica de temperatura y humedad (DHT22).  
  - Posición GPS.  
  - Lecturas del IMU.

### 4. **Gestión de Datos**
- **CSV Writer**: almacenamiento automático en archivos con marca de tiempo.  
- **Circular Buffer** y **Plot Timer**: manejo eficiente de los datos en vivo.

### 5. **Almacenamiento**
Los datos se guardan en archivos **CSV** con el formato:
- esp32_data_YYYYMMDD_HHMMSS.csv

## 📷 **Arquitectura de software**:
![Arquitectura](./imagenes/arquitectura.jpg)

## 📷 **Interfaz**:
![Interfaz](./imagenes/interfaz.jpg)
