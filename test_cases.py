"""
Test Cases Individuales para Centinela Digital

Este módulo contiene casos de prueba para validar el flujo de trabajo
de análisis de integridad académica con IA.

Casos de prueba:
1. Caso Low Risk: Trabajo de calidad con pocas señales de alerta
2. Caso Medium Risk: Trabajo con algunas anomalías moderadas
3. Caso High Risk: Trabajo con múltiples señales de fraude/plagio
4. Caso Edge Case: Texto muy corto o con errores de extracción
"""

TEST_CASES = {
    "caso_bajo_riesgo": {
        "rol": "Estudiante",
        "tipo_producto": "Ensayo",
        "texto": """
La integridad académica es fundamental en la educación superior. 
Este ensayo examina cómo las instituciones pueden fortalecer su cultura 
de honestidad intelectual a través de múltiples estrategias.

Primero, es esencial que los estudiantes comprendan las normas institucionales 
desde el primer semestre. Según Smith (2022), la claridad en las expectativas 
reduce significativamente las infracciones no intencionales.

En segundo lugar, los docentes deben modelar conductas éticas en la investigación 
y la enseñanza. Thompson y Lee (2021) documentan que los estudiantes replican 
los estándares que observan en sus mentores académicos.

Finalmente, los sistemas de detección y apoyo deben ser proporcionales y estar 
orientados hacia la formación. No se trata únicamente de castigar, sino de 
reconocer infracciones como oportunidades para mejorar.

En conclusión, una cultura de integridad se construye a través de educación, 
modelado y sistemas justos de rendición de cuentas.
        """,
        "evidencias": {
            "estilo_diferente": 0,
            "tiempo_sospechoso": 0,
            "referencias_raras": 0,
            "datos_inconsistentes": 0,
            "imagenes_sospechosas": 0,
            "sin_borradores": 0,
            "defensa_debil": 0,
        },
        "expected_risk_level": "BAJO",
        "descripcion": "Trabajo académico bien estructurado, sin señales de alerta.",
    },
    
    "caso_riesgo_medio": {
        "rol": "Estudiante",
        "tipo_producto": "Artículo científico",
        "texto": """
Este artículo investiga la relación entre uso de inteligencia artificial 
y rendimiento académico.

MÉTODOS: Se realizó un análisis en 500 estudiantes durante 2024. 
Se utilizaron herramientas estándar de evaluación.

RESULTADOS: Se encontró una correlación positiva significativa (p<0.05) 
entre el uso de IA y notas más altas. El tamaño del efecto fue grande (r=0.78).

Los datos mostraron patrones interesantes en diferentes facultades. 
En Ingeniería, el efecto fue mayor que en Humanidades.

DISCUSIÓN: Estos hallazgos sugieren que la IA puede ser una herramienta 
pedagógica efectiva. Sin embargo, se requiere más investigación para 
comprender los mecanismos subyacentes.

CONCLUSIÓN: La integración cuidadosa de IA en la educación merece 
un análisis más profundo.
        """,
        "evidencias": {
            "estilo_diferente": 1,
            "tiempo_sospechoso": 1,
            "referencias_raras": 0,
            "datos_inconsistentes": 1,
            "imagenes_sospechosas": 0,
            "sin_borradores": 0,
            "defensa_debil": 0,
        },
        "expected_risk_level": "MEDIO",
        "descripcion": "Trabajo con algunas anomalías: estilo inconsistente, datos potencialmente cuestionables.",
    },
    
    "caso_alto_riesgo": {
        "rol": "Estudiante",
        "tipo_producto": "Tesis",
        "texto": """
La inteligencia artificial ha revolucionado el mundo moderno de manera sin precedentes.
El aprendizaje automático es una rama fascinante de la IA que permite a las máquinas 
aprender de los datos.

Las redes neuronales profundas son particularmente interesantes. Ellas utilizan 
múltiples capas de neuronas artificiales para procesar información compleja.

El transformador es un modelo reciente que ha mostrado resultados excepcionales 
en procesamiento de lenguaje natural. BERT y GPT son ejemplos notables.

En conclusión, la IA y el aprendizaje automático son tecnologías cruciales 
para el futuro de la humanidad y representan una revolución tecnológica sin precedentes.
        """,
        "evidencias": {
            "estilo_diferente": 1,
            "tiempo_sospechoso": 1,
            "referencias_raras": 1,
            "datos_inconsistentes": 1,
            "imagenes_sospechosas": 1,
            "sin_borradores": 1,
            "defensa_debil": 1,
        },
        "expected_risk_level": "ALTO",
        "descripcion": "Trabajo con múltiples señales de alerta: sin referencias adecuadas, superficial, probablemente generado por IA.",
    },
    
    "caso_edge_short": {
        "rol": "Semillerista",
        "tipo_producto": "Trabajo de curso",
        "texto": "IA es importante.",
        "evidencias": {
            "estilo_diferente": 0,
            "tiempo_sospechoso": 0,
            "referencias_raras": 0,
            "datos_inconsistentes": 0,
            "imagenes_sospechosas": 0,
            "sin_borradores": 0,
            "defensa_debil": 0,
        },
        "expected_risk_level": "BAJO",
        "descripcion": "Texto muy corto - verifica que el sistema maneja bien los casos límite.",
    },
    
    "caso_investigador_externo": {
        "rol": "Coinvestigador externo",
        "tipo_producto": "Proyecto de grado",
        "texto": """
PROYECTO: Evaluación de Modelos de Predicción en Salud Pública

OBJETIVO: Comparar la precisión de algoritmos de machine learning 
en la predicción de enfermedades crónicas.

METODOLOGÍA: Estudio transversal con 1,200 participantes de tres instituciones. 
Se aplicaron 8 modelos diferentes (regresión logística, árboles de decisión, 
SVM, redes neuronales, etc.).

RESULTADOS PARCIALES: 
- Regresión logística: AUC = 0.82
- Random Forest: AUC = 0.89
- Red neuronal profunda: AUC = 0.91

Estos resultados son preliminares y están siendo validados 
en una cohorte independiente.

IMPLICACIONES: Los resultados sugieren que los modelos complejos 
suponen un mejor desempeño, aunque con mayor complejidad computacional.

Este trabajo respeta todos los protocolos de bioética y ha sido 
revisado por el comité institucional.
        """,
        "evidencias": {
            "estilo_diferente": 0,
            "tiempo_sospechoso": 0,
            "referencias_raras": 0,
            "datos_inconsistentes": 0,
            "imagenes_sospechosas": 0,
            "sin_borradores": 0,
            "defensa_debil": 0,
        },
        "expected_risk_level": "BAJO",
        "descripcion": "Trabajo profesional de investigación con metodología clara y transparencia.",
    },
}


def get_test_case(case_name: str) -> dict:
    """Retorna un caso de prueba por su nombre."""
    return TEST_CASES.get(case_name)


def get_all_test_cases() -> dict:
    """Retorna todos los casos de prueba disponibles."""
    return TEST_CASES


def list_test_cases() -> list:
    """Retorna la lista de nombres de casos disponibles."""
    return list(TEST_CASES.keys())


if __name__ == "__main__":
    # Script para visualizar casos de prueba disponibles
    print("=" * 70)
    print("CASOS DE PRUEBA DISPONIBLES PARA CENTINELA DIGITAL")
    print("=" * 70)
    
    for idx, (case_name, case_data) in enumerate(TEST_CASES.items(), 1):
        print(f"\n{idx}. {case_name.upper()}")
        print(f"   Rol: {case_data['rol']}")
        print(f"   Tipo: {case_data['tipo_producto']}")
        print(f"   Riesgo esperado: {case_data['expected_risk_level']}")
        print(f"   Descripción: {case_data['descripcion']}")
        print(f"   Evidencias marcadas: {sum(case_data['evidencias'].values())}")
        print(f"   Longitud texto: {len(case_data['texto'])} caracteres")
