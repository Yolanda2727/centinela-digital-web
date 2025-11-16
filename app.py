import streamlit as st
import pandas as pd
import altair as alt
from textblob import TextBlob

# =========================
# CONFIGURACIÓN BÁSICA APP
# =========================
st.set_page_config(
    page_title="Centinela Digital",
    page_icon="🛡️",
    layout="wide"
)

# =========================
# ENCABEZADO GENERAL
# =========================
st.title("🛡️ Centinela Digital")
st.subheader("Monitorizando la integridad académica y científica con apoyo de IA")

st.markdown(
    """
Esta es una **versión inicial web** del modelo de monitoreo, pensada para apoyar a profesores, semilleros,
comités académicos y comités de ética en la identificación preliminar de posibles inconsistencias, desviaciones
o riesgos en trabajos académicos y científicos.
"""
)

st.info(
    "💻 **Software y modelo conceptual desarrollados por el Prof. Anderson Díaz Pérez**  \n"
    "Autor del sistema Centinela Digital para monitoreo de integridad académica y científica asistida por IA."
)

# =========================
# PESTAÑAS PRINCIPALES
# =========================
tab_analizar, tab_estado = st.tabs(
    ["🔍 Analizar un caso", "📊 Estado actual y próximos pasos"]
)

# =========================
# TAB 1: ANALIZAR UN CASO
# =========================
with tab_analizar:
    st.header("1. Información básica del caso")

    col1, col2 = st.columns(2)

    with col1:
        rol = st.selectbox(
            "Rol de quien entrega el trabajo",
            [
                "estudiante",
                "docente-investigador",
                "semillerista",
                "miembro de comité",
                "otro",
            ],
            index=1,
            help="Selecciona el rol principal de la persona que entrega el producto académico."
        )

    with col2:
        tipo_producto = st.selectbox(
            "Tipo de producto (ensayo, artículo, tesis, informe, etc.)",
            [
                "ensayo",
                "artículo",
                "tesis",
                "informe",
                "monografía",
                "proyecto de investigación",
                "otro",
            ],
            index=1,
            help="Selecciona el tipo de trabajo que estás evaluando."
        )

    st.markdown("### 2. Texto del trabajo (opcional)")

    texto_trabajo = st.text_area(
        "Pega aquí un fragmento del trabajo para análisis de sentimiento y consistencia:",
        height=220,
        placeholder="Puedes pegar introducción, discusión o cualquier sección representativa…"
    )

    st.markdown("### 3. Declaración de uso de IA (auto-reporte)")

    col3, col4 = st.columns(2)
    with col3:
        uso_declarado = st.radio(
            "La persona declara haber usado herramientas de IA generativa en este trabajo:",
            [
                "No lo menciona",
                "Sí, lo declara de forma transparente",
                "Lo menciona de forma ambigua",
            ],
            index=0
        )

    with col4:
        herramienta_mencionada = st.text_input(
            "Si lo declara, ¿qué herramienta menciona? (ChatGPT, Copilot, Gemini, etc.)",
            value=""
        )

    st.markdown("### 4. Ejecutar análisis preliminar")

    if st.button("🚦 Analizar caso con Centinela Digital"):
        if not texto_trabajo.strip():
            st.warning(
                "Para un análisis más útil, es recomendable pegar al menos un fragmento del texto."
            )

        # -------------------------
        # HEURÍSTICAS SIMPLES
        # -------------------------
        texto_lower = texto_trabajo.lower()

        # 1. Palabras clave de posible uso de IA
        palabras_ia = [
            "chatgpt",
            "copilot",
            "gemini",
            "inteligencia artificial",
            "modelo de lenguaje",
            "gpt-",
        ]
        indicios_palabras_ia = any(p in texto_lower for p in palabras_ia)

        # 2. Detección muy básica de estilo "genérico"
        num_palabras = len(texto_lower.split())
        densidad_palabras_formales = sum(
            1 for p in texto_lower.split()
            if p in ["por lo tanto", "en conclusión", "además", "sin embargo"]
        )

        # 3. Análisis de sentimiento (solo como descriptor)
        if texto_trabajo.strip():
            blob = TextBlob(texto_trabajo)
            sentimiento = blob.sentiment.polarity  # -1 a 1
        else:
            sentimiento = 0.0

        # Clasificación de riesgo MUY simple
        if uso_declarado == "Sí, lo declara de forma transparente":
            nivel_riesgo = "bajo"
            motivo = "La persona declara abiertamente el uso de IA. Se recomienda revisión formativa y verificación de referencias."
        elif indicios_palabras_ia and uso_declarado == "No lo menciona":
            nivel_riesgo = "alto"
            motivo = (
                "Se identifican referencias explícitas a herramientas de IA en el texto, "
                "pero no hay declaración de uso. Esto sugiere posible ocultamiento."
            )
        elif num_palabras > 0 and densidad_palabras_formales / max(num_palabras, 1) > 0.02:
            nivel_riesgo = "medio"
            motivo = (
                "El texto presenta alta densidad de conectores formales y estilo muy homogéneo. "
                "Podría ser indicio de apoyo intenso de IA, se sugiere entrevista corta."
            )
        else:
            nivel_riesgo = "bajo"
            motivo = (
                "No se identifican indicios fuertes de uso indebido de IA. "
                "Aun así, siempre es recomendable acompañar con retroalimentación."
            )

        # -------------------------
        # MOSTRAR RESULTADOS
        # -------------------------
        st.success("✅ Análisis preliminar generado.")

        col_res_1, col_res_2 = st.columns(2)

        with col_res_1:
            st.metric(
                "Nivel preliminar de riesgo ético asociado al uso de IA",
                value=nivel_riesgo.upper()
            )
            st.write("**Motivo principal:**")
            st.write(motivo)

        with col_res_2:
            st.write("**Datos descriptivos del fragmento analizado:**")
            st.write(f"- Número aproximado de palabras: **{num_palabras}**")
            st.write(
                f"- Sentimiento global (TextBlob): **{sentimiento:.2f}** "
                "(solo como descriptor; no implica juicio ético)"
            )
            st.write(
                "- Este módulo NO reemplaza el juicio del profesor o del comité; "
                "solo entrega señales para la conversación pedagógica y ética."
            )

        # Pequeño resumen textual
        st.markdown("---")
        st.markdown("#### Resumen narrativo del caso")
        resumen_txt = (
            f"Se evaluó un {tipo_producto} presentado por un **{rol}**. "
            f"El nivel preliminar de riesgo asociado al uso de IA se clasificó como **{nivel_riesgo.upper()}**. "
            f"{motivo}"
        )
        st.write(resumen_txt)

