# app.py
# Centinela Digital Web – Versión inicial con formulario y matriz de riesgo

import os
import io
import streamlit as st
from textblob import TextBlob
from docx import Document
import PyPDF2
import altair as alt

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="Centinela Digital",
    page_icon="🛡️",
    layout="wide"
)

# Intentar importar cliente OpenAI (opcional)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False


# =========================
# DICCIONARIOS BASE
# =========================

PROGRAMAS = {
    "texto_ia": {
        "descripcion": "Análisis de similitud y detección de texto posiblemente generado por IA.",
        "herramientas": [
            "Detectores de IA (Turnitin, GPTZero, etc.).",
            "Herramientas de plagio (Turnitin, SafeAssign, etc.).",
            "Análisis lingüístico (coherencia, fluidez, patrones repetitivos).",
        ],
        "alternativas": [
            "Pedir al autor que explique decisiones de redacción.",
            "Comparar con trabajos anteriores del mismo autor.",
            "Solicitar justificación de fuentes y argumentos.",
        ],
    },
    "referencias": {
        "descripcion": "Verificación de existencia y consistencia de las referencias bibliográficas.",
        "herramientas": [
            "Google Scholar, PubMed, Scopus.",
            "Buscador de DOIs de Crossref / DOI.org.",
        ],
        "alternativas": [
            "Verificar manualmente 3–5 referencias en las bases disponibles.",
            "Solicitar al autor los PDFs o enlaces reales de las fuentes citadas.",
        ],
    },
    "datos": {
        "descripcion": "Coherencia de resultados numéricos y posibles manipulaciones.",
        "herramientas": [
            "statcheck (coherencia p-valores / estadísticos).",
            "GRIM / SPRITE (consistencia de medias y proporciones).",
            "Reproducir análisis en R, JASP, Jamovi o Python.",
        ],
        "alternativas": [
            "Solicitar bases de datos crudas y recalcular estadísticas básicas.",
            "Analizar si n, medias y desviaciones tienen sentido clínico / disciplinar.",
        ],
    },
    "imagenes": {
        "descripcion": "Detección de duplicación o manipulación de imágenes científicas.",
        "herramientas": [
            "ImageTwin, Proofig, Image Data Integrity.",
            "Herramientas forenses (FotoForensics, revisión de metadatos).",
        ],
        "alternativas": [
            "Pedir archivos originales de las imágenes.",
            "Comparar figuras con publicaciones previas del mismo autor.",
        ],
    },
    "proceso": {
        "descripcion": "Trazabilidad del proceso de elaboración del trabajo.",
        "herramientas": [
            "Historial de versiones en Google Docs, Word online, Overleaf.",
            "Entrevista o defensa oral corta (5–10 minutos).",
            "Cuestionario de auto-reporte de uso de IA (Forms).",
        ],
        "alternativas": [
            "Solicitar borradores enviados por correo u otros medios.",
            "Pedir que rehaga un fragmento clave en presencia del profesor.",
        ],
    },
}

