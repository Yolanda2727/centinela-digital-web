"""
Módulo de Métricas e Insights Institucionales

Proporciona análisis agregados para construcción de evidencia
sobre integridad académica a nivel institucional.
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json


class InstitucionalMetrics:
    """Calcula métricas institucionales para reportes."""
    
    @staticmethod
    def calcular_tasa_riesgo(casos: List[Dict]) -> Dict[str, float]:
        """
        Calcula tasa de riesgo por nivel.
        
        Args:
            casos: lista de casos analizados
        
        Returns:
            tasas por nivel (ALTO, MEDIO, BAJO)
        """
        total = len(casos)
        if total == 0:
            return {"ALTO": 0.0, "MEDIO": 0.0, "BAJO": 0.0}
        
        por_nivel = {}
        for nivel in ["ALTO", "MEDIO", "BAJO"]:
            count = sum(1 for caso in casos if caso.get("nivel_riesgo") == nivel)
            por_nivel[nivel] = round((count / total) * 100, 2)
        
        return por_nivel
    
    @staticmethod
    def calcular_por_rol(casos: List[Dict]) -> Dict[str, Dict]:
        """
        Desglose de métricas por rol de autor.
        
        Returns:
            métricas agrupadas por rol
        """
        por_rol = {}
        
        for caso in casos:
            rol = caso.get("rol", "Sin especificar")
            if rol not in por_rol:
                por_rol[rol] = {
                    "total": 0,
                    "riesgo_alto": 0,
                    "riesgo_promedio": 0.0,
                    "casos": [],
                }
            
            por_rol[rol]["total"] += 1
            if caso.get("nivel_riesgo") == "ALTO":
                por_rol[rol]["riesgo_alto"] += 1
            por_rol[rol]["casos"].append(caso)
        
        # Calcular promedios
        for rol in por_rol:
            puntajes = [c.get("riesgo_score", 0) for c in por_rol[rol]["casos"]]
            por_rol[rol]["riesgo_promedio"] = (
                round(sum(puntajes) / len(puntajes), 2) if puntajes else 0
            )
            por_rol[rol]["tasa_alto_riesgo"] = round(
                (por_rol[rol]["riesgo_alto"] / por_rol[rol]["total"] * 100), 2
            )
        
        return por_rol
    
    @staticmethod
    def calcular_por_producto(casos: List[Dict]) -> Dict[str, Dict]:
        """
        Desglose de métricas por tipo de producto.
        """
        por_producto = {}
        
        for caso in casos:
            producto = caso.get("tipo_producto", "Sin especificar")
            if producto not in por_producto:
                por_producto[producto] = {
                    "total": 0,
                    "riesgo_alto": 0,
                    "riesgo_promedio": 0.0,
                    "casos": [],
                }
            
            por_producto[producto]["total"] += 1
            if caso.get("nivel_riesgo") == "ALTO":
                por_producto[producto]["riesgo_alto"] += 1
            por_producto[producto]["casos"].append(caso)
        
        # Calcular promedios
        for producto in por_producto:
            puntajes = [c.get("riesgo_score", 0) for c in por_producto[producto]["casos"]]
            por_producto[producto]["riesgo_promedio"] = (
                round(sum(puntajes) / len(puntajes), 2) if puntajes else 0
            )
            por_producto[producto]["tasa_alto_riesgo"] = round(
                (por_producto[producto]["riesgo_alto"] / por_producto[producto]["total"] * 100), 2
            )
        
        return por_producto
    
    @staticmethod
    def identificar_patrones(casos: List[Dict]) -> Dict[str, List[str]]:
        """
        Identifica patrones y anomalías en los casos.
        
        Returns:
            patrones detectados
        """
        patrones = {
            "red_flags_frecuentes": [],
            "combinaciones_sospechosas": [],
            "anomalias": [],
        }
        
        if not casos:
            return patrones
        
        # Red flags más frecuentes
        todas_flags = []
        for caso in casos:
            todas_flags.extend(caso.get("red_flags", []))
        
        from collections import Counter
        flags_count = Counter(todas_flags)
        patrones["red_flags_frecuentes"] = [
            {"flag": flag, "frecuencia": count}
            for flag, count in flags_count.most_common(5)
        ]
        
        # Combinaciones de características
        por_nivel = {}
        for nivel in ["ALTO", "MEDIO", "BAJO"]:
            casos_nivel = [c for c in casos if c.get("nivel_riesgo") == nivel]
            if casos_nivel:
                por_nivel[nivel] = {
                    "casos": len(casos_nivel),
                    "tasa": round(len(casos_nivel) / len(casos) * 100, 2),
                }
        
        patrones["distribucion_riesgo"] = por_nivel
        
        # Anomalías (casos muy atípicos)
        if casos:
            puntajes = [c.get("riesgo_score", 0) for c in casos]
            promedio = sum(puntajes) / len(puntajes)
            std_dev = (sum((x - promedio) ** 2 for x in puntajes) / len(puntajes)) ** 0.5
            
            threshold = promedio + 2 * std_dev
            anomalias = [c for c in casos if c.get("riesgo_score", 0) > threshold]
            
            if anomalias:
                patrones["anomalias"] = [
                    f"Caso {c.get('caso_id', 'N/A')}: Riesgo {c.get('riesgo_score')} "
                    f"(muy por encima de promedio {round(promedio, 1)})"
                    for c in anomalias[:3]
                ]
        
        return patrones
    
    @staticmethod
    def generar_reporte_ejecutivo(
        casos: List[Dict],
        periodo: str = "mensual"
    ) -> Dict:
        """
        Genera reporte ejecutivo para administración/comité.
        
        Args:
            casos: lista de casos
            periodo: "diario", "semanal", "mensual", "anual"
        
        Returns:
            reporte estructurado
        """
        return {
            "fecha_reporte": datetime.now().isoformat(),
            "periodo": periodo,
            "resumen_general": {
                "total_casos_analizados": len(casos),
                "tasa_riesgo_general": sum(c.get("riesgo_score", 0) for c in casos) / len(casos)
                if casos else 0,
            },
            "tasas_por_nivel": InstitucionalMetrics.calcular_tasa_riesgo(casos),
            "metricas_por_rol": InstitucionalMetrics.calcular_por_rol(casos),
            "metricas_por_producto": InstitucionalMetrics.calcular_por_producto(casos),
            "patrones_detectados": InstitucionalMetrics.identificar_patrones(casos),
            "recomendaciones_estrategicas": (
                InstitucionalMetrics._generar_recomendaciones_estrategicas(casos)
            ),
        }
    
    @staticmethod
    def _generar_recomendaciones_estrategicas(casos: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en patrones institucionales."""
        recomendaciones = []
        
        if not casos:
            return recomendaciones
        
        # Analizar si hay tendencia de alto riesgo
        tasa_alto = sum(1 for c in casos if c.get("nivel_riesgo") == "ALTO") / len(casos)
        
        if tasa_alto > 0.3:
            recomendaciones.append(
                "⚠️ Más del 30% de casos muestran alto riesgo. "
                "Se recomienda revisión de políticas institucionales y mayor capacitación."
            )
        
        if tasa_alto < 0.05:
            recomendaciones.append(
                "✓ Tasa baja de casos de alto riesgo. Continuar con medidas actuales."
            )
        
        # Por tipo de producto
        por_producto = InstitucionalMetrics.calcular_por_producto(casos)
        alto_riesgo_producto = [
            (p, stats) for p, stats in por_producto.items()
            if stats.get("tasa_alto_riesgo", 0) > 25
        ]
        
        if alto_riesgo_producto:
            prods = ", ".join([p for p, _ in alto_riesgo_producto])
            recomendaciones.append(
                f"Investigar patrones de riesgo en productos: {prods}. "
                "Considerrar capacitación específica o ajustes en procesos."
            )
        
        # Por rol
        por_rol = InstitucionalMetrics.calcular_por_rol(casos)
        alto_riesgo_rol = [
            (r, stats) for r, stats in por_rol.items()
            if stats.get("tasa_alto_riesgo", 0) > 20
        ]
        
        if alto_riesgo_rol:
            roles = ", ".join([r for r, _ in alto_riesgo_rol])
            recomendaciones.append(
                f"Grupos {roles} presentan tasa elevada de infracciones. "
                "Se sugiere intervención personalizada."
            )
        
        # Patrones de red flags
        patrones = InstitucionalMetrics.identificar_patrones(casos)
        flags_top = patrones.get("red_flags_frecuentes", [])
        
        if flags_top:
            flag_principal = flags_top[0]
            recomendaciones.append(
                f"Red flag más frecuente: '{flag_principal['flag']}' ({flag_principal['frecuencia']} casos). "
                "Diseñar estrategia de detección temprana."
            )
        
        return recomendaciones
    
    @staticmethod
    def comparar_periodos(
        casos_periodo1: List[Dict],
        casos_periodo2: List[Dict],
        nombre_p1: str = "Período 1",
        nombre_p2: str = "Período 2"
    ) -> Dict:
        """
        Compara métricas entre dos períodos.
        
        Útil para evaluar mejora tras intervenciones.
        """
        return {
            "comparacion": {
                nombre_p1: {
                    "total_casos": len(casos_periodo1),
                    "tasa_riesgo": InstitucionalMetrics.calcular_tasa_riesgo(casos_periodo1),
                    "promedio_riesgo": (
                        round(sum(c.get("riesgo_score", 0) for c in casos_periodo1) / len(casos_periodo1), 2)
                        if casos_periodo1 else 0
                    ),
                },
                nombre_p2: {
                    "total_casos": len(casos_periodo2),
                    "tasa_riesgo": InstitucionalMetrics.calcular_tasa_riesgo(casos_periodo2),
                    "promedio_riesgo": (
                        round(sum(c.get("riesgo_score", 0) for c in casos_periodo2) / len(casos_periodo2), 2)
                        if casos_periodo2 else 0
                    ),
                },
            },
            "cambios": InstitucionalMetrics._calcular_cambios(
                casos_periodo1, casos_periodo2
            ),
        }
    
    @staticmethod
    def _calcular_cambios(casos_p1: List[Dict], casos_p2: List[Dict]) -> Dict:
        """Calcula cambios entre períodos."""
        if not casos_p1 or not casos_p2:
            return {}
        
        prom_p1 = sum(c.get("riesgo_score", 0) for c in casos_p1) / len(casos_p1)
        prom_p2 = sum(c.get("riesgo_score", 0) for c in casos_p2) / len(casos_p2)
        
        cambio = prom_p2 - prom_p1
        cambio_pct = (cambio / prom_p1 * 100) if prom_p1 != 0 else 0
        
        return {
            "cambio_promedio_riesgo": round(cambio, 2),
            "cambio_porcentual": round(cambio_pct, 2),
            "tendencia": "↑ EMPEORA" if cambio > 0 else "↓ MEJORA" if cambio < 0 else "→ ESTABLE",
        }


