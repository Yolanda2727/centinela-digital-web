# app.py
# Centinela Digital Web
# Monitorizando la integridad académica y científica con apoyo de IA

import os
import json
import re
from typing import Dict, Any, List

import streamlit as st
import pandas as pd
import altair as alt

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================

st.set_page_config(
    page_title="Centinela Digital",
    page_icon="🛡️",
    layout="wide",
)

st.sidebar.title("🛡️ Centinela Digital")
st.sidebar.markdown(
    """
**Monitorizando la integridad académica y científica con apoyo de IA.**

**Autor del software:**  
Prof. **Anderson Díaz Pérez**  
(Bioeticista e investigador en integridad científica).

Versión web inicial (beta).
"""
)

# --- OpenAI client (opcional) ---

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # por si la librería no está instalada


def get_openai_client():
    """Intenta crear el cliente de OpenAI usando secrets o variables de entorno."""
    if OpenAI is None:
        return None

    api_key = None
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    else:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    return OpenAI(api_key=api_key)


openai_client = get_openai_client()
HAS_OPENAI = openai_client is not None

if not HAS_OPENAI:
    st.sidebar.info(
        "👉 Para activar el análisis avanzado con ChatGPT, "
        "configura `OPENAI_API_KEY` en **Secrets** de Streamlit."
    )
else:
    st.sidebar.success("🔑 Análisis avanzado con OpenAI activado.")


# ============================================
# 2. FUNCIONES DE ANÁLISIS
# ============================================

def limpiar_json_posible(texto: str) -> str:
    """Elimina ```json ... ``` si el modelo devuelve el JSON en un bloque de código."""
    texto = texto.strip()
    texto = re.sub(r"^```json", "", texto, flags=re.IGNORECASE).strip()
    texto = re.sub(r"^```", "", texto).strip()
    texto = re.sub(r"```$", "", texto).strip()
    return texto