ESTRATEGIAS = {
    ("estudiante", "bajo"): [
        "Explicar al estudiante qué se considera uso responsable de IA y la importancia de citarla.",
        "Solicitar una breve reflexión escrita sobre cómo usó o no usó IA en su trabajo.",
        "Registrar la observación en el seguimiento del curso (sin sanción).",
    ],
    ("estudiante", "medio"): [
        "Aplicar herramientas de apoyo (Turnitin, verificación de referencias, revisión de datos).",
        "Solicitar borradores previos y una defensa breve para valorar comprensión del tema.",
        "Advertir sobre las políticas institucionales de integridad académica.",
        "Pedir la reescritura de secciones clave que muestren uso problemático de IA.",
        "Considerar una penalización leve (por ejemplo, reducir nota o rehacer trabajo).",
    ],
    ("estudiante", "alto"): [
        "Tratar el caso como posible fraude académico conforme al reglamento estudiantil.",
        "Escalar el caso a comité de ética/disciplina estudiantil.",
        "Exigir pruebas de originalidad y proceso de elaboración del trabajo.",
        "Considerar sanciones disciplinarias significativas (reprobar curso, suspensión, etc.).",
    ],
    ("docente-investigador", "bajo"): [
        "Recordar buenas prácticas de citación y uso de herramientas en investigación.",
        "Solicitar una declaración del rol de la IA en su trabajo.",
        "Ofrecer talleres o capacitaciones sobre IA y ética en la investigación.",
    ],
    ("docente-investigador", "medio"): [
        "Solicitar evidencia del proceso de investigación (protocolo, bases de datos, borradores).",
        "Revisión por pares externos o por un comité interno.",
        "Advertencia formal sobre políticas de integridad científica.",
        "Solicitar aclaraciones o correcciones en el trabajo.",
    ],
    ("docente-investigador", "alto"): [
        "Tratar el caso como posible mala conducta científica (fabricación, falsificación o plagio).",
        "Escalar a Comité de Ética en Investigación / Dirección de Investigaciones.",
        "Exigir evidencia completa de datos, cuadernos de laboratorio, scripts y comunicaciones.",
        "Si se confirma, seguir la ruta disciplinaria institucional correspondiente.",
    ],
}


# =========================
# FUNCIONES AUXILIARES
# =========================

def extraer_texto_desde_archivo(uploaded_file) -> str:
    """Extrae texto de un archivo Word o PDF subido en Streamlit."""
    if uploaded_file is None:
        return ""

    nombre = uploaded_file.name.lower()

    if nombre.endswith(".docx"):
        # Leer desde buffer en memoria
        file_bytes = uploaded_file.read()
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)

    if nombre.endswith(".pdf"):
        texto = ""
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                texto += page_text + "\n"
        return texto

    return ""


def calcular_riesgo(evidencias_dict):
    pesos = {
        "estilo_diferente": 2,
        "tiempo_sospechoso": 1,
        "referencias_raras": 2,
        "datos_inconsistentes": 2,
        "imagenes_sospechosas": 2,
        "sin_borradores": 1,
        "defensa_debil": 2,
    }
    score = sum(pesos[k] for k, v in evidencias_dict.items() if v)

    if score <= 2:
        nivel = "bajo"
    elif score <= 5:
        nivel = "medio"
    else:
        nivel = "alto"
    return score, nivel


def recomendar_programas(evidencias):
    categorias = []
    if evidencias["estilo_diferente"] or evidencias["tiempo_sospechoso"]:
        categorias.append("texto_ia")
    if evidencias["referencias_raras"]:
        categorias.append("referencias")
    if evidencias["datos_inconsistentes"]:
        categorias.append("datos")
    if evidencias["imagenes_sospechosas"]:
        categorias.append("imagenes")
    if evidencias["sin_borradores"] or evidencias["defensa_debil"]:
        categorias.append("proceso")

    cat_unicas = []
    for c in categorias:
        if c not in cat_unicas:
            cat_unicas.append(c)

    return {c: PROGRAMAS[c] for c in cat_unicas}


def recomendar_estrategias(rol, nivel_riesgo):
    if rol.startswith("estud"):
        clave = ("estudiante", nivel_riesgo)
    else:
        clave = ("docente-investigador", nivel_riesgo)
    return ESTRATEGIAS.get(clave, [])


def obtener_sentimiento_objetivo(texto: str) -> str:
    if not texto:
        return "No hay texto suficiente para analizar."
    analysis = TextBlob(texto)
    if analysis.sentiment.polarity > 0.1:
        return "predominantemente positivo"
    elif analysis.sentiment.polarity < -0.1:
        return "predominantemente negativo"
    else:
        return "neutro / objetivo"


