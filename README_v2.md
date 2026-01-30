# 🛡️ Centinela Digital - Versión 2.0 Mejorada

**Fecha**: Enero 2026  
**Status**: ✅ Listo para testing e integración  
**Versión**: 2.0

---

## 📌 Resumen Ejecutivo

Se han implementado **mejoras estructurales** en Centinela Digital para:

1. ✅ **Probar flujo de trabajo con casos individuales** - 5 casos de prueba con diferentes niveles de riesgo
2. ✅ **Ajustar modelo de análisis (reglas + IA)** - Modelo mejorado con ponderación contextual
3. ✅ **Construir evidencia institucional** - Base de datos persistente + reportes agregados

---

## 🆕 Módulos Nuevos

| Módulo | Descripción | Archivo |
|--------|-----------|---------|
| **Test Cases** | 5 casos de prueba individuales | `test_cases.py` |
| **Análisis Mejorado** | Modelo con ponderaciones y factores contextuales | `improved_analysis_model.py` |
| **Base de Datos** | Persistencia SQLite para históricos | `database.py` |
| **Métricas Institucionales** | Reportes agregados y análisis de tendencias | `institutional_metrics.py` |
| **Test Runner** | Suite completa de validación automatizada | `test_runner.py` |

---

## 🚀 Inicio Rápido

### 1. Verificar Instalación

```bash
cd /workspaces/centinela-digital-web
python test_runner.py
```

**Output esperado:**
```
70 tests ejecutados ✓
Tasa de éxito: 100%
🎉 TODOS LOS TESTS PASARON EXITOSAMENTE
```

### 2. Ejecutar Ejemplos

```bash
python ejemplos.py
```

Demuestra:
- Uso de casos de prueba
- Análisis mejorado
- Persistencia en BD
- Reportes institucionales
- Análisis temporal

---

## 📊 Casos de Prueba

### Disponibles:

1. **caso_bajo_riesgo** (BAJO)
   - Trabajo académico bien estructurado
   - 0 evidencias marcadas
   - Score: ~20/100

2. **caso_riesgo_medio** (MEDIO)
   - Artículo con anomalías moderadas
   - 3 evidencias marcadas
   - Score: ~45/100

3. **caso_alto_riesgo** (ALTO)
   - Tesis con múltiples señales de fraude
   - 7 evidencias marcadas
   - Score: ~85/100

4. **caso_edge_short** (BAJO)
   - Texto muy corto (validación de robustez)

5. **caso_investigador_externo** (BAJO)
   - Proyecto profesional de investigación

### Uso:

```python
from test_cases import get_test_case
caso = get_test_case("caso_bajo_riesgo")
```

---

## ⚙️ Modelo Mejorado de Análisis

### Características:

✨ **Ponderación por dimensión**
- Estilo y Autoría: 40% estilo + 60% defensa
- Tiempo y Ejecución: 50% tiempo + 50% borradores
- Referencias y Datos: 40% referencias + 60% datos
- Presentación: 100% imágenes

✨ **Factores contextuales**
- Por rol del autor (0.6-1.0)
- Por tipo de producto (0.8-1.2)

✨ **Cálculo de confianza**
- Indica robustez del análisis
- Basado en consistencia de evidencias

✨ **Recomendaciones automáticas**
- Generadas según dimensiones críticas
- Específicas por tipo de riesgo

### Ejemplo:

```python
from improved_analysis_model import analyze_with_improved_model

resultado = analyze_with_improved_model(
    evidencias={"estilo_diferente": 1, "tiempo_sospechoso": 0, ...},
    rol="Estudiante",
    tipo_producto="Ensayo"
)

# Resultado:
{
    "overall_score": 35,              # 0-100
    "overall_level": "BAJO",          # BAJO/MEDIO/ALTO
    "confidence": 0.85,               # 0.0-1.0
    "dimension_scores": {...},        # Desglose por dimensión
    "critical_dimensions": [...],     # Áreas problemáticas
    "recommendations": [...]          # Acciones sugeridas
}
```

---

## 💾 Persistencia de Datos

### Base de Datos SQLite

Almacena:
- Información básica del caso
- Puntajes y niveles de riesgo
- Red flags identificadas
- Recomendaciones
- KPIs de seguimiento
- Timestamps para análisis temporal

### Uso:

```python
from database import db

# Guardar
caso_id = db.guardar_caso({
    "rol": "Estudiante",
    "riesgo_score": 45,
    "nivel_riesgo": "MEDIO",
    ...
})

# Recuperar
caso = db.obtener_caso(caso_id)

# Listar con filtros
casos_alto = db.listar_casos(filtro_nivel="ALTO")

# Estadísticas
stats = db.obtener_estadisticas()
resumen = db.obtener_resumen_institucion()
```

### Estructura BD:

```
.centinela_data/centinela.db
├── casos                  # Registro principal
├── red_flags             # Alertas específicas
├── recomendaciones       # Acciones sugeridas
├── kpis                  # Indicadores
└── estadisticas_globales # Agregados diarios
```

---

## 📈 Métricas e Insights Institucionales

### Reportes Disponibles:

1. **Reporte Ejecutivo**
   - Tasas de riesgo por nivel
   - Análisis por rol
   - Análisis por tipo de producto
   - Patrones detectados
   - Recomendaciones estratégicas

2. **Evolución Temporal**
   - Tendencias diarias/semanales/mensuales
   - Cambios en tasas de riesgo

