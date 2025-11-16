import io
import json
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st
from fpdf import FPDF
from openai import OpenAI

# ============================================================
# CONFIGURACIÓN OPENAI
# ============================================================
try:
    # Usa la variable de entorno OPENAI_API_KEY (en Streamlit Cloud: st.secrets)
    client = OpenAI()
    OPENAI_OK = True
except Exception:
    client = None
    OPENAI_OK = False

# ============================================================
# CONSTANTES Y HELPERS
# ============================================================
PRODUCT_OPTIONS = [
    "Ensayo",
    "Artículo científico",
    "Tesis",
    "Informe técnico",
    "Trabajo de curso",
    "Proyecto de grado",
    "Otro",
]


def yn(label: str, key: str) -> int:
    """Radio Sí/No que devuelve 1 o 0."""
    choice = st.radio(label, ["No", "Sí"], index=0, horizontal=True, key=key)
    return 1 if choice == "Sí" else 0


# ---------- extracción de texto de archivos -----------------
def extract_text_from_file(uploaded_file) -> str:
    """Extrae texto desde PDF / DOCX / TXT."""
    if uploaded_file is None:
        return ""
    import os

    suffix = os.path.splitext(uploaded_file.name)[1].lower()

    if suffix == ".txt":
        return uploaded_file.read().decode("utf-8", errors="ignore")

    if suffix in [".docx", ".doc"]:
        from docx import Document

        doc = Document(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs)

    if suffix == ".pdf":
        import PyPDF2

        reader = PyPDF2.PdfReader(uploaded_file)
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)

    return ""


# ---------- matriz de riesgo -------------------------------
def build_risk_matrix(evidencias: dict) -> pd.DataFrame:
    """Construye matriz de riesgo por dimensiones a partir de las evidencias."""
    dims = {
        "Autoría / estilo": evidencias["estilo_diferente"] + evidencias["defensa_debil"],
        "Tiempo y forma de entrega": evidencias["tiempo_sospechoso"] + evidencias["sin_borradores"],
        "Referencias y datos": evidencias["referencias_raras"] + evidencias["datos_inconsistentes"],
        "Imágenes / figuras": evidencias["imagenes_sospechosas"],
    }
    rows = []
    for dim, score in dims.items():
        nivel = "Bajo"
        if score >= 3:
            nivel = "Alto"
        elif score == 2:
            nivel = "Medio"
        rows.append({"dimension": dim, "riesgo": score, "nivel": nivel})
    return pd.DataFrame(rows)


def risk_score_from_matrix(df: pd.DataFrame) -> int:
    max_score = 3 * len(df)
    raw = df["riesgo"].sum()
    if max_score == 0:
        return 0
    return int(100 * raw / max_score)


def overall_level(score: int) -> str:
    if score >= 70:
        return "ALTO"
    if score >= 40:
        return "MEDIO"
    if score > 0:
        return "BAJO"
    return "SIN ALERTAS"


# ============================================================
# UTILIDADES PARA PDF (evitar errores de FPDF)
# ============================================================
def _break_long_words(text: str, max_len: int = 60) -> str:
    """
    Evita el error 'Not enough horizontal space...' partiendo palabras muy largas
    (por ejemplo, URLs) en trozos manejables.
    """
    words = text.split(" ")
    pieces = []

    for w in words:
        if len(w) <= max_len:
            pieces.append(w)
        else:
            for i in range(0, len(w), max_len):
                pieces.append(w[i : i + max_len])

    return " ".join(pieces)


