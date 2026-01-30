"""
Sistema Avanzado de Análisis de Integridad Científica
Incluye: plagio conceptual, desviaciones metodológicas, 
mala conducta científica, fabricación de datos, falacias
"""

from typing import Dict, List, Tuple
from datetime import datetime
import json


class AnálisisIntegridad:
    """Análisis avanzado de integridad científica"""
    
    # Patrones de plagio conceptual
    PLAGIO_CONCEPTUAL = {
        "sin_atribución": {
            "indicadores": [
                "Ideas idénticas sin cita",
                "Paráfrasis directa sin referencia",
                "Estructura argumental copiada",
                "Definiciones idénticas"
            ],
            "peso": 30
        },
        "reutilización_excesiva": {
            "indicadores": [
                ">40% contenido parafraseado de una fuente",
                "Múltiples párrafos del mismo autor",
                "Ideas de un solo autor dominan",
                "Referencias limitadas a un autor"
            ],
            "peso": 20
        }
    }
    
    # Desviaciones metodológicas
    DESVIACIONES_METODOLOGICAS = {
        "método_no_descrito": {
            "indicadores": [
                "Falta descripción del método",
                "Muestra no especificada",
                "Procedimiento incompleto",
                "Parámetros no definidos"
            ],
            "peso": 25
        },
        "incompatibilidad_método_objetivo": {
            "indicadores": [
                "Método no apropiado para objetivo",
                "Análisis inconsistente con diseño",
                "Estadística inapropiada",
                "Instrumentos no validados"
            ],
            "peso": 25
        },
        "cambios_posteriori": {
            "indicadores": [
                "Hipótesis cambiada después de análisis",
                "Métodos ajustados sin justificación",
                "Criterios modificados",
                "Análisis no preregistrados"
            ],
            "peso": 20
        }
    }
    
    # Mala conducta científica
    MALA_CONDUCTA = {
        "fabricación": {
            "indicadores": [
                "Datos exactos improbables",
                "Valores demasiado perfectos",
                "Distribuciones imposibles",
                "Resultados sin variabilidad"
            ],
            "peso": 40
        },
        "falsificación": {
            "indicadores": [
                "Datos omitidos selectivamente",
                "Outliers eliminados sin justificación",
                "Resultados negativos desaparecen",
                "Cambios en análisis"
            ],
            "peso": 35
        },
        "conflicto_interés": {
            "indicadores": [
                "Financiamiento no declarado",
                "Relaciones personales no mencionadas",
                "Incentivos no explícitos",
                "Presiones comerciales"
            ],
            "peso": 25
        }
    }
    
    # Falacias argumentativas
    FALACIAS = {
        "ad_hominem": {
            "descripción": "Ataque a la persona en lugar del argumento",
            "indicadores": ["crítica personal", "descalificación del autor"],
            "peso": 15
        },
        "falsa_causalidad": {
            "descripción": "Confundir correlación con causación",
            "indicadores": ["asume causalidad sin evidencia", "no controla variables"],
            "peso": 20
        },
        "generalización_excesiva": {
            "descripción": "Extrapolar conclusiones más allá de datos",
            "indicadores": ["conclusiones exageradas", "muestra pequeña"],
            "peso": 18
        },
        "apelación_autoridad": {
            "descripción": "Usar autoridad en lugar de evidencia",
            "indicadores": ["solo cita experto", "sin justificación científica"],
            "peso": 15
        },
        "argumento_circular": {
            "descripción": "Usar conclusión como premisa",
            "indicadores": ["razonamiento circular", "definición tautológica"],
            "peso": 18
        }
    }
    
    @staticmethod
    def analizar_integridad_completa(
        documento: Dict,
        rol: str = "Estudiante"
    ) -> Dict:
        """
        Análisis completo de integridad académica/científica
        
        Args:
            documento: Dict con contenido y metadatos
            rol: Rol del autor
        
        Returns:
            Dict con análisis detallado
        """
        
        resultados = {
            "timestamp": datetime.now().isoformat(),
            "rol": rol,
            "plagio_conceptual": AnálisisIntegridad._evaluar_plagio_conceptual(documento),
            "desviaciones_metodologicas": AnálisisIntegridad._evaluar_desviaciones(documento),
            "mala_conducta": AnálisisIntegridad._evaluar_mala_conducta(documento),
            "falacias": AnálisisIntegridad._evaluar_falacias(documento),
            "score_general": 0,
            "nivel_riesgo": "BAJO"
        }
        
        # Calcular score general
        scores = [
            resultados["plagio_conceptual"]["score"],
            resultados["desviaciones_metodologicas"]["score"],
            resultados["mala_conducta"]["score"],
            resultados["falacias"]["score"]
        ]
        
        resultados["score_general"] = sum(scores) / len(scores)
        
        # Determinar nivel de riesgo
        if resultados["score_general"] >= 70:
            resultados["nivel_riesgo"] = "CRÍTICO"
        elif resultados["score_general"] >= 50:
            resultados["nivel_riesgo"] = "ALTO"
        elif resultados["score_general"] >= 30:
            resultados["nivel_riesgo"] = "MEDIO"
        else:
            resultados["nivel_riesgo"] = "BAJO"
        
        # Agregar recomendaciones
        resultados["recomendaciones"] = AnálisisIntegridad._generar_recomendaciones(resultados)
        
        return resultados
    
    @staticmethod
    def _evaluar_plagio_conceptual(documento: Dict) -> Dict:
        """Evalúa plagio conceptual"""
        score = 0
        hallazgos = []
        
        # Simular análisis de plagio
        texto = documento.get("contenido", "").lower()
        
        # Analizar atribuciones
        if "(" not in texto or "[" not in texto:
            score += 15
            hallazgos.append("Pocas referencias/atribuciones detectadas")
        
        # Analizar repetición de fuentes
        ref_count = texto.count("según")
        if ref_count < 5 and len(texto) > 1000:
            score += 10
            hallazgos.append("Referencias limitadas para el tamaño del documento")
        
        return {
            "score": min(score, 100),
            "hallazgos": hallazgos,
            "detalles": {k: v for k, v in AnálisisIntegridad.PLAGIO_CONCEPTUAL.items()}
        }
    
    @staticmethod
    def _evaluar_desviaciones(documento: Dict) -> Dict:
        """Evalúa desviaciones metodológicas"""
        score = 0
        hallazgos = []
        
        # Verificar si es investigación
        if documento.get("tipo_documento") == "investigación":
            # Verificar descripción de método
            if "método" not in documento.get("contenido", "").lower():
                score += 25
                hallazgos.append("No describe el método utilizado")
            
            # Verificar muestra
            if "muestra" not in documento.get("contenido", "").lower():
                score += 15
                hallazgos.append("Tamaño/descripción de muestra no clara")
        
        return {
            "score": min(score, 100),
            "hallazgos": hallazgos,
            "detalles": {k: v for k, v in AnálisisIntegridad.DESVIACIONES_METODOLOGICAS.items()}
        }
    
    @staticmethod
    def _evaluar_mala_conducta(documento: Dict) -> Dict:
        """Evalúa mala conducta científica"""
        score = 0
        hallazgos = []
        
        contenido = documento.get("contenido", "").lower()
        
        # Verificar fabricación de datos
        if "simulado" in contenido or "asumido" in contenido:
            score += 10
            hallazgos.append("Posible uso de datos simulados sin indicación clara")
        
        # Verificar omisión de conflictos de interés
        if "conflicto" not in contenido and documento.get("rol") == "investigador":
            score += 15
            hallazgos.append("No declara posibles conflictos de interés")
        
        return {
            "score": min(score, 100),
            "hallazgos": hallazgos,
            "detalles": {k: v for k, v in AnálisisIntegridad.MALA_CONDUCTA.items()}
        }
    
    @staticmethod
    def _evaluar_falacias(documento: Dict) -> Dict:
        """Evalúa falacias argumentativas"""
        score = 0
        hallazgos = []
        
        contenido = documento.get("contenido", "").lower()
        
        # Detectar patrones de falacias
        falacias_detectadas = {
            "falsa_causalidad": ("por lo tanto", "causa", "causó"),
            "generalización_excesiva": ("siempre", "nunca", "todos", "nadie"),
            "apelación_autoridad": ("el experto dice", "según expertos"),
        }
        
        for falacia, palabras_clave in falacias_detectadas.items():
            if any(palabra in contenido for palabra in palabras_clave):
                score += 10
                hallazgos.append(f"Posible falacia: {falacia}")
        
        return {
            "score": min(score, 100),
            "hallazgos": hallazgos,
            "detalles": {k: v for k, v in AnálisisIntegridad.FALACIAS.items()}
        }
    
    @staticmethod
    def _generar_recomendaciones(resultados: Dict) -> List[str]:
        """Genera recomendaciones basadas en análisis"""
        recomendaciones = []
        
        if resultados["plagio_conceptual"]["score"] > 30:
            recomendaciones.append(
                "Revisar atribuciones y referencias. Asegurar todas las ideas se citan correctamente."
            )
        
        if resultados["desviaciones_metodologicas"]["score"] > 30:
            recomendaciones.append(
                "Describir claramente el método, muestra y procedimientos utilizados."
            )
        
        if resultados["mala_conducta"]["score"] > 20:
            recomendaciones.append(
                "Declarar todos los conflictos de interés y fuentes de financiamiento."
            )
        
        if resultados["falacias"]["score"] > 20:
            recomendaciones.append(
                "Revisar la lógica de argumentos. Distinguir entre correlación y causalidad."
            )
        
        if resultados["nivel_riesgo"] in ["CRÍTICO", "ALTO"]:
            recomendaciones.append(
                "Se recomienda revisión por supervisor/comité académico."
            )
        
        return recomendaciones