# Clase para seguimiento a través del tiempo
class FollowUpMetrics:
    """Métricas de seguimiento y evolución."""
    
    @staticmethod
    def calcular_evolucion_temporal(
        casos_historicos: List[Dict],
        agrupacion: str = "diaria"
    ) -> Dict[str, Dict]:
        """
        Agrupa casos por período temporal.
        
        Args:
            casos_historicos: lista de todos los casos
            agrupacion: "diaria", "semanal", "mensual"
        
        Returns:
            evolución por período
        """
        from collections import defaultdict
        
        por_periodo = defaultdict(list)
        
        for caso in casos_historicos:
            timestamp = caso.get("timestamp") or caso.get("created_at")
            if not timestamp:
                continue
            
            try:
                fecha = datetime.fromisoformat(timestamp)
                
                if agrupacion == "diaria":
                    clave = fecha.date().isoformat()
                elif agrupacion == "semanal":
                    semana = fecha.isocalendar()
                    clave = f"{fecha.year}-W{semana[1]:02d}"
                elif agrupacion == "mensual":
                    clave = f"{fecha.year}-{fecha.month:02d}"
                else:
                    clave = fecha.date().isoformat()
                
                por_periodo[clave].append(caso)
            except (ValueError, AttributeError):
                continue
        
        # Calcular métricas por período
        evolucion = {}
        for periodo in sorted(por_periodo.keys()):
            casos = por_periodo[periodo]
            evolucion[periodo] = {
                "total": len(casos),
                "promedio_riesgo": round(
                    sum(c.get("riesgo_score", 0) for c in casos) / len(casos), 2
                ),
                "alto_riesgo": sum(1 for c in casos if c.get("nivel_riesgo") == "ALTO"),
                "tasa_alto": round(
                    sum(1 for c in casos if c.get("nivel_riesgo") == "ALTO") / len(casos) * 100, 2
                ),
            }
        
        return evolucion


if __name__ == "__main__":
    # Prueba rápida
    casos_ejemplo = [
        {"nivel_riesgo": "ALTO", "riesgo_score": 85, "rol": "Estudiante", "tipo_producto": "Tesis"},
        {"nivel_riesgo": "MEDIO", "riesgo_score": 50, "rol": "Estudiante", "tipo_producto": "Ensayo"},
        {"nivel_riesgo": "BAJO", "riesgo_score": 20, "rol": "Docente", "tipo_producto": "Artículo"},
    ]
    
    reporte = InstitucionalMetrics.generar_reporte_ejecutivo(casos_ejemplo)
    print(json.dumps(reporte, indent=2, ensure_ascii=False))
