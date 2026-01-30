# Guía Rápida de Implementación - Centinela Digital v2.0

## 🚀 Inicio Rápido

### 1. Ejecutar Tests

```bash
# Desde el directorio del proyecto
python test_runner.py
```

Esto validará:
- ✓ Estructura de 5 casos de prueba
- ✓ Análisis individual de cada caso
- ✓ Modelo mejorado de ponderación
- ✓ Persistencia en base de datos SQLite
- ✓ Generación de reportes

---

## 📚 Módulos Disponibles

### A. Análisis Mejorado

```python
from improved_analysis_model import analyze_with_improved_model

# Analizar un caso
resultado = analyze_with_improved_model(
    evidencias={
        "estilo_diferente": 1,
        "tiempo_sospechoso": 0,
        "referencias_raras": 1,
        "datos_inconsistentes": 0,
        "imagenes_sospechosas": 0,
        "sin_borradores": 0,
        "defensa_debil": 0,
    },
    rol="Estudiante",
    tipo_producto="Ensayo",
    num_evidencias_marked=2
)

# Acceder a resultados
print(f"Score: {resultado['overall_score']}/100")
print(f"Nivel: {resultado['overall_level']}")
print(f"Confianza: {resultado['confidence']}")
print(f"Recomendaciones: {resultado['recommendations']}")
```

**Output esperado:**
```
Score: 35/100
Nivel: BAJO
Confianza: 0.850
Recomendaciones: [
    'Trabajo dentro de parámetros normales.',
    'Continuar monitoreo periódico.'
]
```

---

### B. Persistencia de Datos

```python
from database import db

# Guardar un caso analizado
caso_id = db.guardar_caso({
    "rol": "Estudiante",
    "tipo_producto": "Ensayo",
    "riesgo_score": 35,
    "nivel_riesgo": "BAJO",
    "confianza": 0.85,
    "sentimiento": "neutro",
    "num_evidencias": 2,
    "texto_length": 2500,
    "red_flags": ["Patrón sospechoso"],
    "recomendaciones": ["Verificar referencias"],
})

# Recuperar
caso = db.obtener_caso(caso_id)

# Listar con filtros
casos_alto_riesgo = db.listar_casos(filtro_nivel="ALTO")

# Estadísticas
stats = db.obtener_estadisticas()
print(stats)  # {"total_casos": 5, "casos_alto_riesgo": 1, ...}
```

---

### C. Reportes Institucionales

```python
from institutional_metrics import InstitucionalMetrics, FollowUpMetrics

# Obtener todos los casos
casos = db.listar_casos(limite=1000)

# 1. Reporte Ejecutivo
reporte = InstitucionalMetrics.generar_reporte_ejecutivo(casos)

print(f"Total de casos: {reporte['resumen_general']['total_casos_analizados']}")
print(f"Distribución de riesgo: {reporte['tasas_por_nivel']}")
print(f"\nMétricas por rol:")
for rol, stats in reporte['metricas_por_rol'].items():
    print(f"  {rol}: {stats['total']} casos, {stats['tasa_alto_riesgo']}% alto riesgo")

print(f"\nRecomendaciones:")
for rec in reporte['recomendaciones_estrategicas']:
    print(f"  • {rec}")

# 2. Evolución Temporal
evolucion = FollowUpMetrics.calcular_evolucion_temporal(casos, agrupacion="mensual")

for periodo, stats in sorted(evolucion.items()):
    print(f"{periodo}: {stats['total']} casos, riesgo promedio {stats['promedio_riesgo']}")

# 3. Comparación entre períodos
reporte_comparativo = InstitucionalMetrics.comparar_periodos(
    casos_mes_anterior,
    casos_mes_actual,
    "Enero",
    "Febrero"
)
```

---

## 🧪 Casos de Prueba Disponibles

```python
from test_cases import get_all_test_cases

casos = get_all_test_cases()

for nombre, datos in casos.items():
    print(f"\n{nombre}:")
    print(f"  - Rol: {datos['rol']}")
    print(f"  - Tipo: {datos['tipo_producto']}")
    print(f"  - Riesgo esperado: {datos['expected_risk_level']}")
    print(f"  - Descripción: {datos['descripcion']}")
```

**Casos disponibles:**
1. `caso_bajo_riesgo` - Trabajo bien estructurado (BAJO)
2. `caso_riesgo_medio` - Con anomalías moderadas (MEDIO)
3. `caso_alto_riesgo` - Con múltiples alertas (ALTO)
4. `caso_edge_short` - Texto muy corto (caso límite)
5. `caso_investigador_externo` - Investigador profesional (BAJO)

