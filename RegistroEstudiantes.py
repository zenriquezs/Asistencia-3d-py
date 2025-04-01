import streamlit as st
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore
from imagekitio import ImageKit
import os
import tempfile
import pandas as pd
st.set_page_config(layout="wide")

def mostrar_formulario():
    imagekit = ImageKit(
        public_key='public_admuwkyUTEm7eXVNJ2wtM+kfu4U=',
        private_key='private_cUrpqm3wZEzWTiho+/Nvh9Pdapk=',
        url_endpoint='https://ik.imagekit.io/nw2nkapkw'
    )

    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_config.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
   

    col1, col2 = st.columns([1.3, 1])

    with col1:
        st.header("📝 Formulario")

        with st.form("registro_estudiante"):
            matricula = st.text_input("📌 Matrícula")
            nombre = st.text_input("👤 Nombre")

            carreras = [
                "Ingeniería en Logística",
                "Ingeniería en Industrias Alimentarias",
                "Ingeniería en Tecnologías de la Información y Comunicaciones",
                "Ingeniería en Sistemas Computacionales",
                "Ingeniería Electromecánica",
                "Ingeniería en Gestión Empresarial",
                "Ingeniería Industrial"
            ]
            carrera = st.selectbox("🏫 Carrera", carreras)

            instructores = [
                "Dra. Thalía Heidi Hernández Omaña",
                "Ing. Giovany Humberto Neri Pérez",
                "Mtro. José Martín Oropeza Méndez",
                "Mtro. Saúl Isaí Soto Ortiz",
                "Ing. María Guadalupe Tolentino Cruz",
                "Mtro. Pedro Jhoan Salazar Pérez",
                "Dr. Francisco Javier Cuadros Romero"
            ]
            profesor = st.selectbox("👨‍🏫 Instructor", instructores)

            imagen = st.file_uploader("📷 Fotografía", type=["jpg", "jpeg", "png"])

            submitted = st.form_submit_button("✅ Registrar Estudiante")

            if submitted:
                if not all([matricula, nombre, carrera, profesor, imagen]):
                    st.error("Todos los campos son obligatorios.")
                else:
                    try:
                        img = Image.open(imagen)
                        img = img.convert("RGB")
                        img = img.resize((134, 171))

                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                            img.save(tmp_file, format="JPEG")
                            tmp_file_path = tmp_file.name

                        file_name = os.path.basename(tmp_file_path)
                        upload = imagekit.upload_file(file=open(tmp_file_path, "rb"), file_name=file_name)
                        foto_url = upload.response_metadata.raw['url']

                        datos = {
                            "matricula": matricula,
                            "nombre": nombre,
                            "carrera": carrera,
                            "profesor": profesor,
                            "foto_url": foto_url
                        }
                        db.document(f"estudiantes/{matricula}").set(datos)

                        st.success("✅ Estudiante registrado correctamente.")
                        st.image(foto_url, width=134)
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"❌ Error al registrar: {e}")

    with col2:
        st.header("👥 Estudiantes Registrados")
        docs = db.collection("estudiantes").stream()

        datos_tabla = []
        matriculas = []

        for doc in docs:
            est = doc.to_dict()
            datos_tabla.append({
                "📷 Foto": f'<img src="{est.get("foto_url", "")}" width="80"/>',
                "📌 Matrícula": est.get("matricula", ""),
                "👤 Nombre": est.get("nombre", ""),
                "🏫 Carrera": est.get("carrera", ""),
                "👨‍🏫 Instructor": est.get("profesor", "")
            })
            matriculas.append(est.get("matricula", ""))

        if datos_tabla:
            df = pd.DataFrame(datos_tabla)
            st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("No hay estudiantes registrados aún.")

        st.markdown("---")
        st.subheader("🗑️ Eliminar Estudiante")

        selected_matricula = st.selectbox("Selecciona una matrícula", matriculas)

        if st.button("Eliminar"):
            db.document(f"estudiantes/{selected_matricula}").delete()
            st.success(f"Estudiante con matrícula {selected_matricula} eliminado correctamente.")
            st.rerun()
