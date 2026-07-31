import streamlit as st
from google import genai

# Configuración de la página en modo ancho
st.set_page_config(page_title="Dashboard SBAR - Pediatría", layout="wide")

st.title("🏥 Panel SBAR por Camas - Servicio de Pediatría")
st.caption("Haz clic en la solapa de cada cama para pegar la evolución del turno y generar el Pase SBAR.")

# Sidebar para la clave API
st.sidebar.header("⚙️ Configuración")
api_key = st.sidebar.text_input("Ingresa tu API Key de Gemini:", type="password")

SYSTEM_PROMPT = """
Eres un asistente experto en Enfermería Pediátrica. Tu función es transformar registros clínicos heterogéneos, notas del turno e indicaciones médicas en un borrador de Pase de Guardia estandarizado bajo el formato SBAR (Situación, Antecedentes, Evaluación, Recomendación). 

[REGLAS DE SEGURIDAD Y FORMATO]
1. NUNCA inventes, asumas o deduzcas datos clínicos que no estén explícitamente presentes en el texto de entrada.
2. Estandariza la terminología informal o coloquial a lenguaje técnico de enfermería.
3. Si un dato requerido no figura en el texto, indica estrictamente: "No registrado".
4. REGLA DE ORO PARA PENDIENTES: Compara la lista de órdenes/indicaciones médicas con los resultados o reportes disponibles. Si una práctica o estudio solicitado no cuenta con reporte cargado, DEBES colocarlo en la sección [R] encabezado con el símbolo "⚠️ PENDIENTE:".

[ESTRUCTURA DE SALIDA REQUERIDA]

■ [S] SITUACIÓN
- Paciente: [Nombre, Edad, Cama]
- Diagnóstico principal: [Diagnóstico y Días de internación]
- Motivo de ingreso / Situación actual breve: [Resumen en 1 oración]

■ [B] ANTECEDENTES (BACKGROUND)
- Dispositivos / Vías activas: [Vía periférica, sondas, cánulas, etc.]
- Alergias: [Alergias conocidas o "Sin alergias conocidas"]
- Antecedentes relevantes: [Afecciones previas o pautas clave]

■ [A] EVALUACIÓN (ASSESSMENT)
- Signos vitales del turno: [Tendencia de FC, FR, SatO2, TA y registro de temperatura/fiebre]
- Examen físico / Resumen del turno: [Evolución de enfermería resumida en lenguaje técnico]
- Tolerancia alimentaria / Diuresis / Deposiciones: [Estado general]

■ [R] RECOMENDACIONES Y PENDIENTES
- ⚠️ PENDIENTES DEL TURNO: [Lista de estudios, laboratorios o interconsultas sin reporte]
- Pautas de cuidado / Vigilancia para el turno entrante: [Alertas clínicas a vigilar]
"""

# Definir la lista de las 12 camas
camas = [f"Cama {i:02d}" for i in range(1, 13)]

# Crear solapas / pestañas superiores para cada cama
tabs = st.tabs(camas)

# Generar el contenido individual dentro de cada solapa
for i, tab in enumerate(tabs):
    nombre_cama = camas[i]
    
    with tab:
        st.subheader(f"🛏️ Registro y Pase SBAR - {nombre_cama}")
        
        col_input, col_output = st.columns([1, 1])
        
        with col_input:
            st.markdown("**1. Pega o escribe el registro del turno aquí:**")
            texto_turno = st.text_area(
                label=f"Evolución {nombre_cama}",
                height=250,
                placeholder=f"Pega aquí la evolución, constantes e indicaciones para {nombre_cama}...",
                key=f"input_{nombre_cama}"
            )
            
            btn_generar = st.button(f"✨ Generar SBAR {nombre_cama}", key=f"btn_{nombre_cama}", type="primary")
            
            if btn_generar:
                if not api_key:
                    st.error("Por favor, ingresa tu API Key en el menú lateral izquierdo.")
                elif not texto_turno.strip():
                    st.warning("Ingresa el texto del turno antes de procesar.")
                else:
                    try:
                        # Cliente oficial de Google GenAI
                        client = genai.Client(api_key=api_key)
                        
                        with st.spinner("Procesando registro clínico y alertas..."):
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=f"{SYSTEM_PROMPT}\n\nTexto de entrada:\n{texto_turno}"
                            )
                            st.session_state[f'sbar_res_{nombre_cama}'] = response.text
                            st.success("¡Pase SBAR generado!")
                            
                    except Exception as err:
                        st.error(f"Error al conectar con la API de Gemini: {err}")

        with col_output:
            st.markdown("**2. Borrador SBAR Generado (Editable):**")
            resultado_guardado = st.session_state.get(f'sbar_res_{nombre_cama}', "")
            
            st.text_area(
                label=f"Resultado SBAR {nombre_cama}",
                value=resultado_guardado,
                height=280,
                placeholder="El informe estructurado SBAR aparecerá aquí después de presionar 'Generar SBAR'.",
                key=f"output_{nombre_cama}"
            )
            
            if resultado_guardado:
                st.info("💡 Puedes editar o copiar este texto para pegarlo en el registro de la HCD.")
