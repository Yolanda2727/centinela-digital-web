"""
Modelo de Análisis Mejorado para Centinela Digital

Incluye:
- Reglas ponderadas por dimensión
- Factores contextuales (rol, tipo de producto)
- Cálculo de confianza
- Análisis de patrones
"""

from typing import Dict, List, Tuple
import json


# ============================================================
# PESOS Y FACTORES CONTEXTUALES
# ============================================================

# Pesos por dimensión de análisis
DIMENSION_WEIGHTS = {
    "estilo_y_autoría": {
        "estilo_diferente": 0.4,
        "defensa_debil": 0.6,
    },
    "tiempo_y_ejecucion": {
        "tiempo_sospechoso": 0.5,
        "sin_borradores": 0.5,
    },
    "referencias_y_datos": {
        "referencias_raras": 0.4,
        "datos_inconsistentes": 0.6,
    },
    "presentacion": {
        "imagenes_sospechosas": 1.0,
    },
}

# Factores de riesgo base según rol (multiplicador)
ROLE_RISK_FACTORS = {
    "Estudiante": 1.0,
    "Docente-investigador": 0.7,
    "Semillerista": 0.9,
    "Coinvestigador externo": 0.6,
    "Otro": 0.8,
}

# Factores de riesgo según tipo de producto
PRODUCT_RISK_FACTORS = {
    "Ensayo": 0.8,
    "Artículo científico": 1.1,
    "Tesis": 1.2,
    "Informe técnico": 0.9,
    "Trabajo de curso": 0.9,
    "Proyecto de grado": 1.1,
    "Otro": 1.0,
}

# Umbrales de riesgo
RISK_THRESHOLDS = {
    "BAJO": (0, 33),
    "MEDIO": (33, 67),
    "ALTO": (67, 100),
}


# ============================================================
# FUNCIONES DE ANÁLISIS MEJORADAS
# ============================================================

def calculate_dimension_scores(evidencias: Dict[str, int]) -> Dict[str, float]:
    """
    Calcula puntuación normalizada (0-1) para cada dimensión.
    
    Args:
        evidencias: diccionario con valores binarios (0/1)
    
    Returns:
        diccionario con puntuaciones por dimensión
    """
    scores = {}
    
    for dimension, indicators in DIMENSION_WEIGHTS.items():
        dimension_score = 0.0
        for indicator, weight in indicators.items():
            if indicator in evidencias:
                dimension_score += evidencias[indicator] * weight
        
        # Normalizar a 0-1
        max_weight = sum(indicators.values())
        scores[dimension] = dimension_score / max_weight if max_weight > 0 else 0.0
    
    return scores


def apply_contextual_factors(
    base_scores: Dict[str, float],
    rol: str,
    tipo_producto: str
) -> Dict[str, float]:
    """
    Aplica factores contextuales según rol y tipo de producto.
    
    Args:
        base_scores: scores iniciales por dimensión
        rol: rol de quien entrega el trabajo
        tipo_producto: tipo de producto académico
    
    Returns:
        scores ajustados por contexto
    """
    adjusted_scores = {}
    
    role_factor = ROLE_RISK_FACTORS.get(rol, 1.0)
    product_factor = PRODUCT_RISK_FACTORS.get(tipo_producto, 1.0)
    
    for dimension, score in base_scores.items():
        # Aplicar factores acumulativos pero capped a 1.0
        adjusted = min(score * role_factor * product_factor, 1.0)
        adjusted_scores[dimension] = adjusted
    
    return adjusted_scores


def calculate_overall_risk(
    adjusted_scores: Dict[str, float],
    confidence_boost: float = 0.0
) -> Tuple[int, str, float]:
    """
    Calcula riesgo global (0-100), nivel y confianza.
    
    Args:
        adjusted_scores: scores ajustados por dimensión
        confidence_boost: incremento de confianza (0-1)
    
    Returns:
        tupla (score_global, nivel_riesgo, confianza)
    """
    # Promedio ponderado de dimensiones
    overall = sum(adjusted_scores.values()) / len(adjusted_scores) if adjusted_scores else 0.0
    
    # Escalar a 0-100
    score_0_100 = int(overall * 100)
    
    # Determinar nivel
    level = "BAJO"
    for level_name, (min_val, max_val) in RISK_THRESHOLDS.items():
        if min_val <= score_0_100 < max_val:
            level = level_name
            break
    if score_0_100 >= 67:
        level = "ALTO"
    
    # Confianza basada en consistencia de evidencias
    consistency = 1.0 - (max(adjusted_scores.values()) - min(adjusted_scores.values())) if adjusted_scores else 0.5
    confidence = min(consistency + confidence_boost, 1.0)
    
    return score_0_100, level, confidence


