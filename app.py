import streamlit as st
import google.generativeai as genai

# Configuración de la página
st.set_page_config(page_title="Asistente SBAR - Pediatría", layout="wide")

# Título y encabezado
st.title("🏥 Asistente SBAR - Servicio de Pediatría")
st.caption("Herramienta de apoyo para la estandarización del pase de guardia y detección de pendientes.")

# Barra lateral para configuración
st.sidebar.header("⚙️ Configuración")
api_key = st.sidebar.text_input("Ingresa tu API Key de Gemini:", type="password")

# Prompt del sistema
SYSTEM_PROMPT = """
Eres un asistente experto en Enfermería Pediátrica. Tu función es transformar notas del turno e indicaciones médicas en un borrador de Pase de Guardia en formato SBAR (Situación, Antecedentes, Evaluación, Recomendación).
Reglas:
1. NO inventes datos.
2. Estandariza la terminología a lenguaje técnico de enfermería.
3. REGLA DE ORO: Si detectas una indicación médica o estudio sin reporte cargado, colócalo en la sección [R] encabezado con '⚠️ PENDIENTE:'.
"""

# Selección de camas (12 camas de Pediatría)
camas = [f"Cama {i:02d}" for i in range(1, 13)]
cama_seleccionada = st.selectbox("Selecciona la Cama de Pediatría:", camas)

st.subheader(f"📋 Registro del Turno - {cama_seleccionada}")

# Área de texto para ingresar las notas crudas del turno
texto_turno = st.text_area(
    "Pega o escribe las notas del turno (evolución, signos vitales, indicaciones):",
    height=200,
    placeholder="Ej: Paciente femenina de 12 años... pendiente prueba de tolerancia..."
)

# Botón para procesar con IA
if st.button("✨ Generar Pase SBAR"):
    if not api_key:
        st.error("Por favor, ingresa una API Key de Gemini en la barra lateral para continuar.")
    elif not texto_turno:
        st.warning("Por favor, ingresa el texto del turno para procesar.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner("Procesando información clínica y detectando pendientes..."):
                response = model.generate_content(f"{SYSTEM_PROMPT}\n\nTexto de entrada:\n{texto_turno}")
                
            st.success("¡Pase SBAR generado con éxito!")
            st.markdown("### 📄 Borrador de Pase de Guardia SBAR")
            st.text_area("Resultado (Editable para validación de enfermería):", value=response.text, height=400)
            st.warning("⚠️ Recordatorio de Seguridad: Valide el contenido antes de copiarlo a la Historia Clínica.")
            
        except Exception as e:
            st.error(f"Error al procesar: {e}")
