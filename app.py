# app.py
# -*- coding: utf-8 -*-
"""
Centinela Digital Web. 
Autor-Anderson Díaz Pérez
Corporacion Universitaria Iberoamerica.
Monitorizando la integridad académica y científica con apoyo de IA.

Versión 1.0 (mínimo producto viable en Streamlit):
- Registro del rol y tipo de producto.
- Ingreso de un fragmento de texto.
- Marcación de evidencias de posible uso problemático de IA.
- Cálculo de puntaje y nivel de riesgo.
- Recomendaciones básicas de programas y estrategias.
(Sin conexión a OpenAI todavía: la narrativa automática la añadimos en el siguiente paso.)
"""

import streamlit as st
from textblob import TextBlob

# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Centinela Digital",
    page_icon="🛡️",
    layout="centered"
)

# ---------------------------------------------------------
# DICCIONARIO DE PROGRAMAS / HERRAMIENTAS SUGERIDAS
# ---------------------------------------------------------
PROGRAMAS = {
    "texto_ia": {
        "descripcion": "Análisis de similitud y detección de texto posiblemente generado por IA.",
        "herramientas": [
            "Detectores de IA (por ejemplo: Turnitin, GPTZero).",
            "Herramientas de plagio (Turnitin, SafeAssign, etc.).",
            "Análisis lingüístico de coherencia, fluidez y patrones repetitivos."
        ],
        "alternativas": [
            "Pedir al autor que explique decisiones de redacción en una breve entrevista.",
            "Comparar con trabajos anteriores del mismo autor.",
            "Solicitar justificación de fuentes y argumentos."
        ],
    },
    "referencias": {
        "descripcion": "Verificación de existencia y consistencia de las referencias bibliográficas.",
        "herramientas": [
            "Google Scholar, PubMed, Scopus.",
            "Buscador de DOIs de Crossref / doi.org."
        ],
        "alternativas": [
            "Verificar manualmente 3–5 referencias en las bases disponibles.",
            "Pedir al autor los PDFs o enlaces reales de las fuentes citadas."
        ],
    },
    "datos": {
        "descripcion": "Coherencia de resultados numéricos y posibles manipulaciones.",
        "herramientas": [
            "statcheck (coherencia p-valores / estadísticos).",
            "GRIM / SPRITE (consistencia de medias y proporciones).",
            "Reproducir análisis en R, JASP, Jamovi o Python."
        ],
        "alternativas": [
            "Solicitar bases de datos crudas y recalcular estadísticas básicas.",
            "Analizar si n, medias y desviaciones tienen sentido clínico / disciplinar."
        ],
    },
    "imagenes": {
        "descripcion": "Detección de duplicación o manipulación de imágenes científicas.",
        "herramientas": [
            "ImageTwin, Proofig, Image Data Integrity.",
            "Herramientas forenses (revisión de metadatos, FotoForensics)."
        ],
        "alternativas": [
            "Pedir archivos originales de las imágenes.",
            "Comparar figuras con publicaciones previas del mismo autor."
        ],
    },
    "proceso": {
        "descripcion": "Trazabilidad del proceso de elaboración del trabajo.",
        "herramientas": [
            "Historial de versiones en Google Docs, Word online u Overleaf.",
            "Entrevista o defensa oral corta (5–10 minutos).",
            "Cuestionario de auto-reporte de uso de IA."
        ],
        "alternativas": [
            "Solicitar borradores enviados por correo u otros medios.",
            "Pedir que rehaga un fragmento clave en presencia del profesor."
        ],
    },
}