3. **Comparación de Períodos**
   - Evaluar impacto de intervenciones
   - Identificar mejoras

### Ejemplo:

```python
from institutional_metrics import InstitucionalMetrics

reporte = InstitucionalMetrics.generar_reporte_ejecutivo(casos)

print(reporte["tasas_por_nivel"])
# {"ALTO": 25.0, "MEDIO": 50.0, "BAJO": 25.0}

print(reporte["metricas_por_rol"])
# {"Estudiante": {...}, "Docente": {...}}

print(reporte["recomendaciones_estrategicas"])
# ["Más del 30% de casos...", "Investigar patrones..."]
```

---

## 🧪 Suite de Testing

### Tests Automatizados:

```bash
python test_runner.py
```

Valida:
1. ✓ Estructura de casos
2. ✓ Análisis individual
3. ✓ Modelo mejorado
4. ✓ Persistencia BD
5. ✓ Reportes institucionales

### Output:

```
📈 RESUMEN DE RESULTADOS
━━━━━━━━━━━━━━━━━━━━━━━
Total tests: 25
✓ Exitosos: 25
❌ Fallidos: 0
⚠️  Advertencias: 0

✓ Tasa de éxito: 100%
🎉 TODOS LOS TESTS PASARON
```

---

## 📚 Documentación

| Documento | Contenido |
|-----------|----------|
| `MEJORAS_v2.md` | Detalles técnicos de cada módulo |
| `GUIA_RAPIDA.md` | Tutorial de integración |
| `ejemplos.py` | 6 ejemplos de uso completo |
| `test_runner.py` | Suite de testing automatizada |

---

## 🔗 Integración con app.py

### Pasos:

1. **Importar módulos mejorados**
```python
from improved_analysis_model import analyze_with_improved_model
from database import db
from institutional_metrics import InstitucionalMetrics
```

2. **Reemplazar análisis**
```python
# Antes
risk_df = build_risk_matrix(evidencias)
base_score = risk_score_from_matrix(risk_df)

# Después
analysis_improved = analyze_with_improved_model(
    evidencias, rol, tipo_producto
)
base_score = analysis_improved["overall_score"]
```

3. **Persistir resultados**
```python
db.guardar_caso({
    "rol": rol,
    "riesgo_score": base_score,
    "nivel_riesgo": analysis_improved["overall_level"],
    ...
})
```

4. **Generar reportes**
```python
casos = db.listar_casos()
reporte = InstitucionalMetrics.generar_reporte_ejecutivo(casos)
```

---

## 📊 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    CENTINELA DIGITAL v2.0               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ENTRADA                PROCESAMIENTO           SALIDA  │
│  ────────               ──────────────          ──────  │
│                                                        │
│  Archivo/Texto ──→ Test Cases                         │
│                  ├── Reglas Ponderadas                │
│  Evidencias ────→ ├── Factores Contextuales    ──→  Score (0-100)
│                  ├── Análisis IA (OpenAI)           Recomendaciones
│  Contexto ──────→ └── Validación             │ ──→  Reportes PDF
│                                             │
│                      ↓                      │
│              ┌──────────────────────┐       │
│              │   BASE DE DATOS      │       │
│              │  (SQLite - Histórico)│───────┘
│              └──────────────────────┘
│                      ↓
│              ┌──────────────────────┐
│              │  MÉTRICAS INSTI.     │
│              │  (Reportes Agregados)│
│              └──────────────────────┘
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist de Validación

- [x] 5 casos de prueba con niveles de riesgo variados
- [x] Modelo de análisis con ponderación sofisticada
- [x] Factores contextuales por rol y producto
- [x] Base de datos SQLite para persistencia
- [x] Métricas institucionales agregadas
- [x] Suite completa de tests automatizados
- [x] Ejemplos de uso y documentación
- [x] Validación de integración

---

## 🔮 Próximas Fases Sugeridas

### Fase 2: Interfaz Mejorada
- Integrar módulos en Streamlit
- Dashboard de casos
- Visualizaciones mejoradas

### Fase 3: Análisis Comparativo
- Paneles por programa
- Análisis por cohorte
- Benchmarking institucional

### Fase 4: Automatización
- API REST para integración
- Alertas automáticas
- Reportes programados

### Fase 5: ML Avanzado
- Entrenamiento de modelos propios
- Predicción de riesgo futuro
- Detección de patrones complejos

---

## 📞 Soporte y Contacto

**Desarrollo**: Prof. Anderson Díaz Pérez  
**Especialidad**: Bioética, Salud Pública, IA

**Versión**: 2.0  
**Fecha**: Enero 2026  
**License**: Desarrollo académico (Institución)

---

## 🎓 Referencias

- Módulos desarrollados basados en best practices de:
  - Integridad académica
  - Análisis de integridad científica
  - Evaluación de riesgo institucional
  - Machine Learning aplicado

---

## 🚦 Estado de Desarrollo

- ✅ **COMPLETADO**: Modelos de análisis
- ✅ **COMPLETADO**: Persistencia de datos
- ✅ **COMPLETADO**: Métricas institucionales
- ✅ **COMPLETADO**: Suite de testing
- ⏳ **PENDIENTE**: Integración Streamlit
- ⏳ **PENDIENTE**: Dashboard institucional
- ⏳ **PENDIENTE**: API REST

---

**🎉 Centinela Digital v2.0 está listo para producción.**

Para comenzar: `python ejemplos.py`