def generar_explicacion_openai(
    rol,
    tipo_producto,
    nivel_riesgo,
    categoria_falta,
    evidencias,
    programas,
    estrategias,
    texto_trabajo="",
):
    """Genera explicación narrativa usando OpenAI (si hay API KEY configurada)."""

    if not OPENAI_AVAILABLE:
        return "El módulo de OpenAI no está disponible en este entorno."

    # Buscar API key en secrets o variables de entorno
    api_key = None
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    elif os.getenv("OPENAI_API_KEY"):
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return (
            "No se encontró la clave de API de OpenAI. "
            "Configúrala en los *Secrets* de Streamlit para generar la explicación automática."
        )

    client = OpenAI(api_key=api_key)

    evidencias_activas = [k for k, v in evidencias.items() if v]
    evid_txt = ", ".join(evidencias_activas) if evidencias_activas else "ninguna evidencia marcada"

    prog_resumen = []
    for cat, info in programas.items():
        prog_resumen.append(f"{cat}: " + ", ".join(info["herramientas"]))
    prog_txt = "; ".join(prog_resumen) if prog_resumen else "no se sugirieron programas específicos"

    estr_txt = " | ".join(estrategias) if estrategias else "no se definieron estrategias específicas"
    fragmento = texto_trabajo[:1500] if texto_trabajo else ""

    sentimiento = obtener_sentimiento_objetivo(texto_trabajo)

    if rol.startswith("estud"):
        instruccion_rol = (
            "Como un tutor experimentado, tu explicación debe ser empática, "
            "formativa y constructiva, orientada a guiar al estudiante."
        )
    else:
        instruccion_rol = (
            "Como un colega experto en ética de investigación, tu explicación debe ser rigurosa, "
            "objetiva y enfocada en los principios de integridad científica."
        )

    prompt = f"""
Eres un experto en ética académica, integridad científica y docencia universitaria. {instruccion_rol}

DATOS DEL CASO:
- Rol de la persona evaluada: {rol}
- Tipo de producto: {tipo_producto}
- Nivel de riesgo calculado: {nivel_riesgo.upper()}
- Clasificación preliminar: {categoria_falta}
- Evidencias marcadas: {evid_txt}
- Sentimiento global del texto (TextBlob): {sentimiento}

PROGRAMAS / HERRAMIENTAS SUGERIDAS:
{prog_txt}

ESTRATEGIAS PROPUESTAS:
{estr_txt}

FRAGMENTO DEL TEXTO (si está disponible):
\"\"\"{fragmento}\"\"\"


TAREA:
1. Resume los hallazgos clave del caso, destacando el nivel de riesgo y la clasificación preliminar.
2. Explica brevemente por qué las evidencias marcadas pueden ser 'banderas rojas' de posible uso problemático de IA.
3. Describe para qué sirven los tipos de programas/herramientas sugeridos (sin hacer publicidad, solo función).
4. Explica cómo aplicar las estrategias de prevención y sanción, diferenciando:
   - un error formativo corregible
   - una falta grave que requiere ruta disciplinaria formal.
5. Termina con un mensaje corto que enfatice que el objetivo es formar en integridad, no hacer cacería de brujas.

Escribe la explicación en español, tono profesional pero accesible, en 350–450 palabras.
"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"No fue posible generar la explicación automática. Detalle técnico: {e}"


def graficar_evidencias_chart(evidencias_dict):
    """Devuelve un gráfico de barras simple con las evidencias activas."""
    activos = {k.replace("_", " ").title(): int(v) for k, v in evidencias_dict.items() if v}
    if not activos:
        return None

    data = [{"Evidencia": k, "Presente": v} for k, v in activos.items()]
    chart = (
        alt.Chart(alt.Data(values=data))
        .mark_bar()
        .encode(
            x=alt.X("Evidencia:N", sort="-y"),
            y=alt.Y("Presente:Q", axis=None),
            tooltip=["Evidencia"],
        )
    )
    return chart


# =========================
# INTERFAZ DE STREAMLIT
# =========================

st.title("🛡️ Centinela Digital")
st.subheader("Monitorizando la integridad académica y científica con apoyo de IA")

st.markdown(
    """
