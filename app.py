# app.py
# -*- coding: utf-8 -*-
"""
Centinela Digital Web
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