# ---------------------------------------------------------
# DICCIONARIO DE ESTRATEGIAS SEGÚN ROL Y NIVEL DE RIESGO
# ---------------------------------------------------------
ESTRATEGIAS = {
    ("estudiante", "bajo"): [
        "Explicar al estudiante qué se considera uso responsable de IA y la importancia de citarla.",
        "Solicitar una breve reflexión escrita sobre cómo usó o no usó IA en su trabajo.",
        "Registrar la observación en el seguimiento del curso (sin sanción).",
    ],
    ("estudiante", "medio"): [
        "Aplicar herramientas de apoyo (Turnitin, verificación de referencias, revisión de datos).",
        "Solicitar borradores previos y una defensa breve para valorar comprensión.",
        "Advertir sobre las políticas institucionales de integridad académica.",
        "Pedir la reescritura de secciones clave que muestren uso problemático de IA.",
        "Considerar una penalización leve (por ejemplo, rehacer el trabajo o reducir la nota).",
    ],
    ("estudiante", "alto"): [
        "Tratar el caso como posible fraude o plagio según el reglamento estudiantil.",
        "Escalar el caso a comité de ética o disciplina estudiantil.",
        "Exigir pruebas de originalidad y del proceso de elaboración del trabajo.",
        "Considerar sanciones disciplinarias significativas si se confirma la falta.",
    ],
    ("docente-investigador", "bajo"): [
        "Recordar buenas prácticas de citación y uso de herramientas en investigación.",
        "Solicitar una declaración del rol de la IA en el manuscrito.",
        "Ofrecer talleres o capacitaciones sobre IA y ética en investigación.",
    ],
    ("docente-investigador", "medio"): [
        "Solicitar evidencia del proceso de investigación (protocolo, bases de datos, borradores).",
        "Realizar revisión por pares internos o por un comité metodológico / de ética.",
        "Emitir una advertencia formal sobre integridad científica.",
        "Solicitar aclaraciones o correcciones en el trabajo (por ejemplo, erratas o notas editoriales).",
    ],
    ("docente-investigador", "alto"): [
        "Tratar el caso como posible mala conducta científica (fabricación, falsificación o plagio).",
        "Escalar a Comité de Ética en Investigación / Dirección de Investigaciones.",
        "Exigir evidencia completa: datos, cuadernos de laboratorio, scripts, comunicaciones.",
        "Seguir la ruta disciplinaria institucional si se confirma la falta.",
    ],
}

# ---------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------
def calcular_riesgo(evidencias_dict):
    """Devuelve puntaje de riesgo y nivel categórico."""
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


def recomendar_programas(evidencias_dict):
    """Selecciona qué dimensiones aplicar según las evidencias activas."""
    categorias = []

    if evidencias_dict["estilo_diferente"] or evidencias_dict["tiempo_sospechoso"]:
        categorias.append("texto_ia")
    if evidencias_dict["referencias_raras"]:
        categorias.append("referencias")
    if evidencias_dict["datos_inconsistentes"]:
        categorias.append("datos")
    if evidencias_dict["imagenes_sospechosas"]:
        categorias.append("imagenes")
    if evidencias_dict["sin_borradores"] or evidencias_dict["defensa_debil"]:
        categorias.append("proceso")

    # quitar duplicados manteniendo el orden
    categorias_unicas = []
    for c in categorias:
        if c not in categorias_unicas:
            categorias_unicas.append(c)

    return {c: PROGRAMAS[c] for c in categorias_unicas}


def recomendar_estrategias(rol, nivel_riesgo):
    """Devuelve lista de estrategias según rol y nivel de riesgo."""
    if rol.startswith("estud"):
        clave = ("estudiante", nivel_riesgo)
    else:
        clave = ("docente-investigador", nivel_riesgo)
    return ESTRATEGIAS.get(clave, [])


def analizar_sentimiento_texto(texto: str) -> str:
    """Análisis muy sencillo de sentimiento usando TextBlob (inglés/español mezclado)."""
    if not texto.strip():
        return "No se analizó sentimiento (texto vacío)."
    analisis = TextBlob(texto)
    pol = analisis.sentiment.polarity
    if pol > 0.1:
        return "El fragmento tiene un tono global más bien positivo."
    elif pol < -0.1:
        return "El fragmento tiene un tono global más bien negativo."
    else:
        return "El fragmento parece tener un tono neutro u objetivo."


