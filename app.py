# app.py
import io
import json
from datetime import datetime

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from fpdf import FPDF
from PyPDF2 import PdfReader
from docx import Document

# --- IA de OpenAI (modo clásico para compatibilidad) ---
import openai

OPENAI_KEY = st.secrets.get("OPENAI_API_KEY", "")
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

# -------------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Centinela Digital – Integridad académica y científica",
    page_icon="🛡️",
    layout="wide",
)

# -------------------------------------------------------------------
# ESTILOS BÁSICOS
# -------------------------------------------------------------------
st.markdown(
    """
    <style>
    .small-text {font-size: 0.8rem; color: #aaaaaa;}
    .risk-high {color:#ff4b4b; font-weight:bold;}
    .risk-medium {color:#ffb000; font-weight:bold;}
    .risk-low {color:#21c55d; font-weight:bold;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# UTILIDADES DE EXTRACCIÓN DE TEXTO
# -------------------------------------------------------------------
def extract_text_from_pdf(file) -> str:
    try:
        reader = PdfReader(file)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    except Exception as e:
        return f"[Error al leer PDF: {e}]"

def extract_text_from_docx(file) -> str:
    try:
        doc = Document(file)
        paragraphs = [p.text for p in doc.paragraphs]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"[Error al leer DOCX: {e}]"


# -------------------------------------------------------------------
# ANÁLISIS BÁSICO (SIN IA) – RESPALDO
# -------------------------------------------------------------------
def fallback_basic_analysis(text: str, rol: str, tipo: str) -> dict:
    """Análisis mínimo cuando no hay API key o la IA falla."""
    n_chars = len(text)
    n_words = len(text.split())
    red_flags = []
    lower = text.lower()

    if "plagio" in lower or "copy" in lower:
        red_flags.append("Mención explícita a plagio o copia.")
    if "chatgpt" in lower or "inteligencia artificial" in lower:
        red_flags.append("Se menciona uso de IA en el texto.")
    if n_words < 150:
        red_flags.append("Texto muy corto para el tipo de producto declarado.")

    dim_scores = {
        "Metodológica": 40 if "método" in lower or "metodología" in lower else 25,
        "Ética": 50 if "consentimiento" in lower or "ética" in lower else 30,
        "Bibliográfica": 45 if "doi" in lower or "referencias" in lower else 25,
        "Redacción / Coherencia": 55 if n_words > 200 else 30,
        "Uso de IA / Originalidad": 60 if "chatgpt" in lower else 35,
    }

    resumen = (
        "Análisis básico sin IA de OpenAI. Se revisó longitud, presencia de términos "
        "clave y posibles alertas mínimas sobre plagio, ética y uso de IA."
    )

    return {
        "sentimiento_global": "neutral",
        "nivel_riesgo_global": "medio",
        "dimensiones": dim_scores,
        "kpis": {
            "n_palabras": n_words,
            "n_caracteres": n_chars,
            "n_red_flags": len(red_flags),
        },
        "red_flags": red_flags,
        "insights": [
            "Se recomienda complementar el análisis con IA cuando se configure la API key.",
            "Revisar manualmente la coherencia metodológica y la solidez de las referencias.",
        ],
        "recomendaciones": [
            "Ampliar el marco teórico y las referencias actualizadas.",
            "Incluir una sección explícita sobre consideraciones éticas.",
        ],
        "resumen": resumen,
    }


# -------------------------------------------------------------------
# ANÁLISIS CON IA DE OPENAI
# -------------------------------------------------------------------
def analyze_with_openai(text: str, rol: str, tipo: str) -> dict:
    """Llama a OpenAI para un análisis profundo. Devuelve dict estructurado.
    Si algo falla, usa fallback_basic_analysis.
    """

    if not OPENAI_KEY or not text.strip():
        return fallback_basic_analysis(text, rol, tipo)

    system_prompt = (
        "Eres un experto en integridad científica, bioética y análisis de textos "
        "académicos. Analizas trabajos de estudiantes y docentes con mirada crítica "
        "pero formativa. Responde SIEMPRE en español y SOLO con un JSON válido."
    )

    user_prompt = f"""
Texto del trabajo (recortado si es muy largo):
\"\"\"{text[:8000]}\"\"\"  # si es muy largo, se corta a 8000 caracteres

Contexto:
- Rol de quien entrega el trabajo: {rol}
- Tipo de producto: {tipo}

Por favor devuelve SOLO un JSON con la siguiente estructura (sin comentarios):

{{
  "sentimiento_global": "positivo | neutro | negativo",
  "nivel_riesgo_global": "bajo | medio | alto",
  "dimensiones": {{
    "Metodológica": 0-100,
    "Ética": 0-100,
    "Bibliográfica": 0-100,
    "Redacción / Coherencia": 0-100,
    "Uso de IA / Originalidad": 0-100
  }},
  "kpis": {{
    "n_palabras": número,
    "n_parrafos": número,
    "porcentaje_primera_persona": 0-100,
    "porcentaje_citas_aproximado": 0-100
  }},
  "red_flags": [
    "descripción breve de cada alerta o posible mala práctica"
  ],
  "insights": [
    "insight analítico importante 1",
    "insight analítico importante 2"
  ],
  "recomendaciones": [
    "recomendación priorizada 1",
    "recomendación priorizada 2"
  ],
  "resumen": "párrafo corto que resuma la situación del caso"
}}

No incluyas texto fuera del JSON.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw = response["choices"][0]["message"]["content"]
        data = json.loads(raw)
        return data
    except Exception as e:
        # En caso de error: análisis básico
        st.warning(
            f"No se pudo completar el análisis con OpenAI ({e}). "
            "Se usará un análisis básico local."
        )
        return fallback_basic_analysis(text, rol, tipo)


# -------------------------------------------------------------------
# GENERACIÓN DE INFORME PDF
# -------------------------------------------------------------------
def build_pdf_report(case_data: dict, analysis: dict) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Centinela Digital - Informe del caso", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.ln(4)
    pdf.multi_cell(
        0,
        6,
        f"Fecha de análisis: {case_data['fecha']}\n"
        f"Rol: {case_data['rol']}\n"
        f"Tipo de producto: {case_data['tipo_producto']}\n",
    )

    pdf.ln(2)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "1. Resumen general", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, analysis.get("resumen", ""))

    pdf.ln(2)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "2. Indicadores clave (KPIs)", ln=True)
    pdf.set_font("Arial", "", 11)
    for k, v in analysis.get("kpis", {}).items():
        pdf.cell(0, 6, f"- {k}: {v}", ln=True)

    pdf.ln(2)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "3. Matriz de riesgo por dimensiones", ln=True)
    pdf.set_font("Arial", "", 11)
    for dim, score in analysis.get("dimensiones", {}).items():
        pdf.cell(0, 6, f"- {dim}: {score}/100", ln=True)

    pdf.ln(2)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "4. Red flags / Alertas", ln=True)
    pdf.set_font("Arial", "", 11)
    if analysis.get("red_flags"):
        for rf in analysis["red_flags"]:
            pdf.multi_cell(0, 6, f"- {rf}")
    else:
        pdf.multi_cell(0, 6, "- No se identificaron red flags críticas.")

    pdf.ln(2)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "5. Recomendaciones para el comité / tutor", ln=True)
    pdf.set_font("Arial", "", 11)
    for rec in analysis.get("recomendaciones", []):
        pdf.multi_cell(0, 6, f"- {rec}")

    pdf.ln(2)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(
        0,
        5,
        "Generado automáticamente por Centinela Digital – "
        "Modelo de monitoreo de integridad académica y científica.\n"
        "Autor del software: Dr. Anderson Díaz Pérez.",
    )

    return pdf.output(dest="S").encode("latin-1")