---

## 🔗 Integración con Streamlit

Para conectar con `app.py`:

```python
# En app.py, tras cargar el formulario:

from improved_analysis_model import analyze_with_improved_model
from database import db

# Reemplazar análisis actual:
if submitted:
    with st.spinner("Analizando..."):
        # Análisis mejorado
        analysis_improved = analyze_with_improved_model(
            evidencias,
            rol,
            tipo_producto,
            num_evidencias_marked=sum(evidencias.values())
        )
        
        # Guardar en BD
        caso_id = db.guardar_caso({
            "rol": rol,
            "tipo_producto": tipo_producto,
            "riesgo_score": analysis_improved["overall_score"],
            "nivel_riesgo": analysis_improved["overall_level"],
            "confianza": analysis_improved["confidence"],
            "num_evidencias": sum(evidencias.values()),
            "red_flags": analysis_improved.get("critical_dimensions", []),
            "recomendaciones": analysis_improved.get("recommendations", []),
        })
        
        # Mostrar resultados
        st.success(f"Análisis completado: {analysis_improved['overall_level']}")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Riesgo (0-100)", analysis_improved["overall_score"])
        col_b.metric("Confianza", f"{analysis_improved['confidence']:.1%}")
        col_c.metric("Caso ID", caso_id[:8])
```

---

## 📊 Ejemplo: Pipeline Completo

```python
#!/usr/bin/env python3
"""Pipeline completo de análisis e integración."""

from test_cases import get_test_case
from improved_analysis_model import analyze_with_improved_model
from database import db
from institutional_metrics import InstitucionalMetrics

# 1. Seleccionar caso de prueba
caso = get_test_case("caso_riesgo_medio")

# 2. Análisis
print("Analizando caso...")
resultado = analyze_with_improved_model(
    caso["evidencias"],
    caso["rol"],
    caso["tipo_producto"],
)

# 3. Guardar en BD
print("Guardando en BD...")
caso_id = db.guardar_caso({
    "rol": caso["rol"],
    "tipo_producto": caso["tipo_producto"],
    "riesgo_score": resultado["overall_score"],
    "nivel_riesgo": resultado["overall_level"],
    "confianza": resultado["confidence"],
    "num_evidencias": sum(caso["evidencias"].values()),
})

# 4. Generar reporte
print("Generando reporte...")
todos_casos = db.listar_casos(limite=50)
reporte = InstitucionalMetrics.generar_reporte_ejecutivo(todos_casos)

# 5. Mostrar resultados
print(f"\nResultado del caso:")
print(f"  ID: {caso_id}")
print(f"  Score: {resultado['overall_score']}/100")
print(f"  Nivel: {resultado['overall_level']}")
print(f"  Confianza: {resultado['confidence']:.1%}")

print(f"\nReporte institucional:")
print(f"  Total casos: {reporte['resumen_general']['total_casos_analizados']}")
print(f"  Distribución: {reporte['tasas_por_nivel']}")
```

---

## ⚙️ Configuración

### Base de datos

Los datos se guardan automáticamente en:
```
.centinela_data/centinela.db
```

Para limpiar:
```bash
rm -rf .centinela_data/
```

Esto recreará la BD la próxima vez que se ejecute.

---

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'test_cases'"
**Solución**: Asegúrate de que todos los archivos `.py` estén en el mismo directorio.

### Error: "sqlite3.OperationalError: near ...": syntax error"
**Solución**: Elimina `.centinela_data/` y reinicia para recrear la BD.

### Test runner falla
**Solución**: Ejecutar con verbose:
```bash
python test_runner.py --verbose
```

---

## 📈 Métricas Clave para Monitoreo

La versión v2.0 captura:

- **Por caso**: Rol, tipo, score (0-100), nivel, confianza
- **Red flags**: Alertas específicas identificadas
- **Recomendaciones**: Acciones sugeridas
- **Temporal**: Timestamp de cada análisis
- **Agregado**: Tasas por rol, producto, tendencias

---

## 🎯 Próximos Pasos Sugeridos

1. Integrar módulos mejorados en `app.py`
2. Crear dashboard de monitoreo en Streamlit
3. Configurar exportación de reportes a Excel/PDF
4. Implementar alertas automáticas para casos alto riesgo
5. Generar KPIs automáticos para comités

---

**Versión**: 2.0  
**Última actualización**: Enero 2026  
**Status**: ✓ Listo para producción
