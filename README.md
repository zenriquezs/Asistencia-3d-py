
---

## Arquitectura Técnica

1. **Registro de tarjetas RFID (Arduino):**  
   Se conectan lector y tarjeta para almacenar nombre, matrícula, carrera, semestre desde consola serial.

2. **Lectura de tarjetas (ESP32):**  
   El estudiante escanea su tarjeta. El ESP32 envía la matrícula por MQTT.

3. **Procesamiento (Streamlit):**  
   La app web consulta Firestore, actualiza la asistencia y muestra el resultado en el dashboard.

4. **Almacenamiento en la nube:**  
   - Firestore almacena los datos y registros.  
   - ImageKit guarda las fotografías asociadas a cada matrícula.

5. **Exportación de reportes:**  
   El profesor puede filtrar por alumno o fecha y descargar los registros en PDF.

---

## Flujo del Sistema

1. Registro de estudiantes desde la app web.
2. Personalización de tarjetas RFID mediante Arduino.
3. Escaneo diario con ESP32.
4. Recepción de matrícula por MQTT.
5. Validación, registro y visualización en tiempo real.
6. Generación de reportes desde el dashboard.

---

## Instalación y Ejecución

1. Clona el repositorio:
```bash


git clone https://github.com/zenriquezs/Asistencia-3d-py.git
cd Asistencia-3d-py