# -------------------------------------------------------------------
# GENERACIÓN DE INFORME WORD
# -------------------------------------------------------------------
def build_word_report(case_data: dict, analysis: dict) -> bytes:
    doc = Document()
    doc.add_heading("Centinela Digital - Informe del caso", level=1)

    doc.add_paragraph(f"Fecha de análisis: {case_data['fecha']}")
    doc.add_paragraph(f"Rol: {case_data['rol']}")
    doc.add_paragraph(f"Tipo de producto: {case_data['tipo_producto']}")

    doc.add_heading("1. Resumen general", level=2)
    doc.add_paragraph(analysis.get("resumen", ""))

    doc.add_heading("2. Indicadores clave (KPIs)", level=2)
    for k, v in analysis.get("kpis", {}).items():
        doc.add_paragraph(f"{k}: {v}", style="List Bullet")

    doc.add_heading("3. Matriz de riesgo por dimensiones", level=2)
    for dim, score in analysis.get("dimensiones", {}).items():
        doc.add_paragraph(f"{dim}: {score}/100", style="List Bullet")

    doc.add_heading("4. Red flags / Alertas", level=2)
    if analysis.get("red_flags"):
        for rf in analysis["red_flags"]:
            doc.add_paragraph(rf, style="List Bullet")
    else:
        doc.add_paragraph("No se identificaron red flags críticas.")

    doc.add_heading("5. Recomendaciones", level=2)
    for rec in analysis.get("recomendaciones", []):
        doc.add_paragraph(rec, style="List Bullet")

    doc.add_paragraph(
        "\nGenerado por Centinela Digital – Autor del software: "
        "Dr. Anderson Díaz Pérez.",
        style=None,
    )

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.read()