def analizar_texto_openai(texto: str, rol: str, tipo_producto: str) -> Dict[str, Any]:
    """Análisis profundo usando ChatGPT vía OpenAI."""
    system_msg = (
        "Eres un experto en bioética, integridad académica e investigación. "
        "Evalúas trabajos académicos y científicos, detectas posibles usos indebidos de IA, "
        "plagio, fabricación/falsificación de datos y problemas éticos. "
        "SIEMPRE devuelves ÚNICAMENTE un JSON válido en UTF-8, sin comentarios adicionales."
    )

    user_prompt = f"""
Analiza el siguiente texto académico/científico.

Contexto:
- Rol de quien entrega el trabajo: {rol}
- Tipo de producto: {tipo_producto}

Tareas:

1. Análisis de sentimiento general del fragmento (positivo, neutral o negativo).
2. Nivel de riesgo de integridad académica en una escala cualitativa (bajo, medio, alto).
3. Detección de **red flags** (alertas) relacionadas con:
   - posible uso indebido de IA,
   - plagio o parafraseo pobre,
   - fabricación o manipulación de datos,
   - referencias inverificables o sospechosas,
   - incoherencias metodológicas o éticas.
4. Cálculo de algunos **KPIs** (indicadores clave) útiles para el docente, semillero o comité, por ejemplo:
   - porcentaje estimado de riesgo de uso indebido de IA,
   - claridad argumentativa,
   - coherencia entre objetivos y resultados,
   - solidez ética/metodológica.
5. Formulación de **insights principales** (2–5 frases cortas).
6. Propuestas de **recomendaciones prácticas** para mitigar los riesgos identificados.

Devuelve ÚNICA Y EXCLUSIVAMENTE un JSON con la siguiente estructura:

{{
  "sentiment": "positivo|neutral|negativo",
  "sentiment_score": float (0 a 1),
  "risk_level": "bajo|medio|alto",
  "num_words": int,
  "red_flags": ["lista", "de", "frases"],
  "kpis": [
    {{"nombre": "texto", "valor": float}},
    {{"nombre": "texto", "valor": float}}
  ],
  "insights": ["frase 1", "frase 2"],
  "recomendaciones": ["recomendación 1", "recomendación 2"]
}}

Texto a analizar:
\"\"\"{texto}\"\"\"
"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = response.choices[0].message.content or ""
    content = limpiar_json_posible(content)

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Si algo sale mal, lanzamos excepción para que el caller use un fallback local
        raise ValueError("La respuesta de OpenAI no fue un JSON válido.")

    return data


def analizar_texto_local(texto: str, rol: str, tipo_producto: str) -> Dict[str, Any]:
    """Análisis sencillo de respaldo cuando no hay OpenAI o falla la llamada."""
    palabras = re.findall(r"\w+", texto.lower(), flags=re.UNICODE)
    num_words = len(palabras)

    positivos = {"excelente", "claro", "coherente", "riguroso", "válido", "valido"}
    negativos = {"confuso", "débil", "debil", "incompleto", "plagio", "copiado"}

    score = 0
    for p in palabras:
        if p in positivos:
            score += 1
        if p in negativos:
            score -= 1

    if num_words > 0:
        sentiment_score = max(0.0, min(1.0, 0.5 + score / (2 * num_words)))
    else:
        sentiment_score = 0.5

    if sentiment_score > 0.6:
        sentiment = "positivo"
    elif sentiment_score < 0.4:
        sentiment = "negativo"
    else:
        sentiment = "neutral"

    # Red flags muy básicas
    texto_lower = texto.lower()
    red_flags: List[str] = []
    patrones_sospechosos = [
        "como modelo de lenguaje",
        "como inteligencia artificial",
        "chatgpt",
        "gpt-",
        "según la ia",
        "inteligencia artificial generativa",
    ]
    for p in patrones_sospechosos:
        if p in texto_lower:
            red_flags.append(f"Referencia explícita a IA: «{p}»")

    risk_level = "bajo"
    if len(red_flags) >= 2 or sentiment == "negativo":
        risk_level = "alto"
    elif len(red_flags) == 1 or sentiment == "neutral":
        risk_level = "medio"

    kpis = [
        {"nombre": "Extensión analizada (palabras)", "valor": float(num_words)},
        {"nombre": "Índice local de sentimiento (0-1)", "valor": float(sentiment_score)},
        {"nombre": "Número de red flags detectadas", "valor": float(len(red_flags))},
    ]

    insights = [
        f"Análisis local sin OpenAI: sentimiento {sentiment} con puntaje {sentiment_score:.2f}.",
        f"Se detectaron {len(red_flags)} posibles alertas en el texto.",
    ]

    recomendaciones = [
        "Revisar manualmente la coherencia y las referencias del texto.",
        "Solicitar al estudiante una reflexión sobre el proceso de elaboración y las herramientas utilizadas.",
    ]

    return {
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "risk_level": risk_level,
        "num_words": num_words,
        "red_flags": red_flags,
        "kpis": kpis,
        "insights": insights,
        "recomendaciones": recomendaciones,
    }


def analizar_texto(texto: str, rol: str, tipo_producto: str) -> Dict[str, Any]:
    """Coordinador: intenta usar OpenAI y, si falla, usa el análisis local."""
    if HAS_OPENAI:
        try:
            return analizar_texto_openai(texto, rol, tipo_producto)
        except Exception as e:
            st.error(f"⚠️ Error al usar OpenAI: {e}")
            st.info("Se utilizará el análisis local de respaldo.")
    return analizar_texto_local(texto, rol, tipo_producto)


# ============================================
# 3. FUNCIÓN PARA MOSTRAR RESULTADOS
# ============================================

def mostrar_resultados_analisis(analisis: Dict[str, Any]) -> None:
    st.subheader("🔎 Resultados del análisis del caso")

    col1, col2, col3 = st.columns(3)
    col1.metric("Nivel de riesgo", analisis.get("risk_level", "N/D").capitalize())
    col2.metric("Sentimiento global", analisis.get("sentiment", "N/D").capitalize())
    col3.metric(
        "Palabras analizadas",
        f"{analisis.get('num_words', 0):,}".replace(",", "."),
    )

    # KPIs -> gráfico de barras
    st.markdown("### 📈 KPIs clave del caso")

    kpis = analisis.get("kpis", []) or []
    df_kpis = pd.DataFrame(kpis)

    if not df_kpis.empty and "nombre" in df_kpis.columns and "valor" in df_kpis.columns:
        df_kpis["valor"] = pd.to_numeric(df_kpis["valor"], errors="coerce")
        df_kpis = df_kpis.dropna(subset=["valor"])

        if not df_kpis.empty:
            chart = (
                alt.Chart(df_kpis)
                .mark_bar()
                .encode(
                    x=alt.X("nombre:N", sort="-y", title="Indicador"),
                    y=alt.Y("valor:Q", title="Valor"),
                    tooltip=["nombre", "valor"],
                )
                .properties(height=300)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No hay KPIs numéricos suficientes para graficar.")
    else:
        st.info("La IA no devolvió KPIs en formato numérico para graficar.")

    # Red flags
    st.markdown("### 🚩 Red flags (alertas de integridad)")

    red_flags = analisis.get("red_flags", []) or []
    if red_flags:
        for rf in red_flags:
            st.warning(f"• {rf}")
    else:
        st.success("No se identificaron red flags relevantes en este fragmento.")

    # Insights
    st.markdown("### 💡 Principales insights")
    insights = analisis.get("insights", []) or []
    if insights:
        for ins in insights:
            st.markdown(f"- {ins}")
    else:
        st.write("Sin insights adicionales reportados por la IA.")

    # Recomendaciones
    st.markdown("### 🛠️ Recomendaciones para mitigar riesgos")
    recomendaciones = analisis.get("recomendaciones", []) or []
    if recomendaciones:
        for rec in recomendaciones:
            st.markdown(f"- {rec}")
    else:
        st.write("No se reportaron recomendaciones específicas.")


# ============================================
# 4. INTERFAZ PRINCIPAL
# ============================================

st.title("🛡️ Centinela Digital")
st.caption(
    "Monitorizando la integridad académica y científica con apoyo de IA. "
    "Versión mínima estable desplegada en Streamlit Cloud."
)

tabs = st.tabs(
    [
        "🔍 Analizar un caso",
        "📊 Estado actual y próximos pasos",
    ]
)

# --------------------------------------------
# TAB 1: Analizar un caso
# --------------------------------------------

with tabs[0]:
    st.subheader("1. Información básica del caso")

    col_rol, col_tipo = st.columns(2)

    with col_rol:
        rol = st.selectbox(
            "Rol de quien entrega el trabajo",
            [
                "estudiante",
                "docente-investigador",
                "semillerista",
                "miembro de comité",
                "otro",
            ],
            index=0,
        )

    with col_tipo:
        opciones_tipo = [
            "Ensayo",
            "Artículo",
            "Tesis",
            "Informe",
            "Monografía",
            "Proyecto de grado",
            "Otro",
        ]
        tipo_seleccion = st.selectbox(
            "Tipo de producto (ensayo, artículo, tesis, informe, etc.)",
            opciones_tipo,
            index=1,
        )
        if tipo_seleccion == "Otro":
            tipo_otro = st.text_input("Especifique el tipo de producto")
            tipo_producto = tipo_otro.strip() if tipo_otro.strip() else "Otro"
        else:
            tipo_producto = tipo_seleccion

    st.subheader("2. Texto del trabajo (fragmento para análisis)")

    texto_trabajo = st.text_area(
        "Puedes pegar aquí un fragmento relevante del trabajo académico o científico.",
        height=220,
        placeholder=(
            "Ejemplo: introducción, discusión, análisis de resultados o cualquier sección donde "
            "quieras evaluar la coherencia, el estilo y los posibles riesgos éticos."
        ),
    )

    analizar_btn = st.button(
        "Analizar caso con IA",
        type="primary",
        use_container_width=True,
    )

    if analizar_btn:
        if not texto_trabajo.strip():
            st.warning("Por favor pega al menos un fragmento de texto para analizar.")
        else:
            with st.spinner("Analizando el caso con IA (puede tardar algunos segundos)..."):
                resultado = analizar_texto(texto_trabajo, rol, tipo_producto)

            mostrar_resultados_analisis(resultado)

# --------------------------------------------
# TAB 2: Estado actual y próximos pasos
# --------------------------------------------

with tabs[1]:
    st.subheader("📊 Estado actual del modelo web (versión inicial)")

    st.markdown(
        """