def safe_pdf_text(text: str) -> str:
    """
    1) Sustituye caracteres Unicode problemáticos.
    2) Rompe palabras larguísimas.
    3) Fuerza compatibilidad latin-1 (FPDF clásico).
    """
    if not text:
        return ""

    replacements = {
        "–": "-",
        "—": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "•": "-",
        "º": "o",
        "ª": "a",
        "→": "->",
        "°": " grados",
        "\u00a0": " ",  # espacio no separable
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = _break_long_words(text, max_len=60)
    text = text.encode("latin-1", "replace").decode("latin-1")
    return text


def build_pdf_report(case_data: dict, analysis: dict) -> bytes:
    """
    Genera un informe PDF corto para comité / tutor.
    Usa safe_pdf_text() para evitar problemas de Unicode y palabras largas.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # -------- Encabezado ----------
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, safe_pdf_text("Centinela Digital – Informe para comité / tutor"), ln=1)

    pdf.set_font("Helvetica", "", 10)
    autor_software = (
        "Software desarrollado por Prof. Anderson Díaz Pérez "
        "(Doctor en Bioética y Salud Pública, especialista en IA)."
    )
    pdf.multi_cell(0, 5, safe_pdf_text(autor_software))
    pdf.ln(4)

    # -------- Datos básicos del caso ----------
    rol = case_data.get("rol", "No especificado")
    tipo_producto = case_data.get("tipo_producto", "No especificado")
    archivo = case_data.get("file_name") or "Texto pegado"

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, safe_pdf_text("1. Información básica del caso"), ln=1)

    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, safe_pdf_text(f"Rol de quien entrega el trabajo: {rol}"))
    pdf.multi_cell(0, 5, safe_pdf_text(f"Tipo de producto: {tipo_producto}"))
    pdf.multi_cell(0, 5, safe_pdf_text(f"Fuente del texto analizado: {archivo}"))
    pdf.ln(3)

    # -------- Resultado global de riesgo ----------
    riesgo_global = analysis.get("riesgo_global", 0)
    nivel_global = analysis.get("nivel_global", "NO DISPONIBLE")
    sentimiento = analysis.get("sentimiento", "neutro")
    num_evidencias = analysis.get("num_evidencias", 0)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, safe_pdf_text("2. Resultado global de la evaluación"), ln=1)

    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, safe_pdf_text(f"Riesgo global (0–100): {riesgo_global}"))
    pdf.multi_cell(0, 5, safe_pdf_text(f"Nivel de riesgo global: {nivel_global.upper()}"))
    pdf.multi_cell(0, 5, safe_pdf_text(f"Sentimiento estimado del texto (IA): {sentimiento}"))
    pdf.multi_cell(
        0,
        5,
        safe_pdf_text(f"Número de evidencias marcadas en el primer filtro: {num_evidencias}"),
    )
    pdf.ln(3)

    # -------- Red flags ----------
    red_flags = analysis.get("red_flags", []) or []

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, safe_pdf_text("3. Principales red flags (alertas)"), ln=1)

    pdf.set_font("Helvetica", "", 10)
    if red_flags:
        for rf in red_flags:
            pdf.multi_cell(0, 5, safe_pdf_text(f"- {rf}"))
    else:
        pdf.multi_cell(0, 5, safe_pdf_text("- No se identificaron red flags relevantes."))
    pdf.ln(3)

    # -------- Acciones de mitigación ----------
    acciones = analysis.get("acciones", []) or []

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, safe_pdf_text("4. Acciones sugeridas / mitigación"), ln=1)

    pdf.set_font("Helvetica", "", 10)
    if acciones:
        for ac in acciones:
            pdf.multi_cell(0, 5, safe_pdf_text(f"- {ac}"))
    else:
        pdf.multi_cell(0, 5, safe_pdf_text("- A la fecha, no se sugieren acciones específicas."))
    pdf.ln(3)

    # -------- KPIs / insights clave ----------
    kpis = analysis.get("kpis", []) or []
    insights = analysis.get("insights", []) or []

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, safe_pdf_text("5. KPIs e insights para seguimiento"), ln=1)

    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 5, safe_pdf_text("KPIs sugeridos:"))
    pdf.set_font("Helvetica", "", 10)
    for k in kpis:
        pdf.multi_cell(0, 5, safe_pdf_text(f"- {k}"))

    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 5, safe_pdf_text("Insights clave del caso:"))
    pdf.set_font("Helvetica", "", 10)
    for ins in insights:
        pdf.multi_cell(0, 5, safe_pdf_text(f"- {ins}"))
    pdf.ln(3)

    # -------- Síntesis narrativa (IA) ----------
    narrativa = analysis.get("narrativa", "")

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, safe_pdf_text("6. Síntesis narrativa del caso (IA)"), ln=1)

    pdf.set_font("Helvetica", "", 10)
    if narrativa:
        pdf.multi_cell(0, 5, safe_pdf_text(narrativa))
    else:
        pdf.multi_cell(
            0,
            5,
            safe_pdf_text(
                "La síntesis narrativa automática no está disponible para este caso "
                "(texto muy corto o IA no configurada)."
            ),
        )

    # Devolver bytes del PDF
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return pdf_bytes


# ============================================================
# LLAMADA A GPT PARA ANÁLISIS AVANZADO
# ============================================================
def call_gpt_analysis(texto: str, rol: str, tipo_producto: str, evidencias: dict) -> dict:
    """Llama a OpenAI (ChatGPT) para análisis avanzado del caso."""
    if not OPENAI_OK:
        return {
            "sentiment_label": "desconocido",
            "sentiment_score": 0,
            "overall_risk_level": "desconocido",
            "overall_risk_score": 0,
            "gpt_red_flags": [],
            "mitigation_actions": [],
            "kpis": [],
            "insights": [],
            "short_narrative": (
                "No se pudo llamar a la API de OpenAI. "
                "Revisa la configuración de la clave en Streamlit Cloud (st.secrets)."
            ),
        }

    snippet = texto[:4000]  # recorte de seguridad
    evid_str = json.dumps(evidencias, ensure_ascii=False)

    system_prompt = (
        "Eres un experto en integridad académica, bioética de la investigación y análisis "
        "de textos científicos en lengua española. Evalúas posible uso inadecuado de IA, "
        "plagio, problemas metodológicos y calidad del razonamiento."
    )

    user_prompt = f"""
Rol declarado de quien entrega el trabajo: {rol}
Tipo de producto académico: {tipo_producto}
Evidencias binarias marcadas por el revisor (1 = Sí, 0 = No):
{evid_str}

Texto / fragmento a analizar (recortado a máximo 4000 caracteres):
\"\"\"{snippet}\"\"\"


Tarea:
1. Evalúa el SENTIMIENTO general del texto (positivo, neutro o negativo) y asigna un puntaje entre -1 y 1.
2. Evalúa el riesgo de USO INDEBIDO DE IA y de PROBLEMAS DE INTEGRIDAD (bajo, medio, alto).
3. Identifica las 5-8 principales RED FLAGS (alertas) específicas.
4. Propón 5-8 ACCIONES DE MITIGACIÓN realistas para el docente, tutor o comité.
5. Sugiere 4-6 KPIs para hacer seguimiento a la integridad académica y científica.
6. Extrae 4-6 INSIGHTS clave que sirvan como resumen ejecutivo para un comité de ética o coordinación de programa.
7. Redacta un párrafo narrativo breve que explique el caso de forma clara y profesional.

Devuelve EXCLUSIVAMENTE un JSON válido con esta estructura:

{{
  "sentiment_label": "positivo|neutro|negativo",
  "sentiment_score": 0.0,
  "overall_risk_level": "bajo|medio|alto",
  "overall_risk_score": 0,
  "gpt_red_flags": ["..."],
  "mitigation_actions": ["..."],
  "kpis": ["..."],
  "insights": ["..."],
  "short_narrative": "..."
}}
"""

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    content = completion.choices[0].message.content

    try:
        data = json.loads(content)
    except Exception:
        # Por si el modelo devuelve texto no JSON
        data = {
            "sentiment_label": "desconocido",
            "sentiment_score": 0,
            "overall_risk_level": "desconocido",
            "overall_risk_score": 0,
            "gpt_red_flags": [],
            "mitigation_actions": [],
            "kpis": [],
            "insights": [],
            "short_narrative": content,
        }
    return data


# ============================================================
# CONFIG GENERAL DE STREAMLIT
# ============================================================
st.set_page_config(
    page_title="Centinela Digital – Integridad académica con IA"
    page_icon="🛡️",
    layout="wide",
)

if "historial" not in st.session_state:
    st.session_state["historial"] = []

st.sidebar.title("🛡️ Centinela Digital")
st.sidebar.markdown(
    """
**Monitor de integridad académica y científica con apoyo de IA.** **Corporación Universitaria Iberoamericana [IBERO]**

Software desarrollado por **Prof. Anderson Díaz Pérez**  
(Doctor en Bioética, Doctor en Salud Pública, Magister en Ciencias Básicas Biomédicas, Especialista en IA).

Versión web inicial, orientada a:
- Docentes y tutores.
- Semilleros de investigación.
- Comités de ética y programas académicos.
"""
)

if not OPENAI_OK:
    st.sidebar.warning(
        "No se detectó la configuración de la API de OpenAI. "
        "Configura tu clave en `OPENAI_API_KEY` o en `st.secrets`."
    )

tabs = st.tabs(
    [
        "🔍 Analizar un caso",
        "📊 Estado actual y próximos pasos",
        "🏛️ Panel para comités y programas",
    ]
)

# ============================================================
# TAB 1 – ANALIZAR CASO
# ============================================================
with tabs[0]:
    st.title("Centinela Digital")
    st.markdown(
        "### Monitorizando la integridad académica y científica con apoyo de IA\n"
    )

    with st.form("form_caso"):
        st.subheader("1. Información básica del caso")

        col1, col2 = st.columns(2)
        with col1:
            rol = st.selectbox(
                "Rol de quien entrega el trabajo",
                [
                    "Estudiante",
                    "Docente-investigador",
                    "Semillerista",
                    "Coinvestigador externo",
                    "Otro",
                ],
            )
        with col2:
            tipo_producto = st.selectbox(
                "Tipo de producto (ensayo, artículo, tesis, informe, etc.)",
                PRODUCT_OPTIONS,
            )

        st.subheader("2. Texto del trabajo (archivo o fragmento)")

        uploaded = st.file_uploader(
            "Sube un archivo Word, PDF o TXT (opcional)",
            type=["pdf", "docx", "doc", "txt"],
        )
        texto_archivo = extract_text_from_file(uploaded)
        texto_manual = st.text_area(
            "O pega un fragmento relevante del trabajo:",
            height=200,
        )

        texto_final = (texto_manual or "").strip() or (texto_archivo or "").strip()

        st.subheader("3. Evidencias estructuradas (primer filtro)")
        st.markdown(
            "Marca **Sí / No** según tus observaciones preliminares. "
            "Esto alimenta la matriz de riesgo."
        )

        evidencias = {
            "estilo_diferente": yn(
                "¿El estilo del texto es muy diferente al habitual de la persona?",
                key="ev_estilo",
            ),
            "tiempo_sospechoso": yn(
                "¿Fue entregado en un tiempo inusualmente corto para su complejidad?",
                key="ev_tiempo",
            ),
            "referencias_raras": yn(
                "¿Hay referencias 'raras', imposibles de encontrar o DOIs dudosos?",
                key="ev_refs",
            ),
            "datos_inconsistentes": yn(
                "¿Hay datos / resultados estadísticos sospechosos o poco creíbles?",
                key="ev_datos",
            ),
            "imagenes_sospechosas": yn(
                "¿Figuras o imágenes muy 'perfectas' o sin trazabilidad clara?",
                key="ev_imgs",
            ),
            "sin_borradores": yn(
                "¿No hay borradores ni historial de versiones del trabajo?",
                key="ev_borr",
            ),
            "defensa_debil": yn(
                "¿La persona no puede explicar ni defender lo que está escrito?",
                key="ev_def",
            ),
        }

        submitted = st.form_submit_button("🔎 Analizar caso con IA")

    if submitted:
        if not texto_final:
            st.error(
                "Necesitas subir un archivo o pegar al menos un fragmento de texto para poder analizar."
            )
        else:
            with st.spinner("Analizando caso con reglas + IA, por favor espera..."):
                # Reglas (matriz de riesgo)
                risk_df = build_risk_matrix(evidencias)
                base_score = risk_score_from_matrix(risk_df)

                # IA (OpenAI)
                gpt_result = call_gpt_analysis(texto_final, rol, tipo_producto, evidencias)

                overall_score = max(base_score, gpt_result.get("overall_risk_score", 0))
                level = overall_level(overall_score)

                # Diccionario completo para la interfaz
                analysis = {
                    "overall_risk_score": overall_score,
                    "overall_risk_level": level,
                    **gpt_result,
                }

                # Datos básicos del caso para el PDF
                case_data = {
                    "rol": rol,
                    "tipo_producto": tipo_producto,
                    "file_name": uploaded.name if uploaded else None,
                }

                # Datos específicos que usa el PDF
                report_data = {
                    "riesgo_global": overall_score,
                    "nivel_global": level,
                    "sentimiento": gpt_result.get("sentiment_label", "N/A"),
                    "num_evidencias": sum(evidencias.values()),
                    "red_flags": gpt_result.get("gpt_red_flags", []),
                    "acciones": gpt_result.get("mitigation_actions", []),
                    "kpis": gpt_result.get("kpis", []),
                    "insights": gpt_result.get("insights", []),
                    "narrativa": gpt_result.get("short_narrative", ""),
                }

                # Guardar en historial de la sesión
                st.session_state["historial"].append(
                    {
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                        "rol": rol,
                        "tipo_producto": tipo_producto,
                        "riesgo_global": overall_score,
                        "nivel": level,
                    }
                )

            st.success(f"Análisis completado. Nivel de riesgo global: **{level}**.")

            # ----- KPIs rápidos -----
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Riesgo global (0–100)", overall_score)
            col_b.metric("Sentimiento (IA)", gpt_result.get("sentiment_label", "N/A"))
            col_c.metric("Evidencias marcadas", sum(evidencias.values()))

            # ----- Matriz de riesgo -----
            st.markdown("### Matriz de riesgo por dimensión")
            st.dataframe(risk_df, use_container_width=True)

            chart = (
                alt.Chart(risk_df)
                .mark_bar()
                .encode(
                    x=alt.X("dimension:N", sort="-y", title="Dimensión"),
                    y=alt.Y("riesgo:Q", title="Puntaje de riesgo (0–3)"),
                    color="nivel:N",
                    tooltip=["dimension", "riesgo", "nivel"],
                )
                .properties(height=300)
            )
            st.altair_chart(chart, use_container_width=True)

            # ----- Insights, red flags y mitigación -----
            st.markdown("### Principales insights y red flags")
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Red flags (alertas)")
                if analysis.get("gpt_red_flags"):
                    for rf in analysis["gpt_red_flags"]:
                        st.markdown(f"- {rf}")
                else:
                    st.info("La IA no reportó red flags específicas (o no se pudo llamar a la API).")

            with col2:
                st.subheader("Acciones sugeridas / mitigación")
                if analysis.get("mitigation_actions"):
                    for ac in analysis["mitigation_actions"]:
                        st.markdown(f"- {ac}")
                else:
                    st.info("Aún no hay acciones sugeridas generadas por IA.")

            st.markdown("### KPIs e insights para seguimiento")
            if analysis.get("kpis"):
                st.write("**KPIs sugeridos:**")
                for k in analysis["kpis"]:
                    st.markdown(f"- {k}")

            if analysis.get("insights"):
                st.write("**Insights clave:**")
                for ins in analysis["insights"]:
                    st.markdown(f"- {ins}")

            if analysis.get("short_narrative"):
                st.markdown("### Síntesis narrativa del caso (IA)")
                st.write(analysis["short_narrative"])

            # ----- Informe PDF -----
            st.markdown("---")
            st.subheader("Informes automáticos para comité / tutor")
            try:
                # 🔴 AQUÍ ESTABA EL ERROR ANTES: se pasaban 3 argumentos.
                pdf_bytes = build_pdf_report(case_data, report_data)
                st.download_button(
                    label="📄 Descargar informe PDF del caso",
                    data=pdf_bytes,
                    file_name="informe_centinela_digital.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(
                    "Ocurrió un error al generar el PDF. Intenta con un texto más corto o sin URLs muy largas. "
                    f"Detalle técnico: {e}"
                )

# ============================================================
# TAB 2 – ESTADO ACTUAL Y PRÓXIMOS PASOS
# ============================================================
with tabs[1]:
    st.header("Estado actual y próximos pasos del proyecto")

    st.markdown(
        """
Esta es una **versión inicial estable** de Centinela Digital, pensada para:

- Probar el flujo de trabajo con casos individuales.
- Ajustar el modelo de análisis (reglas + IA).
- Construir evidencia para una futura versión institucional.

**Qué ya hace esta versión:**

- Recoge información básica del caso.
- Permite carga de archivos Word/PDF/TXT o texto pegado.
- Genera una matriz de riesgo por dimensiones.
- Llama (cuando está configurada) a la IA de OpenAI para:
  - análisis de sentimiento,
  - red flags,
  - acciones de mitigación,
  - KPIs e insights.
- Genera un **informe automático en PDF** para comités y tutores.
- Mantiene un **historial local** de los casos analizados en esta sesión de trabajo.

**Próximas extensiones previstas:**

1. Persistencia en base de datos (históricos institucionales).
2. Perfiles diferenciados (docente, coordinación, comité de ética, vicerrectoría).
3. Paneles comparativos por programa, cohorte, asignatura o semillero.
4. Módulos especiales:
   - Evaluación de proyectos de investigación.
   - Seguimiento a tesis y artículos en proceso de publicación.
   - Integración con reglamentos y matrices de decisión institucionales.
"""
    )

    if st.session_state["historial"]:
        st.markdown("### Historial de casos analizados en esta sesión")
        df_hist = pd.DataFrame(st.session_state["historial"])
        st.dataframe(df_hist, use_container_width=True)

        chart_hist = (
            alt.Chart(df_hist)
            .mark_line(point=True)
            .encode(
                x=alt.X("timestamp:T", title="Fecha y hora"),
                y=alt.Y("riesgo_global:Q", title="Riesgo global"),
                color="tipo_producto:N",
                tooltip=["timestamp", "rol", "tipo_producto", "nivel", "riesgo_global"],
            )
            .properties(height=300)
        )
        st.altair_chart(chart_hist, use_container_width=True)
    else:
        st.info("Aún no hay casos analizados en esta sesión. Usa la pestaña **Analizar un caso**.")

# ============================================================
# TAB 3 – PANEL PARA COMITÉS Y PROGRAMAS
# ============================================================
with tabs[2]:
    st.header("Panel de control para comités de ética y programas académicos")

    if st.session_state["historial"]:
        df_hist = pd.DataFrame(st.session_state["historial"])

        st.markdown("### Distribución de nivel de riesgo (solo sesión actual)")
        dist = df_hist.groupby("nivel").size().reset_index(name="casos")
        chart_risk = (
            alt.Chart(dist)
            .mark_bar()
            .encode(
                x=alt.X("nivel:N", title="Nivel de riesgo"),
                y=alt.Y("casos:Q", title="Número de casos"),
                color="nivel:N",
                tooltip=["nivel", "casos"],
            )
            .properties(height=250)
        )
        st.altair_chart(chart_risk, use_container_width=True)

        st.markdown("### Casos por tipo de producto")
        by_tipo = df_hist.groupby("tipo_producto").size().reset_index(name="casos")
        chart_tipo = (
            alt.Chart(by_tipo)
            .mark_bar()
            .encode(
                x=alt.X("tipo_producto:N", title="Tipo de producto"),
                y=alt.Y("casos:Q", title="Número de casos"),
                color="tipo_producto:N",
                tooltip=["tipo_producto", "casos"],
            )
            .properties(height=250)
        )
        st.altair_chart(chart_tipo, use_container_width=True)

        st.markdown(
            """
Este panel es un primer boceto para lo que podría ser un tablero institucional
de seguimiento. En una versión futura, estos datos vendrán de una base de datos
histórica (programas, cohortes, asignaturas, semilleros, etc.).
"""
        )
    else:
        st.info(
            "Aún no hay datos para el panel. Analiza uno o más casos en la pestaña **Analizar un caso**."
        )