def construir_explicacion_basica(
    rol, tipo_producto, nivel_riesgo, categoria_falta, evidencias, sentimiento
) -> str:
    """Explicación narrativa sencilla (sin GPT, solo texto estático + variables)."""
    evidencias_activas = [k for k, v in evidencias.items() if v]
    if evidencias_activas:
        lista_ev = ", ".join(evidencias_activas)
    else:
        lista_ev = "no se marcó ninguna evidencia específica"

    texto = []
    texto.append(
        f"En este caso se está evaluando un producto académico/científico de tipo "
        f"**{tipo_producto}**, elaborado por una persona en el rol de **{rol}**."
    )
    texto.append(
        f"A partir de las evidencias seleccionadas, el sistema calculó un **nivel de riesgo {nivel_riesgo.upper()}** "
        f"de posible uso inadecuado de herramientas de IA, clasificado como **{categoria_falta}**."
    )
    texto.append(
        f"Las evidencias principales que sustentan esta valoración son: {lista_ev}."
    )
    texto.append(
        "Este resultado **no prueba** por sí mismo que haya habido fraude o mala conducta, "
        "pero sí sugiere que conviene revisar con más detalle el trabajo, contrastar la información "
        "y documentar el proceso de manera transparente."
    )
    texto.append(sentimiento)
    texto.append(
        "El objetivo de Centinela Digital no es castigar, sino ayudar a formar mejores prácticas "
        "de integridad académica y científica, generando alertas razonables y proporcionales."
    )
    return "\n\n".join(texto)


# ---------------------------------------------------------
# INTERFAZ DE USUARIO
# ---------------------------------------------------------

# Encabezado principal
st.markdown(
    """
# 🛡️ Centinela Digital  
### Monitorizando la integridad académica y científica con apoyo de IA
"""
)

st.write(
    "Herramienta web diseñada para apoyar a profesores, semilleros, comités académicos y "
    "comités de ética en la **identificación preliminar de posibles desviaciones** o riesgos en "
    "trabajos académicos y científicos."
)

st.markdown("---")

# Estado actual
with st.expander("ℹ️ Estado actual de esta versión (mínima estable)", expanded=True):
    st.markdown(
        """
- Registro del **rol** de quien entrega el producto académico/científico.  
- Registro del **tipo de documento**.  
- Área para pegar un **fragmento de texto**.  
- Selección de **evidencias** de posible uso problemático de IA.  
- Cálculo de **puntaje y nivel de riesgo**.  
- Recomendaciones básicas de **herramientas** y **estrategias de actuación**.  

Próximos pasos que iremos agregando (siguientes versiones):

- Carga directa de archivos Word/PDF.  
- Gráficos de matriz de riesgo.  
- Explicación narrativa avanzada con modelos de IA (OpenAI).  
- Generación semiautomática de informe ético.
"""
    )

st.markdown("---")

# FORMULARIO PRINCIPAL
st.subheader("1️⃣ Registro del caso a evaluar")