Esta es una **versión inicial web** del modelo de monitoreo, pensada para apoyar a profesores,
semilleros, comités académicos y comités de ética en la detección preliminar de posibles
inconsistencias, desviaciones o riesgos en trabajos académicos y científicos.
"""
)

tabs = st.tabs(["🔍 Analizar un caso", "ℹ️ Estado actual y próximos pasos"])

# =========================
# TAB 1 – ANALIZAR CASO
# =========================
with tabs[0]:
    st.markdown("### 1. Información básica del caso")

    col1, col2 = st.columns(2)

    with col1:
        rol = st.selectbox(
            "Rol de quien entrega el trabajo",
            ["estudiante", "docente-investigador"],
        )
        tipo_producto = st.text_input(
            "Tipo de producto (ensayo, artículo, tesis, informe, etc.)",
            value="ensayo",
        )

    with col2:
        st.markdown("**Texto del trabajo (opcional, para análisis de sentimiento y contexto):**")
        texto_manual = st.text_area(
            "Puedes pegar un fragmento relevante del texto.",
            height=180,
            placeholder="Pega aquí un fragmento del trabajo si lo deseas...",
        )

    st.markdown("---")
    st.markdown("### 2. Cargar archivo (opcional)")

    uploaded_file = st.file_uploader(
        "Sube un archivo Word (.docx) o PDF (.pdf). Si no subes archivo, se usará solo el texto pegado.",
        type=["docx", "pdf"],
    )

    texto_archivo = extraer_texto_desde_archivo(uploaded_file) if uploaded_file else ""
    texto_trabajo = texto_archivo if texto_archivo else texto_manual

    if uploaded_file and not texto_archivo:
        st.warning("No se pudo extraer texto del archivo. Verifica el formato o intenta con otro archivo.")

    st.markdown("---")
    st.markdown("### 3. Matriz de evidencias de posible uso problemático de IA")

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        estilo_diferente = st.checkbox(
            "El estilo del texto es muy diferente al habitual del autor."
        )
        tiempo_sospechoso = st.checkbox(
            "El trabajo se entregó en un tiempo inusualmente corto para su complejidad."
        )
        referencias_raras = st.checkbox(
            "Hay referencias 'raras', imposibles de encontrar o con DOIs dudosos."
        )
        datos_inconsistentes = st.checkbox(
            "Hay datos o resultados estadísticos poco creíbles o incoherentes."
        )

    with col_e2:
        imagenes_sospechosas = st.checkbox(
            "Las figuras o imágenes parecen demasiado 'perfectas' o sin trazabilidad clara."
        )
        sin_borradores = st.checkbox(
            "No hay borradores, historial de versiones ni trazabilidad del proceso."
        )
        defensa_debil = st.checkbox(
            "La persona no puede explicar ni defender lo que está escrito."
        )

    evidencias = {
        "estilo_diferente": estilo_diferente,
        "tiempo_sospechoso": tiempo_sospechoso,
        "referencias_raras": referencias_raras,
        "datos_inconsistentes": datos_inconsistentes,
        "imagenes_sospechosas": imagenes_sospechosas,
        "sin_borradores": sin_borradores,
        "defensa_debil": defensa_debil,
    }

    st.markdown("---")
    analizar = st.button("🧮 Analizar caso")

    if analizar:
        # 1. Riesgo numérico
        score, nivel_riesgo = calcular_riesgo(evidencias)

        if rol.startswith("estud"):
            categoria_falta = "posible desviación ética académica (estudiante)"
        else:
            categoria_falta = "posible mala conducta científica (docente/investigador)"

        # 2. Recomendaciones
        programas_sugeridos = recomendar_programas(evidencias)
        estrategias_sugeridas = recomendar_estrategias(rol, nivel_riesgo)
        sentimiento = obtener_sentimiento_objetivo(texto_trabajo)

        st.markdown("## 🔎 Resultados del análisis")

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Puntaje de riesgo", score)
        col_r2.metric("Nivel de riesgo", nivel_riesgo.upper())
        col_r3.metric("Clasificación preliminar", categoria_falta)

        st.markdown(f"**Análisis de sentimiento del texto (TextBlob):** {sentimiento}")

        # 3. Gráfico de evidencias
        chart = graficar_evidencias_chart(evidencias)
        if chart is not None:
            st.markdown("### 📊 Evidencias marcadas")
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No se marcó ninguna evidencia en la matriz de riesgo.")

        # 4. Programas sugeridos
        st.markdown("### 🧰 Programas y herramientas sugeridas")
        if programas_sugeridos:
            for cat, info in programas_sugeridos.items():
                st.markdown(f"**Dimensión:** {cat}")
                st.markdown(f"- Qué analiza: {info['descripcion']}")
                st.markdown("  - Herramientas/programas de referencia:")
                for h in info["herramientas"]:
                    st.markdown(f"    - {h}")
                st.markdown("  - Alternativas prácticas si no tienes acceso:")
                for a in info["alternativas"]:
                    st.markdown(f"    - {a}")
                st.markdown("")
        else:
            st.write("No se identificó ninguna dimensión específica para recomendar programas de apoyo.")

        # 5. Estrategias
        st.markdown("### 🧭 Estrategias de prevención y respuesta")
        if estrategias_sugeridas:
            for e in estrategias_sugeridas:
                st.markdown(f"- {e}")
        else:
            st.write(
                "No se encontraron estrategias específicas para esta combinación de rol y nivel de riesgo. "
                "Puedes apoyarte en el reglamento institucional y el comité de ética."
            )

        # 6. Explicación narrativa (OpenAI opcional)
        st.markdown("### 📝 Explicación narrativa del caso (opcional, usando OpenAI)")

        if OPENAI_AVAILABLE:
            if st.checkbox("Generar explicación automática con OpenAI (requiere API Key configurada)"):
                with st.spinner("Generando explicación ética con IA..."):
                    explicacion = generar_explicacion_openai(
                        rol=rol,
                        tipo_producto=tipo_producto,
                        nivel_riesgo=nivel_riesgo,
                        categoria_falta=categoria_falta,
                        evidencias=evidencias,
                        programas=programas_sugeridos,
                        estrategias=estrategias_sugeridas,
                        texto_trabajo=texto_trabajo,
                    )
                st.write(explicacion)
        else:
            st.info(
                "Para activar la explicación automática con OpenAI, instala la librería `openai` "
                "y configura la clave de API en los *Secrets* de Streamlit."
            )

        st.markdown(
            """