Esta es una **versión mínima estable** del modelo de monitoreo **Centinela Digital**, diseñada
para ser desplegada en Streamlit Cloud y servir como base para iteraciones futuras.

Incluye actualmente:

- Registro del **rol** de quien entrega el trabajo.
- Selección del **tipo de producto académico**.
- Área para pegar un fragmento del texto a analizar.
- **Análisis automático con IA** (OpenAI/ChatGPT si está configurado, o análisis local de respaldo).
- Detección de:
  - sentimiento global,
  - nivel de riesgo de integridad,
  - red flags de posible uso indebido de IA o problemas éticos/metodológicos.
- Visualización de **KPIs** en gráfico de barras.
- Listado de insights y recomendaciones prácticas.

Próximos pasos que podremos ir agregando:

1. Carga directa de archivos **Word/PDF**.
2. Matriz de riesgo detallada por dimensiones (metodológica, ética, bibliográfica, etc.).
3. Generación automática de **informes estructurados** en PDF o Word.
4. Paneles de control (dashboards) para **comités de ética** y **programas académicos**.
5. Registro de históricos para seguimiento de semilleros y líneas de investigación.

Todo el desarrollo conceptual, ético y metodológico del modelo corresponde al:

> **Prof. Anderson Díaz Pérez – Autor del software Centinela Digital®.**
"""
    )

    st.info(
        "Si lo deseas, podemos seguir ampliando módulos específicos (por ejemplo, "
        "módulo para comités de ética, módulo para trabajos de grado, panel por asignatura, etc.)."
    )