with st.form("form_caso"):
    col1, col2 = st.columns(2)

    with col1:
        rol = st.radio(
            "Rol de quien entrega el trabajo",
            options=["estudiante", "docente-investigador"],
            index=0,
        )

    with col2:
        tipo_producto = st.selectbox(
            "Tipo de producto",
            [
                "Ensayo",
                "Artículo científico",
                "Tesis",
                "Informe técnico",
                "Proyecto de grado",
                "Otro",
            ],
        )

    texto_trabajo = st.text_area(
        "Pega un fragmento del texto (opcional, máximo aprox. 1500 caracteres):",
        height=200,
    )

    st.markdown("#### Evidencias observadas (marca las que apliquen)")

    c1, c2 = st.columns(2)

    with c1:
        estilo_diferente = st.checkbox(
            "Estilo del texto muy diferente al habitual de la persona"
        )
        tiempo_sospechoso = st.checkbox(
            "Entrega en un tiempo inusualmente corto para su complejidad"
        )
        referencias_raras = st.checkbox(
            "Referencias raras, imposibles de encontrar o DOIs dudosos"
        )
        datos_inconsistentes = st.checkbox(
            "Datos o resultados estadísticos poco creíbles o incoherentes"
        )

    with c2:
        imagenes_sospechosas = st.checkbox(
            "Figuras o imágenes muy perfectas o sin trazabilidad clara"
        )
        sin_borradores = st.checkbox(
            "No hay borradores ni historial de versiones del trabajo"
        )
        defensa_debil = st.checkbox(
            "La persona no puede explicar ni defender lo que está escrito"
        )

    submitted = st.form_submit_button("Analizar caso")

# ---------------------------------------------------------
# PROCESAMIENTO DEL CASO
# ---------------------------------------------------------
if submitted:
    # Construir diccionario de evidencias
    evidencias = {
        "estilo_diferente": estilo_diferente,
        "tiempo_sospechoso": tiempo_sospechoso,
        "referencias_raras": referencias_raras,
        "datos_inconsistentes": datos_inconsistentes,
        "imagenes_sospechosas": imagenes_sospechosas,
        "sin_borradores": sin_borradores,
        "defensa_debil": defensa_debil,
    }

    # Calcular riesgo
    score, nivel_riesgo = calcular_riesgo(evidencias)

    if rol.startswith("estud"):
        categoria_falta = "posible desviación ética académica (estudiante)"
    else:
        categoria_falta = "posible mala conducta científica (docente/investigador)"

    programas_sugeridos = recomendar_programas(evidencias)
    estrategias_sugeridas = recomendar_estrategias(rol, nivel_riesgo)
    sentimiento_texto = analizar_sentimiento_texto(texto_trabajo)
    explicacion = construir_explicacion_basica(
        rol,
        tipo_producto,
        nivel_riesgo,
        categoria_falta,
        evidencias,
        sentimiento_texto,
    )

    st.markdown("## 2️⃣ Resultado del análisis")

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Puntaje de riesgo", score)
    col_b.metric("Nivel de riesgo", nivel_riesgo.upper())
    col_c.metric("Clasificación preliminar", categoria_falta)

    st.markdown("### 2.1 Programas / herramientas sugeridas")
    if programas_sugeridos:
        for clave, info in programas_sugeridos.items():
            st.markdown(f"**Dimensión:** {clave}")
            st.write("**Qué analiza:**", info["descripcion"])
            st.write("**Herramientas recomendadas:**")
            for h in info["herramientas"]:
                st.write(f"- {h}")
            st.write("**Alternativas prácticas si no se dispone de esos programas:**")
            for alt in info["alternativas"]:
                st.write(f"- {alt}")
            st.markdown("---")
    else:
        st.info(
            "No se identificó ninguna dimensión específica para el uso de programas de apoyo. "
            "Esto suele ocurrir cuando no se marca ninguna evidencia."
        )

    st.markdown("### 2.2 Estrategias de prevención y actuación")

    if estrategias_sugeridas:
        for e in estrategias_sugeridas:
            st.write(f"- {e}")
    else:
        st.info(
            "No se encontraron estrategias específicas para esta combinación de rol y nivel de riesgo."
        )

    st.markdown("### 2.3 Explicación narrativa del caso")
    st.markdown(explicacion)

    st.markdown(
        """
> **Nota:** Este sistema orienta al profesor, tutor o comité;  
> **no reemplaza** el juicio ético humano ni el debido proceso institucional.
"""
    )
else:
    st.info(
        "Para empezar el análisis, diligencia el formulario anterior y pulsa en **“Analizar caso”**."
    )
