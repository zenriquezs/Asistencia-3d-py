import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate
from reportlab.lib import colors
import tempfile
import datetime 

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

def obtener_datos_asistencia(matricula_seleccionada=None):
    historial_ref = db.collection("historial_alumnos")
    documentos = historial_ref.stream()

    registros = []
    for doc in documentos:
        data = doc.to_dict()
        if matricula_seleccionada and data.get("matricula") != matricula_seleccionada:
            continue
        registros.append({
            "matricula": data.get("matricula", ""),
            "nombre": data.get("nombre", ""),
            "carrera": data.get("carrera", ""),
            "instructor": data.get("instructor", ""),
            "fecha": data.get("fecha", ""),
            "hora_entrada": data.get("hora_entrada", ""),
            "hora_salida": data.get("hora_salida", "")
        })
    return registros

def generar_pdf_tabla(datos, nombre_reporte):
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(pdf_file.name, pagesize=letter)

    encabezado = [["Matrícula", "Nombre", "Carrera", "Instructor", "Fecha", "Entrada", "Salida"]]
    filas = [[
        d["matricula"],
        d["nombre"],
        d["carrera"],
        d["instructor"],
        d["fecha"],
        d["hora_entrada"],
        d["hora_salida"]
    ] for d in datos]

    tabla = Table(encabezado + filas, repeatRows=1)
    estilo = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ])
    tabla.setStyle(estilo)

    doc.build([tabla])
    return pdf_file.name

def mostrar_generador_reporte():
    st.title("📄 Generador de Reportes PDF de Asistencias")

    estudiantes_docs = db.collection("historial_alumnos").stream()
    matriculas_unicas = sorted(set(doc.to_dict().get("matricula", "") for doc in estudiantes_docs))

    opcion = st.selectbox("Selecciona un alumno o genera reporte general", ["📋 Reporte General"] + matriculas_unicas)

    if st.button("📥 Generar PDF"):
        if opcion == "📋 Reporte General":
            datos = obtener_datos_asistencia()
            nombre_archivo = "Reporte_General.pdf"
        else:
            datos = obtener_datos_asistencia(opcion)
            nombre_alumno = datos[0]["nombre"] if datos else "Alumno"
            nombre_archivo = f"Reporte_{nombre_alumno.replace(' ', '_')}.pdf"

        if datos:
            pdf_path = generar_pdf_tabla(datos, nombre_archivo)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📄 Descargar Reporte PDF",
                    data=f,
                    file_name=nombre_archivo,
                    mime="application/pdf"
                )
        else:
            st.warning("No se encontraron registros para esa matrícula.")

if __name__ == "__main__":
    mostrar_generador_reporte()