class AnálisisConMetadatos:
    """Análisis con metadatos completos"""
    
    @staticmethod
    def crear_análisis_completo(
        contenido: Dict,
        usuario: str,
        version_modelo: str = "2.1",
        temperatura: float = 0.7,
        prompts_usados: List[str] = None
    ) -> Dict:
        """
        Crea análisis con todos los metadatos
        
        Args:
            contenido: Contenido a analizar
            usuario: Usuario que realiza análisis
            version_modelo: Versión del modelo
            temperatura: Temperatura de generación
            prompts_usados: Lista de prompts utilizados
        
        Returns:
            Análisis completo con metadatos
        """
        
        if prompts_usados is None:
            prompts_usados = []
        
        analisis = AnálisisIntegridad.analizar_integridad_completa(contenido)
        
        # Agregar metadatos
        analisis_completo = {
            "metadatos": {
                "fecha": datetime.now().isoformat(),
                "usuario": usuario,
                "version_modelo": version_modelo,
                "temperatura": temperatura,
                "prompts_usados": prompts_usados,
                "ajustes": {
                    "temperatura": temperatura,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            },
            "análisis": analisis,
            "resultados": {
                "score_plagio_conceptual": analisis["plagio_conceptual"]["score"],
                "score_desviaciones": analisis["desviaciones_metodologicas"]["score"],
                "score_mala_conducta": analisis["mala_conducta"]["score"],
                "score_falacias": analisis["falacias"]["score"],
                "score_general": analisis["score_general"],
                "nivel_riesgo": analisis["nivel_riesgo"]
            }
        }
        
        return analisis_completo


# Ejemplos de patrones a detectar
PATRONES_MALA_CONDUCTA = {
    "datos_perfectos": {
        "patrón": r"\d+\.\d{2,}",
        "riesgo": "Valores con precisión sospechosa",
        "indicador": 0.8
    },
    "omisión_datos": {
        "patrón": r"(como se menciona|se reporta|n\s*=)",
        "riesgo": "Posible omisión de datos",
        "indicador": 0.6
    },
    "conflicto_interés": {
        "patrón": r"(financiado|patrocinado|fundación)",
        "riesgo": "Verificar conflictos de interés",
        "indicador": 0.5
    }
}