def analyze_with_improved_model(
    evidencias: Dict[str, int],
    rol: str,
    tipo_producto: str,
    num_evidencias_marked: int = None
) -> Dict:
    """
    Análisis completo con modelo mejorado.
    
    Args:
        evidencias: diccionario de evidencias binarias
        rol: rol del autor
        tipo_producto: tipo de producto
        num_evidencias_marked: número total de evidencias (para validación)
    
    Returns:
        diccionario completo con análisis
    """
    # Paso 1: Calcular scores por dimensión
    dimension_scores = calculate_dimension_scores(evidencias)
    
    # Paso 2: Aplicar factores contextuales
    adjusted_scores = apply_contextual_factors(
        dimension_scores,
        rol,
        tipo_producto
    )
    
    # Paso 3: Calcular riesgo global
    # Boost de confianza si hay muchas evidencias marcadas
    confidence_boost = min(num_evidencias_marked * 0.1, 0.3) if num_evidencias_marked else 0.0
    score, level, confidence = calculate_overall_risk(adjusted_scores, confidence_boost)
    
    # Paso 4: Identificar dimensiones críticas
    critical_dimensions = [
        dim for dim, score in adjusted_scores.items()
        if score > 0.6
    ]
    
    # Paso 5: Generar recomendaciones de acción
    recommendations = _generate_recommendations(
        adjusted_scores,
        critical_dimensions,
        score,
        nivel_riesgo=level
    )
    
    return {
        "dimension_scores": {k: round(v, 3) for k, v in adjusted_scores.items()},
        "overall_score": score,
        "overall_level": level,
        "confidence": round(confidence, 3),
        "critical_dimensions": critical_dimensions,
        "recommendations": recommendations,
        "contexto": {
            "rol": rol,
            "tipo_producto": tipo_producto,
            "role_factor": ROLE_RISK_FACTORS.get(rol, 1.0),
            "product_factor": PRODUCT_RISK_FACTORS.get(tipo_producto, 1.0),
        },
    }


def _generate_recommendations(
    adjusted_scores: Dict[str, float],
    critical_dims: List[str],
    score: int,
    nivel_riesgo: str
) -> List[str]:
    """
    Genera recomendaciones basadas en el análisis.
    """
    recommendations = []
    
    if nivel_riesgo == "ALTO":
        recommendations.append("Realizar una revisión exhaustiva antes de tomar decisiones.")
        recommendations.append("Considerar una entrevista adicional con el autor.")
        recommendations.append("Documentar todas las evidencias para auditoría.")
    
    if "estilo_y_autoría" in critical_dims:
        recommendations.append("Verificar cambios de estilo mediante herramientas especializadas.")
        recommendations.append("Solicitar defensa oral para validar comprensión.")
    
    if "referencias_y_datos" in critical_dims:
        recommendations.append("Validar referencias citadas y datos reportados.")
        recommendations.append("Consultar bases de datos académicas para verificar originalidad.")
    
    if "tiempo_y_ejecucion" in critical_dims:
        recommendations.append("Revisar cronología de entregas y versiones.")
        recommendations.append("Solicitar explicación sobre plazos.")
    
    if "presentacion" in critical_dims:
        recommendations.append("Inspeccionar metadatos de figuras e imágenes.")
        recommendations.append("Verificar coherencia visual con el contexto del trabajo.")
    
    if nivel_riesgo == "BAJO" and score < 20:
        recommendations.append("Trabajo dentro de parámetros normales.")
        recommendations.append("Continuar monitoreo periódico.")
    
    return recommendations


# ============================================================
# VALIDACIÓN Y COMPARACIÓN
# ============================================================

def validate_analysis(
    analysis_result: Dict,
    expected_level: str = None
) -> Dict:
    """
    Valida el resultado del análisis.
    
    Args:
        analysis_result: resultado del análisis
        expected_level: nivel esperado para validación
    
    Returns:
        reporte de validación
    """
    validation = {
        "is_valid": True,
        "warnings": [],
        "expected_vs_actual": None,
        "confidence_check": "OK",
    }
    
    # Validar que el score esté en rango
    if not (0 <= analysis_result["overall_score"] <= 100):
        validation["is_valid"] = False
        validation["warnings"].append("Score fuera de rango 0-100")
    
    # Validar confianza
    if analysis_result["confidence"] < 0.4:
        validation["confidence_check"] = "BAJA"
        validation["warnings"].append("Confianza muy baja del análisis")
    
    # Comparar con esperado
    if expected_level:
        if analysis_result["overall_level"] != expected_level:
            validation["expected_vs_actual"] = {
                "expected": expected_level,
                "actual": analysis_result["overall_level"],
                "match": False,
            }
        else:
            validation["expected_vs_actual"] = {
                "expected": expected_level,
                "actual": analysis_result["overall_level"],
                "match": True,
            }
    
    return validation


if __name__ == "__main__":
    # Test rápido del modelo
    test_evidencias = {
        "estilo_diferente": 1,
        "tiempo_sospechoso": 1,
        "referencias_raras": 0,
        "datos_inconsistentes": 1,
        "imagenes_sospechosas": 0,
        "sin_borradores": 0,
        "defensa_debil": 0,
    }
    
    result = analyze_with_improved_model(
        test_evidencias,
        "Estudiante",
        "Artículo científico",
        num_evidencias_marked=3
    )
    
    print("ANÁLISIS CON MODELO MEJORADO")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
