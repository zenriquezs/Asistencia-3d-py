import paho.mqtt.client as mqtt
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import threading
import time
from datetime import datetime

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

matricula_actual = {"valor": ""}
ultimos_pases = {} 

# MQTT
def on_connect(client, userdata, flags, rc):
    print("✅ Conectado a MQTT")
    client.subscribe("/asistencia/rfid")

def on_message(client, userdata, msg):
    matricula = msg.payload.decode()
    print(f"📩 Matrícula recibida: {matricula}")
    matricula_actual["valor"] = matricula
    st.session_state["forzar_refresco"] = True

def iniciar_cliente():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    #client.connect("192.168.0.101", 1883, 60)
    client.connect("172.20.10.12", 1883, 60)
    client.loop_forever()

if "mqtt_iniciado" not in st.session_state:
    hilo = threading.Thread(target=iniciar_cliente, daemon=True)
    hilo.start()
    st.session_state["mqtt_iniciado"] = True

if "forzar_refresco" not in st.session_state:
    st.session_state["forzar_refresco"] = False

st.set_page_config(page_title="Lector de Asistencia", layout="centered")
st.title("📡 Pase de Asistencia RFID")
placeholder = st.empty()

ultima_matricula = ""

while True:
    if matricula_actual["valor"] and (
        matricula_actual["valor"] != ultima_matricula or st.session_state["forzar_refresco"]
    ):
        st.session_state["forzar_refresco"] = False
        matricula = matricula_actual["valor"]
        ultima_matricula = matricula

        ahora = datetime.now()
        fecha_actual = ahora.strftime("%Y-%m-%d")
        hora_actual = ahora.strftime("%H:%M:%S")
        doc_id = f"{matricula}_{fecha_actual}"
        historial_ref = db.collection("historial_alumnos").document(doc_id)

        est_ref = db.document(f"estudiantes/{matricula}")
        est_doc = est_ref.get()

        if not est_doc.exists:
            with placeholder.container():
                st.error(f"⚠️ Matrícula {matricula} no registrada en Firebase.")
            time.sleep(1)
            continue

        est = est_doc.to_dict()
        nombre = est["nombre"]
        carrera = est["carrera"]
        profesor = est["profesor"]
        foto_url = est["foto_url"]

        historial_doc = historial_ref.get()
        mensaje = ""
        hora_entrada = ""
        hora_salida = ""

        if not historial_doc.exists:
            historial_ref.set({
                "matricula": matricula,
                "nombre": nombre,
                "carrera": carrera,
                "profesor": profesor,
                "foto_url": foto_url,
                "fecha": fecha_actual,
                "hora_entrada": hora_actual,
                "hora_salida": ""
            })
            mensaje = "🟢 Entrada registrada"
            hora_entrada = hora_actual
            hora_salida = "—"
            ultimos_pases[matricula] = "entrada"
        else:
            data = historial_doc.to_dict()
            hora_entrada = data.get("hora_entrada", "—")
            hora_salida = data.get("hora_salida", "—")

            if not hora_salida and ultimos_pases.get(matricula) != "salida":
                historial_ref.update({
                    "hora_salida": hora_actual
                })
                mensaje = "🔁 Salida registrada"
                hora_salida = hora_actual
                ultimos_pases[matricula] = "salida"
            else:
                mensaje = "✅ Ya se registró entrada y salida hoy."

        with placeholder.container():
            st.markdown("""
                    <style>
    .perfil-box {
        background-color: #f9f9f9;
        border-radius: 12px;
        padding: 20px;
        display: flex;
        gap: 40px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        color: black !important;
    }
    .foto-box {
        text-align: center;
    }
    .foto-box img {
        border-radius: 10%;
        object-fit: cover;
        border: 4px solid #4682B4;
    }
    .info-box h2, .info-box p, .foto-box p {
        color: black !important;
    }
    .matricula-box {
        background-color: #333;
        color: white;
        padding: 4px 10px;
        border-radius: 8px;
        display: inline-block;
        font-family: monospace;
    }
    </style>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="perfil-box">
                    <div class="foto-box">
                        <img src="{foto_url}" alt="Foto">
                        <p><strong>{nombre}</strong></p>
                        <p><code>{matricula}</code></p>
                    </div>
                    <div class="info-box">
                        <h2>Datos del Estudiante</h2>
                        <p>🏫 <strong>Carrera:</strong> {carrera}</p>
                        <p>👨‍🏫 <strong>Instructor:</strong> {profesor}</p>
                        <p>📅 <strong>Fecha:</strong> {fecha_actual}</p>
                        <p>🟢 <strong>Hora de entrada:</strong> {hora_entrada}</p>
                        <p>🔴 <strong>Hora de salida:</strong> {hora_salida if hora_salida else '—'}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.info(mensaje)

    time.sleep(1)
