#!/usr/bin/env python3
"""
Ejemplos de uso de los nuevos módulos de Centinela Digital v2.0

Este script demuestra:
1. Uso de casos de prueba
2. Análisis mejorado
3. Persistencia en BD
4. Generación de reportes
"""

import json
from datetime import datetime, timedelta


def ejemplo_1_casos_prueba():
    """Demuestra el uso de casos de prueba individuales."""
    print("\n" + "="*70)
    print("EJEMPLO 1: Casos de Prueba Individuales")
    print("="*70)
    
    from test_cases import get_all_test_cases, list_test_cases
    
    # Listar casos disponibles
    casos_disponibles = list_test_cases()
    print(f"\nCasos de prueba disponibles ({len(casos_disponibles)}):")
    for i, caso in enumerate(casos_disponibles, 1):
        print(f"  {i}. {caso}")
    
    # Detalles de un caso
    from test_cases import get_test_case
    
    caso = get_test_case("caso_bajo_riesgo")
    print(f"\nDetalles del caso 'caso_bajo_riesgo':")
    print(f"  Rol: {caso['rol']}")
    print(f"  Tipo de producto: {caso['tipo_producto']}")
    print(f"  Riesgo esperado: {caso['expected_risk_level']}")
    print(f"  Descripción: {caso['descripcion']}")
    print(f"  Longitud texto: {len(caso['texto'])} caracteres")
    print(f"  Evidencias marcadas: {sum(caso['evidencias'].values())} / 7")


def ejemplo_2_analisis_mejorado():
    """Demuestra el análisis mejorado con ponderaciones."""
    print("\n" + "="*70)
    print("EJEMPLO 2: Análisis Mejorado (Modelo de Ponderación)")
    print("="*70)
    
    from improved_analysis_model import analyze_with_improved_model
    from test_cases import get_test_case
    
    # Analizar los 3 casos principales
    casos_analizar = [
        "caso_bajo_riesgo",
        "caso_riesgo_medio",
        "caso_alto_riesgo",
    ]
    
    print("\nAnalizando casos con modelo mejorado:")
    print("-" * 70)
    
    for caso_name in casos_analizar:
        caso = get_test_case(caso_name)
        
        resultado = analyze_with_improved_model(
            caso["evidencias"],
            caso["rol"],
            caso["tipo_producto"],
            num_evidencias_marked=sum(caso["evidencias"].values()),
        )
        
        print(f"\n📋 {caso_name}:")
        print(f"  Score: {resultado['overall_score']}/100")
        print(f"  Nivel: {resultado['overall_level']}")
        print(f"  Confianza: {resultado['confidence']:.1%}")
        
        print(f"  Dimensiones:")
        for dim, score in resultado["dimension_scores"].items():
            print(f"    - {dim}: {score:.2f}")
        
        print(f"  Dimensiones críticas: {resultado['critical_dimensions']}")
        print(f"  Recomendaciones ({len(resultado['recommendations'])} items):")
        for i, rec in enumerate(resultado['recommendations'][:3], 1):
            print(f"    {i}. {rec}")