# -------------------------------------------------------------------
# INICIALIZACIÓN DEL HISTÓRICO EN SESIÓN
# -------------------------------------------------------------------
if "historial" not in st.session_state:
    st.session_state["historial"] = []  # lista de dicts


# -------------------------------------------------------------------
# ENCABEZADO
# -------------------------------------------------------------------
st.title("🛡️ Centinela Digital")
st.subheader("Monitorizando la integridad académica y científica con apoyo de IA")

st.markdown(
    """
    Esta es una versión inicial avanzada del sistema de monitoreo, diseñada para apoyar a 
    profesores, semilleros, comités académicos y comités de ética en la detección preliminar 
    de posibles inconsistencias, desviaciones o riesgos en trabajos académicos y científicos.
    """
)

st.markdown(
    '<p class="small-text">Autor del software y modelo conceptual: '
    '<strong>Dr. Anderson Díaz Pérez</strong>.</p>',
    unsafe_allow_html=True,
)

tab_analisis, tab_dashboard, tab_info = st.tabs(
    ["🔍 Analizar un caso", "📊 Dashboards y Comité de ética", "ℹ️ Estado actual y próximos pasos"]
)

# -------------------------------------------------------------------
# TAB 1 – ANALIZAR UN CASO
# -------------------------------------------------------------------
with tab_analisis:
    st.header("1. Información básica del caso")

    col1, col2 = st.columns(2)

    with col1:
        rol = st.selectbox(
            "Rol de quien entrega el trabajo",
            [
                "estudiante",
                "docente-investigador",
                "semillero de investigación",
                "integrante de comité de ética",
                "otro",
            ],
        )

    with col2:
        tipo_producto = st.selectbox(
            "Tipo de producto",
            [
                "Artículo científico",
                "Ensayo académico",
                "Tesis / Trabajo de grado",
                "Informe técnico",
                "Proyecto de investigación",
                "Otro",
            ],
        )

    st.markdown("---")
    st.header("2. Contenido del trabajo")

    col_texto, col_archivo = st.columns([2, 1])

    with col_texto:
        fragmento = st.text_area(
            "Texto del trabajo (puedes pegar un fragmento relevante)",
            height=220,
            placeholder="Pega aquí un fragmento del trabajo, introducción, resumen o parte crítica…",
        )

    with col_archivo:
        st.markdown("**Carga opcional del archivo completo**")
        uploaded_file = st.file_uploader(
            "Formatos aceptados: PDF / Word (.docx)",
            type=["pdf", "docx"],
        )
        extra_text = ""
        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                extra_text = extract_text_from_pdf(uploaded_file)
            else:
                extra_text = extract_text_from_docx(uploaded_file)

            if extra_text.startswith("[Error"):
                st.error(extra_text)
            else:
                st.success("Archivo cargado correctamente. Se integrará al análisis.")

    texto_para_analizar = (fragmento + "\n\n" + extra_text).strip()

    st.markdown("---")
    st.header("3. Análisis automatizado con IA")

    analizar = st.button("🚀 Analizar caso con Centinela Digital")

    if analizar:
        if not texto_para_analizar:
            st.error("Por favor ingresa un fragmento de texto o carga un archivo para analizar.")
        else:
            with st.spinner("Analizando el caso con IA…"):
                analysis = analyze_with_openai(texto_para_analizar, rol, tipo_producto)

            fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
            case_data = {
                "fecha": fecha,
                "rol": rol,
                "tipo_producto": tipo_producto,
                "texto_longitud": len(texto_para_analizar),
            }

            # Guardar en histórico de la sesión
            st.session_state["historial"].append(
                {
                    "fecha": fecha,
                    "rol": rol,
                    "tipo_producto": tipo_producto,
                    "nivel_riesgo_global": analysis.get("nivel_riesgo_global", ""),
                    **{f"dim_{k}": v for k, v in analysis.get("dimensiones", {}).items()},
                }
            )

            # ---------------- RESULTADOS PRINCIPALES ----------------
            st.subheader("Resultados principales")

            col_a, col_b, col_c = st.columns(3)
            sentimiento = analysis.get("sentimiento_global", "neutral")
            riesgo_global = analysis.get("nivel_riesgo_global", "medio")
            kpis = analysis.get("kpis", {})

            def riesgo_badge(level: str) -> str:
                level = level.lower()
                if level == "alto":
                    cls = "risk-high"
                elif level == "medio":
                    cls = "risk-medium"
                else:
                    cls = "risk-low"
                return f'<span class="{cls}">{level.upper()}</span>'

            col_a.markdown(f"**Sentimiento global:** `{sentimiento}`")
            col_b.markdown(
                f"**Nivel de riesgo global:** {riesgo_badge(riesgo_global)}",
                unsafe_allow_html=True,
            )
            col_c.markdown(f"**Palabras aproximadas:** `{kpis.get('n_palabras', '---')}`")

            st.markdown("### Matriz de riesgo por dimensiones")
            dim_df = pd.DataFrame(
                [
                    {"Dimensión": d, "Riesgo": v}
                    for d, v in analysis.get("dimensiones", {}).items()
                ]
            )

            if not dim_df.empty:
                try:
                    chart = (
                        alt.Chart(dim_df)
                        .mark_bar()
                        .encode(
                            x=alt.X("Riesgo:Q", scale=alt.Scale(domain=[0, 100])),
                            y=alt.Y("Dimensión:N", sort="-x"),
                            tooltip=["Dimensión", "Riesgo"],
                        )
                        .properties(height=220)
                    )
                    st.altair_chart(chart, use_container_width=True)
                except Exception as e:
                    st.warning(f"No se pudo renderizar el gráfico de riesgo: {e}")
                    st.dataframe(dim_df)
            else:
                st.info("No se encontraron datos de dimensiones de riesgo.")

            # ---------------- RED FLAGS E INSIGHTS ----------------
            st.markdown("### Red flags / Alertas detectadas")
            red_flags = analysis.get("red_flags", [])
            if red_flags:
                for rf in red_flags:
                    st.markdown(f"- ⚠️ {rf}")
            else:
                st.markdown("- ✅ No se identificaron red flags críticas.")

            st.markdown("### Principales insights analíticos")
            for ins in analysis.get("insights", []):
                st.markdown(f"- 💡 {ins}")

            st.markdown("### Recomendaciones para mitigar riesgos")
            for rec in analysis.get("recomendaciones", []):
                st.markdown(f"- 🩺 {rec}")

            st.markdown("### Resumen narrativo del caso")
            st.write(analysis.get("resumen", ""))

            # ---------------- DESCARGA DE INFORMES ----------------
            st.markdown("---")
            st.subheader("4. Informes automáticos para comité / tutor")

            pdf_bytes = build_pdf_report(case_data, analysis)
            docx_bytes = build_word_report(case_data, analysis)

            col_pdf, col_docx = st.columns(2)
            col_pdf.download_button(
                label="📄 Descargar informe en PDF",
                data=pdf_bytes,
                file_name="informe_centinela_digital.pdf",
                mime="application/pdf",
            )
            col_docx.download_button(
                label="📝 Descargar informe en Word",
                data=docx_bytes,
                file_name="informe_centinela_digital.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

# -------------------------------------------------------------------
# TAB 2 – DASHBOARDS Y COMITÉ DE ÉTICA
# -------------------------------------------------------------------
with tab_dashboard:
    st.header("Panel de control para comités de ética y programas académicos")

    historial = st.session_state.get("historial", [])
    if not historial:
        st.info(
            "Aún no hay casos analizados en esta sesión. "
            "Vuelve a la pestaña *Analizar un caso* y genera al menos un análisis."
        )
    else:
        df = pd.DataFrame(historial)

        st.subheader("Resumen general de casos analizados (solo esta sesión)")
        st.dataframe(df)

        col1, col2 = st.columns(2)

        # Distribución por tipo de producto
        with col1:
            st.markdown("**Casos por tipo de producto**")
            tipo_counts = df["tipo_producto"].value_counts().reset_index()
            tipo_counts.columns = ["Tipo de producto", "Casos"]
            chart_tipo = (
                alt.Chart(tipo_counts)
                .mark_bar()
                .encode(
                    x="Casos:Q",
                    y="Tipo de producto:N",
                    tooltip=["Tipo de producto", "Casos"],
                )
                .properties(height=220)
            )
            st.altair_chart(chart_tipo, use_container_width=True)

        # Distribución por nivel de riesgo
        with col2:
            st.markdown("**Casos por nivel de riesgo global**")
            riesgo_counts = df["nivel_riesgo_global"].value_counts().reset_index()
            riesgo_counts.columns = ["Nivel de riesgo", "Casos"]
            chart_riesgo = (
                alt.Chart(riesgo_counts)
                .mark_bar()
                .encode(
                    x="Casos:Q",
                    y="Nivel de riesgo:N",
                    tooltip=["Nivel de riesgo", "Casos"],
                )
                .properties(height=220)
            )
            st.altair_chart(chart_riesgo, use_container_width=True)

        st.markdown("### Matriz promedio de riesgo por dimensión")
        dim_cols = [c for c in df.columns if c.startswith("dim_")]
        if dim_cols:
            dim_avg = (
                df[dim_cols]
                .mean(numeric_only=True)
                .reset_index()
                .rename(columns={"index": "Dimensión", 0: "Riesgo promedio"})
            )
            dim_avg["Dimensión"] = dim_avg["Dimensión"].str.replace("dim_", "")
            chart_dim_avg = (
                alt.Chart(dim_avg)
                .mark_bar()
                .encode(
                    x=alt.X("Riesgo promedio:Q", scale=alt.Scale(domain=[0, 100])),
                    y="Dimensión:N",
                    tooltip=["Dimensión", "Riesgo promedio"],
                )
                .properties(height=220)
            )
            st.altair_chart(chart_dim_avg, use_container_width=True)
        else:
            st.info("Aún no hay información de dimensiones de riesgo en el histórico.")

        st.markdown(
            """
            Esta vista puede servir como **panel del comité de ética** o del **programa académico** 
            para identificar patrones de riesgo en semilleros, cursos o líneas de investigación 
            (por ejemplo, muchos casos con riesgo ético alto en cierto tipo de trabajo).
            """
        )

# -------------------------------------------------------------------
# TAB 3 – INFORMACIÓN Y PRÓXIMOS PASOS
# -------------------------------------------------------------------
with tab_info:
    st.header("Estado actual y próximos pasos del modelo Centinela Digital")

    st.markdown(
        """
        **Estado actual (versión web estable):**
        - Registro del rol y tipo de producto.
        - Carga directa de archivos PDF / Word.
        - Análisis automatizado con IA (o análisis básico si no hay API key).
        - Matriz de riesgo por dimensiones metodológica, ética, bibliográfica, redacción y uso de IA.
        - Detección de *red flags* y recomendaciones.
        - Generación automática de informes en PDF y Word.
        - Panel de control con resúmenes para comités de ética y programas académicos.

        **Próximos módulos posibles:**
        - Persistencia de históricos en base de datos institucional (semilleros, cohortes, líneas).
        - Integración con plataformas institucionales (Moodle, Teams, LMS propios).
        - Módulo avanzado de verificación de referencias (Crossref / PubMed).
        - Scoring específico para convocatorias de investigación y evaluación de proyectos.
        """
    )

    st.markdown(
        """
        <p class="small-text">
        Este software fue conceptualizado y desarrollado como prototipo por 
        <strong>Dr. Anderson Díaz Pérez</strong>, integrando principios de bioética, 
        integridad científica e inteligencia artificial aplicada a la vigilancia académica.
        </p>
        """,
        unsafe_allow_html=True,
    )
