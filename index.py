import streamlit as st
import GenerarReportes
import RegistroEstudiantes
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")  
    firebase_admin.initialize_app(cred)

db = firestore.client()
def verificar_login(usuario, contrasena):
    admin_ref = db.collection("administrador")
    query = admin_ref.where("usuario", "==", usuario).where("password", "==", contrasena).stream()
    for doc in query:
        return True  
    return False  

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False


if not st.session_state.autenticado:
    st.title("🔐 Login de Administrador")
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if verificar_login(usuario, contrasena):
            st.success("Inicio de sesión exitoso.")
            st.session_state.autenticado = True
            st.rerun()  
        else:
            st.error("Credenciales incorrectas. Intenta de nuevo.")
else:

    tab1, tab2 = st.tabs(["📋 Registro de Estudiantes", "📡 Visualización de Datos"])

    with tab1:
        RegistroEstudiantes.mostrar_formulario()

    with tab2:
        GenerarReportes.mostrar_generador_reporte()