def ejemplo_3_persistencia_bd():
    """Demuestra almacenamiento y recuperación en BD."""
    print("\n" + "="*70)
    print("EJEMPLO 3: Persistencia en Base de Datos")
    print("="*70)
    
    from database import db
    from improved_analysis_model import analyze_with_improved_model
    from test_cases import get_test_case
    
    print("\nGuardando casos en BD...")
    
    casos_analizar = [
        "caso_bajo_riesgo",
        "caso_riesgo_medio",
        "caso_alto_riesgo",
    ]
    
    casos_guardados = []
    
    for caso_name in casos_analizar:
        caso = get_test_case(caso_name)
        resultado = analyze_with_improved_model(
            caso["evidencias"],
            caso["rol"],
            caso["tipo_producto"],
        )
        
        caso_id = db.guardar_caso({
            "caso_id": f"demo_{caso_name}",
            "rol": caso["rol"],
            "tipo_producto": caso["tipo_producto"],
            "riesgo_score": resultado["overall_score"],
            "nivel_riesgo": resultado["overall_level"],
            "confianza": resultado["confidence"],
            "num_evidencias": sum(caso["evidencias"].values()),
            "texto_length": len(caso["texto"]),
            "red_flags": resultado["critical_dimensions"],
            "recomendaciones": resultado["recommendations"][:3],
        })
        
        casos_guardados.append(caso_id)
        print(f"  ✓ Guardado: {caso_id}")
    
    # Recuperar casos
    print(f"\nRecuperando casos de BD:")
    for caso_id in casos_guardados:
        caso_recuperado = db.obtener_caso(caso_id)
        print(f"  • {caso_id}: {caso_recuperado['nivel_riesgo']} (score: {caso_recuperado['riesgo_score']})")
    
    # Listar con filtros
    print(f"\nCasos de alto riesgo:")
    casos_alto = db.listar_casos(filtro_nivel="ALTO")
    if casos_alto:
        for caso in casos_alto[:3]:
            print(f"  • {caso.get('caso_id')}: {caso['riesgo_score']}/100")
    else:
        print("  (Ninguno en esta BD)")
    
    # Estadísticas
    print(f"\nEstadísticas de hoy:")
    stats = db.obtener_estadisticas()
    print(f"  Total casos: {stats['total_casos']}")
    print(f"  - Alto riesgo: {stats['casos_alto_riesgo']}")
    print(f"  - Medio riesgo: {stats['casos_medio_riesgo']}")
    print(f"  - Bajo riesgo: {stats['casos_bajo_riesgo']}")
    print(f"  Promedio de riesgo: {stats['promedio_riesgo']}")


def ejemplo_4_reportes_institucionales():
    """Demuestra generación de reportes agregados."""
    print("\n" + "="*70)
    print("EJEMPLO 4: Reportes Institucionales")
    print("="*70)
    
    from database import db
    from institutional_metrics import InstitucionalMetrics
    
    # Obtener casos almacenados
    todos_casos = db.listar_casos(limite=100)
    
    if len(todos_casos) < 3:
        print("\n⚠️  Necesitamos al menos 3 casos para generar reportes.")
        print("    Ejecuta el Ejemplo 3 primero para generar datos.")
        return
    
    print(f"\nGenerando reporte ejecutivo para {len(todos_casos)} casos...")
    print("-" * 70)
    
    reporte = InstitucionalMetrics.generar_reporte_ejecutivo(todos_casos)
    
    # Resumen general
    print(f"\n📊 RESUMEN GENERAL:")
    print(f"  Total de casos analizados: {reporte['resumen_general']['total_casos_analizados']}")
    print(f"  Tasa de riesgo promedio: {reporte['resumen_general']['tasa_riesgo_general']:.1f}")
    
    # Tasas por nivel
    print(f"\n📈 DISTRIBUCIÓN DE RIESGO:")
    for nivel, tasa in reporte['tasas_por_nivel'].items():
        print(f"  {nivel}: {tasa}%")
    
    # Por rol
    print(f"\n👥 ANÁLISIS POR ROL:")
    for rol, stats in reporte['metricas_por_rol'].items():
        print(f"  {rol}:")
        print(f"    - Casos: {stats['total']}")
        print(f"    - Riesgo promedio: {stats['riesgo_promedio']}")
        print(f"    - Tasa alto riesgo: {stats['tasa_alto_riesgo']}%")
    
    # Por producto
    print(f"\n📄 ANÁLISIS POR TIPO DE PRODUCTO:")
    for producto, stats in reporte['metricas_por_producto'].items():
        print(f"  {producto}:")
        print(f"    - Casos: {stats['total']}")
        print(f"    - Riesgo promedio: {stats['riesgo_promedio']}")
        print(f"    - Tasa alto riesgo: {stats['tasa_alto_riesgo']}%")
    
    # Patrones
    print(f"\n🔍 PATRONES DETECTADOS:")
    patrones = reporte['patrones_detectados']
    
    if patrones['red_flags_frecuentes']:
        print(f"  Red flags más frecuentes:")
        for flag_data in patrones['red_flags_frecuentes'][:3]:
            print(f"    - {flag_data.get('flag', flag_data)}: {flag_data.get('frecuencia', 'N/A')} casos")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES ESTRATÉGICAS:")
    for i, rec in enumerate(reporte['recomendaciones_estrategicas'], 1):
        print(f"  {i}. {rec}")