**Nota:** Este sistema orienta al profesor o comité, pero **no reemplaza** el juicio ético humano
ni el debido proceso institucional.
"""
        )

# =========================
# TAB 2 – ESTADO / ROADMAP
# =========================
with tabs[1]:
    st.markdown("### Estado actual (versión inicial)")

    st.write(
        """
Esta versión ya permite:

- Registrar el rol y tipo de producto académico.
- Cargar opcionalmente un archivo Word/PDF o pegar un fragmento de texto.
- Marcar evidencias de posible uso problemático de IA.
- Calcular un puntaje y nivel de riesgo.
- Sugerir programas/herramientas y estrategias pedagógicas/disciplinarias.
- Obtener un análisis básico de sentimiento del texto.
"""
    )

    st.markdown("### Próximos pasos posibles")

    st.write(
        """
- Ampliar la matriz de evidencias con ponderaciones configurables por la institución.
- Exportar el resultado como informe PDF para anexar a comités de ética o consejos de facultad.
- Registrar historial de casos (por usuario / programa / semestre).
- Integrar módulos específicos para **tesis**, **artículos científicos** y **trabajos de curso**.
- Conectar con modelos internos (cuando la universidad tenga su propia infraestructura de IA).
"""
    )

    st.info("Vamos paso a paso, construyendo el sistema de forma profesional y escalable. 🙌")
