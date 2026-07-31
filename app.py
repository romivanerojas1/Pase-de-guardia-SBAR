import streamlit as st
import google.generativeai as genai

# Configuración de página ancha
st.set_page_config(page_title="Dashboard SBAR - Pediatría", layout="wide")

st.title("🏥 Panel de Control SBAR - Servicio de Pediatría (12 Camas)")
st.caption("Selecciona una cama para procesar el pase de guardia o revisar las alertas del turno.")

# Sidebar para API Key
st.sidebar.header("⚙️ Configuración")
api_key = st.sidebar.text_input("Ingresa tu API Key de Gemini:", type="password")

# Inicializar estado de selección de cama
if 'cama_activa' not in st.session_state:
    st.session_state['cama_activa'] = None

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

# Dibujar la grilla de 12 camas (3 filas x 4 columnas)
st.subheader("📌 Cuadrícula de Camas de la Sala")

cols_per_row = 4
for row in range(3):
    cols = st.columns(cols_per_row)
    for col_idx in range(cols_per_row):
        cama_num = row * cols_per_row + col_idx + 1
        nombre_cama = f"Cama {cama_num:02d}"
        
        with cols[col_idx]:
            # Estilo de tarjeta para cada cama
            with st.container(border=True):
                st.markdown(f"### 🛏️ {nombre_cama}")
                st.caption("Estado: Sin procesar" if st.session_state.get(f'sbar_{nombre_cama}') is None else "🟢 SBAR Listo")
                
                # Botón de interacción para cada cama
                if st.button(f"Seleccionar {nombre_cama}", key=f"btn_{nombre_cama}"):
                    st.session_state['cama_activa'] = nombre_cama

# Mostrar el espacio de trabajo de la cama seleccionada abajo
if st.session_state['cama_activa']:
    cama_actual = st.session_state['cama_activa']
    st.divider()
    st.subheader(f"📝 Edición y Generación SBAR - {cama_actual}")
    
    texto_turno = st.text_area(
        f"Notas del turno para {cama_actual}:",
        height=180,
        placeholder="Pega aquí la evolución, signos vitales e indicaciones médicas..."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        generar = st.button("✨ Generar Pase SBAR", type="primary")
        
    if generar:
        if not api_key:
            st.error("Por favor, ingresa tu API Key en la barra lateral.")
        elif not texto_turno:
            st.warning("Ingresa el texto del turno antes de procesar.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                with st.spinner("Analizando registros y buscando pendientes..."):
                    response = model.generate_content(f"{SYSTEM_PROMPT}\n\nTexto de entrada:\n{texto_turno}")
                    st.session_state[f'sbar_{cama_actual}'] = response.text
                st.rerun()
            except Exception as e:
                st.error(f"Error al conectar con la API: {e}")

    # Mostrar resultado si ya existe
    if st.session_state.get(f'sbar_{cama_actual}'):
        st.markdown(f"#### 📋 Informe SBAR Generado para {cama_actual}")
        st.text_area("Resultado editable para validación de enfermería:", 
                     value=st.session_state[f'sbar_{cama_actual}'], 
                     height=350)
        st.info("💡 Puedes copiar este texto y pegarlo en el registro de la Historia Clínica.")