# =========================
# TAB 2: ESTADO ACTUAL
# =========================
with tab_estado:
    st.header("Estado actual (versión inicial)")

    st.markdown(
        """
Esta es la **versión mínima estable**, necesaria para desplegar en Streamlit Cloud, que incluye:

- Registro del rol de quien entrega el producto académico.
- Registro del tipo de documento entregado.
- Área para pegar un fragmento de texto y generar un análisis preliminar.
- Resumen narrativo sencillo del caso evaluado.
"""
    )

    st.markdown("### Próximos pasos que iremos agregando")

    pasos = [
        "Carga de archivos Word/PDF con extracción automática de texto.",
        "Matriz de riesgo más completa, con criterios de integridad académica e integridad científica.",
        "Integración de verificadores de referencias y consistencia de citas.",
        "Dashboard para comités académicos y comités de ética.",
        "Generación automática de informes éticos personalizados.",
    ]

    df_pasos = pd.DataFrame(
        {"Módulo": list(range(1, len(pasos) + 1)), "Descripción": pasos}
    )

    st.write("Listado de módulos previstos:")
    st.table(df_pasos)

    # Gráfica muy simple para evitar errores de Altair
    st.markdown("#### Avance planeado de módulos")

    df_chart = pd.DataFrame(
        {
            "Módulo": [f"M{i}" for i in range(1, len(pasos) + 1)],
            "Prioridad": list(reversed(range(1, len(pasos) + 1))),
        }
    )

    chart = (
        alt.Chart(df_chart)
        .mark_bar()
        .encode(
            x=alt.X("Módulo:N", title="Módulo previsto"),
            y=alt.Y("Prioridad:Q", title="Prioridad relativa"),
            tooltip=["Módulo", "Prioridad"],
        )
    )

    # Esta llamada estaba generando el ValueError; ahora nos aseguramos de que el DataFrame NO esté vacío
    if not df_chart.empty:
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Aún no hay datos suficientes para mostrar la gráfica.")

    st.markdown("---")
    st.markdown(
        """
**Créditos y propiedad intelectual**

- Modelo conceptual y software: **Prof. Anderson Díaz Pérez**.  
- Este prototipo forma parte de una línea de trabajo en integridad académica, integridad científica
  y uso responsable de IA en educación superior y en investigación.
"""
    )
