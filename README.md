# 🚀  Space_NL
Space NL nace como un proyecto ciudadano con el objetivo de diseñar y construir un cohete experimental de bajo costo, accesible y fácil de operar. Su propósito es impulsar la ciencia ciudadana, fomentar el aprendizaje en áreas STEM (ciencia, tecnología, ingeniería y matemáticas) y promover la democratización tecnológica.

# 📡 Sistema de Telemetría de Cohetes

Este proyecto implementa un sistema completo de **telemetría para cohetes experimentales**, compuesto por hardware basado en un **ESP32** y una aplicación de escritorio en **Python (PyQt5)** para la visualización y almacenamiento de datos.

---

## ⚙️ Hardware

El sistema está construido alrededor de un **ESP32**, que se encarga de recolectar información de distintos sensores y transmitirla.

### 🔌 Componentes principales
- **ESP32** – Microcontrolador principal.  
- **GY-91 (IMU: MPU9250 + BMP280)** – Aceleración, giroscopio, magnetómetro y presión/barómetro.  
- **GPS NEO-6M** – Posición y velocidad.  
- **Sensor MQ135** – Calidad de aire (detección de gases).  
- **Sensor DHT22** – Temperatura y humedad.  
- **Módulo LoRa** – Comunicación inalámbrica de largo alcance.  
- **Módulo MicroSD** – Almacenamiento local de datos.  
- **Buzzer** – Señalización acústica.  
- **Servo** – Para sistemas mecánicos auxiliares.  
- **Fuente de alimentación** – TP4056 para carga de batería LiPo y MT3608 como convertidor step-up a 5V.  

🔋 La alimentación se gestiona desde una batería de 3.7V, regulada a **5V y 3.3V** para los distintos módulos.


## Tabla de componentes:

 **Number** | Name                                       | Designator | Footprint                                           | Quantity 
:----------:|:-----------------------------------------------:|:---------------------:|:-------------------------------------------------------------:|:-----------------:
 **1**      | ""BUZZER-12X9""                   | ""BUZZER1""           | ""BUZ-TH_BD12.0-P7.60-D0.6-FD"" | 1                 
 **2**      | ""100nF""                               | ""C1""           | ""RAD-0.1""                                         | 1                 
 **3**      | ""AUIRF3205-VB""                 | ""Q1""           | ""TO-220-3_L10.0-W4.6-P2.54-L"" | 1                 
 **4**      | ""2.7k""                                 | ""R1""           | ""R_AXIAL-0.4""                                 | 1                 
 **5**      | ""10k""                                   | ""R2""           | ""R_AXIAL-0.4""                                 | 1                 
 **6**      | ""1k""                                     | ""R3""           | ""R_AXIAL-0.4""                                 | 1                 
 **7**      | ""Servo-1.27""                     | ""S1""           | ""SERVO-1.27""                                   | 1                 
 **8**      | ""LoRa""                                 | ""U1""           | ""LORA-BREAKOUTBOARD""                   | 1                 
 **9**      | ""GY-91""                               | ""U2""           | ""GY-91""                                             | 1                 
 **10**     | ""GY-NEO6MV2""                     | ""U8""           | ""GY-NEO6MV2""                                   | 1                 
 **11**     | ""MicroSD Card Adapter"" | ""U9""           | ""MICROSD CARD READER""                 | 1                 
 **12**     | ""MT3608""                             | ""U10""         | ""MT3608_V2""                                     | 1                 
 **13**     | ""TP4056 MODULE""               | ""U11""         | ""TP4056""                                           | 1                 
 **14**     | ""ESP32-DEVKITC""               | ""U12""         | ""ESP32 DEVKITC V4 ESP32 WROOM 32D""                          | 1                 
 **15**     | ""MQ135""                               | ""U13""         | ""MQ135""                                             | 1                 
 **16**     | ""DHT22""                               | ""U14""         | ""SENSOR-TH_HAIGU_DHT22""             | 1                 



## Diagramas:

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