def ejemplo_5_comparacion_periodos():
    """Demuestra comparación entre períodos."""
    print("\n" + "="*70)
    print("EJEMPLO 5: Comparación entre Períodos")
    print("="*70)
    
    from database import db
    from institutional_metrics import InstitucionalMetrics
    
    todos_casos = db.listar_casos(limite=100)
    
    if len(todos_casos) < 6:
        print("\n⚠️  Necesitamos al menos 6 casos para comparación.")
        return
    
    # Dividir en dos grupos (simulando periodos)
    mitad = len(todos_casos) // 2
    casos_p1 = todos_casos[:mitad]
    casos_p2 = todos_casos[mitad:]
    
    print(f"\nComparando {len(casos_p1)} casos vs {len(casos_p2)} casos...")
    print("-" * 70)
    
    comparacion = InstitucionalMetrics.comparar_periodos(
        casos_p1,
        casos_p2,
        "Período 1",
        "Período 2"
    )
    
    print(f"\n📊 PERÍODO 1:")
    print(f"  Total casos: {comparacion['comparacion']['Período 1']['total_casos']}")
    print(f"  Promedio riesgo: {comparacion['comparacion']['Período 1']['promedio_riesgo']}")
    print(f"  Distribución: {comparacion['comparacion']['Período 1']['tasa_riesgo']}")
    
    print(f"\n📊 PERÍODO 2:")
    print(f"  Total casos: {comparacion['comparacion']['Período 2']['total_casos']}")
    print(f"  Promedio riesgo: {comparacion['comparacion']['Período 2']['promedio_riesgo']}")
    print(f"  Distribución: {comparacion['comparacion']['Período 2']['tasa_riesgo']}")
    
    print(f"\n📈 CAMBIOS:")
    cambios = comparacion['cambios']
    if cambios:
        print(f"  Cambio promedio: {cambios.get('cambio_promedio_riesgo', 'N/A')}")
        print(f"  Cambio porcentual: {cambios.get('cambio_porcentual', 'N/A')}%")
        print(f"  Tendencia: {cambios.get('tendencia', 'N/A')}")


def ejemplo_6_evolucion_temporal():
    """Demuestra análisis de tendencias en el tiempo."""
    print("\n" + "="*70)
    print("EJEMPLO 6: Evolución Temporal")
    print("="*70)
    
    from database import db
    from institutional_metrics import FollowUpMetrics
    
    todos_casos = db.listar_casos(limite=100)
    
    if not todos_casos:
        print("\n⚠️  No hay casos para analizar evolución.")
        return
    
    print(f"\nAnalizando evolución temporal de {len(todos_casos)} casos...")
    print("-" * 70)
    
    # Agrupación diaria
    evolucion = FollowUpMetrics.calcular_evolucion_temporal(
        todos_casos,
        agrupacion="diaria"
    )
    
    print(f"\n📅 ANÁLISIS DIARIO:")
    for periodo in sorted(evolucion.keys())[-5:]:  # Últimos 5 días
        stats = evolucion[periodo]
        print(f"  {periodo}:")
        print(f"    - Casos: {stats['total']}")
        print(f"    - Riesgo promedio: {stats['promedio_riesgo']}")
        print(f"    - Alto riesgo: {stats['alto_riesgo']} ({stats['tasa_alto']}%)")


def main():
    """Ejecuta todos los ejemplos."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  EJEMPLOS DE USO - CENTINELA DIGITAL v2.0".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        # Ejecutar ejemplos
        ejemplo_1_casos_prueba()
        ejemplo_2_analisis_mejorado()
        ejemplo_3_persistencia_bd()
        ejemplo_4_reportes_institucionales()
        ejemplo_5_comparacion_periodos()
        ejemplo_6_evolucion_temporal()
        
        print("\n" + "="*70)
        print("✓ Todos los ejemplos completados exitosamente")
        print("="*70)
        print("\nPróximos pasos:")
        print("  1. Revisar GUIA_RAPIDA.md para ejemplos adicionales")
        print("  2. Ejecutar: python test_runner.py")
        print("  3. Integrar módulos en app.py")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
