# Centinela Digital - Mejoras v2.0

## 📋 Resumen

Este documento describe las mejoras implementadas en **Centinela Digital** para:

1. **Probar el flujo de trabajo con casos individuales**
2. **Ajustar el modelo de análisis (reglas + IA)**
3. **Construir evidencia para una futura versión institucional**

---

## 🚀 Nuevos Módulos

### 1. **test_cases.py** - Casos de Prueba Individuales

Proporciona 5 casos de prueba para validar el flujo completo:

#### Casos incluidos:

- **caso_bajo_riesgo**: Trabajo académico bien estructurado sin alertas (BAJO)
- **caso_riesgo_medio**: Artículo con anomalías moderadas (MEDIO)
- **caso_alto_riesgo**: Tesis con múltiples señales de fraude (ALTO)
- **caso_edge_short**: Texto muy corto - caso límite
- **caso_investigador_externo**: Proyecto profesional de investigación

#### Uso:

```python
from test_cases import get_all_test_cases, get_test_case

# Obtener todos los casos
casos = get_all_test_cases()

# Obtener caso específico
caso = get_test_case("caso_bajo_riesgo")
```

---

### 2. **improved_analysis_model.py** - Modelo Mejorado de Análisis

Implementa un modelo de análisis más sofisticado con:

#### Características:

- **Pesos ponderados por dimensión**: Cada evidencia tiene un peso específico
- **Factores contextuales**: Ajustes según rol y tipo de producto
- **Cálculo de confianza**: Indica cuán confiable es el análisis
- **Recomendaciones automáticas**: Basadas en dimensiones críticas

#### Dimensiones de análisis:

1. **Estilo y Autoría** (40% estilo diferente + 60% defensa débil)
2. **Tiempo y Ejecución** (50% tiempo sospechoso + 50% sin borradores)
3. **Referencias y Datos** (40% referencias raras + 60% datos inconsistentes)
4. **Presentación** (100% imágenes sospechosas)

#### Factores contextuales:

| Rol | Factor |
|-----|--------|
| Estudiante | 1.0 |
| Docente-investigador | 0.7 |
| Coinvestigador externo | 0.6 |

#### Uso:

```python
from improved_analysis_model import analyze_with_improved_model

resultado = analyze_with_improved_model(
    evidencias={
        "estilo_diferente": 1,
        "tiempo_sospechoso": 0,
        # ... más evidencias
    },
    rol="Estudiante",
    tipo_producto="Ensayo",
    num_evidencias_marked=3
)

print(resultado["overall_score"])      # 0-100
print(resultado["overall_level"])      # BAJO/MEDIO/ALTO
print(resultado["confidence"])         # 0.0-1.0
print(resultado["recommendations"])    # Lista de acciones
```

---

### 3. **database.py** - Persistencia en Base de Datos

Almacena históricos completos para análisis institucional:

#### Tablas:

- **casos**: Registro principal de análisis
- **red_flags**: Alertas específicas por caso
- **recomendaciones**: Acciones sugeridas
- **kpis**: Indicadores de desempeño
- **estadisticas_globales**: Agregados diarios

#### Uso:

```python
from database import CentinelaDatabase

db = CentinelaDatabase()

# Guardar un caso
caso_id = db.guardar_caso({
    "rol": "Estudiante",
    "tipo_producto": "Ensayo",
    "riesgo_score": 45,
    "nivel_riesgo": "MEDIO",
    # ...
})

# Recuperar
caso = db.obtener_caso(caso_id)

# Listar con filtros
casos_alto_riesgo = db.listar_casos(filtro_nivel="ALTO", limite=50)

# Estadísticas
stats = db.obtener_estadisticas()
resumen = db.obtener_resumen_institucion()
```

---

### 4. **institutional_metrics.py** - Métricas Institucionales

Genera reportes agregados para decisiones estratégicas:

#### Clases:

**InstitucionalMetrics**
- `calcular_tasa_riesgo()`: Distribución por nivel
- `calcular_por_rol()`: Análisis desagregado por rol
- `calcular_por_producto()`: Análisis desagregado por tipo
- `identificar_patrones()`: Red flags frecuentes y anomalías
- `generar_reporte_ejecutivo()`: Reporte completo para administración
- `comparar_periodos()`: Análisis de cambios entre períodos

**FollowUpMetrics**
- `calcular_evolucion_temporal()`: Tendencias a través del tiempo

#### Uso:

```python
from institutional_metrics import InstitucionalMetrics, FollowUpMetrics

# Reporte ejecutivo
reporte = InstitucionalMetrics.generar_reporte_ejecutivo(casos)

print(reporte["tasas_por_nivel"])          # {"ALTO": 25.0, "MEDIO": 50.0, ...}
print(reporte["metricas_por_rol"])         # Análisis por rol
print(reporte["patrones_detectados"])      # Red flags frecuentes
print(reporte["recomendaciones_estrategicas"])  # Acciones sugeridas

# Evolución temporal
evolucion = FollowUpMetrics.calcular_evolucion_temporal(
    casos_historicos, 
    agrupacion="mensual"
)
```

---

### 5. **test_runner.py** - Suite de Testing

Script ejecutable que prueba todo el flujo:

#### Tests incluidos:

1. ✓ Estructura de casos de prueba
2. ✓ Análisis de cada caso individual
3. ✓ Validación del modelo mejorado
4. ✓ Persistencia en base de datos
5. ✓ Generación de reportes institucionales

#### Ejecución:

```bash
# Ejecutar todos los tests
python test_runner.py

# Con salida verbose
python test_runner.py --verbose
```

---

## 📊 Flujo de Trabajo Mejorado

### Antes (versión anterior):

```
Entrada → Matriz binaria → OpenAI → Reporte PDF
```

### Ahora (versión mejorada):

```
Entrada 
  ↓
Análisis por reglas ponderadas
  ↓
Factores contextuales aplicados
  ↓
OpenAI (análisis de sentimiento + IA)
  ↓
Validación de confianza
  ↓
Recomendaciones automáticas
  ↓
Persistencia en BD
  ↓
Métricas institucionales
  ↓
Reportes PDF + Reportes ejecutivos
```

---

## 🔧 Integración con app.py

Para integrar las mejoras en la aplicación Streamlit existente:

```python
# En app.py, añadir estos imports
from improved_analysis_model import analyze_with_improved_model
from database import db
from institutional_metrics import InstitucionalMetrics

# Reemplazar la lógica de análisis actual con:
resultado_mejorado = analyze_with_improved_model(
    evidencias,
    rol,
    tipo_producto,
    num_evidencias_marked=sum(evidencias.values())
)

# Guardar en BD
db.guardar_caso({
    "rol": rol,
    "tipo_producto": tipo_producto,
    "riesgo_score": resultado_mejorado["overall_score"],
    "nivel_riesgo": resultado_mejorado["overall_level"],
    "confianza": resultado_mejorado["confidence"],
    # ... más datos
})
```

---

## 📈 Evidencia Construida para Versión Institucional

### Datos capturados:

1. **Por caso individual**:
   - Rol del autor
   - Tipo de producto
   - Puntaje de riesgo (0-100)
   - Nivel de riesgo (BAJO/MEDIO/ALTO)
   - Confianza del análisis
   - Red flags detectadas
   - Recomendaciones
   - KPIs de seguimiento

2. **Por institución** (agregados):
   - Distribución de riesgo por período
   - Tendencias por rol
   - Tendencias por tipo de producto
   - Patrones de red flags más frecuentes
   - Anomalías detectadas
   - Recomendaciones estratégicas

### Reportes posibles:

- 📊 Tablero diario de casos
- 📈 Tendencias mensales
- 👥 Análisis por programa académico
- 🎯 Recomendaciones para comité de ética
- 📋 Validación de mejoras tras intervenciones

---

## 🧪 Ejemplo de Ejecución Completa

```python
from test_cases import get_test_case
from improved_analysis_model import analyze_with_improved_model, validate_analysis
from database import db
from institutional_metrics import InstitucionalMetrics

# 1. Obtener caso de prueba
caso = get_test_case("caso_alto_riesgo")

# 2. Analizar con modelo mejorado
resultado = analyze_with_improved_model(
    caso["evidencias"],
    caso["rol"],
    caso["tipo_producto"],
)

# 3. Validar
validacion = validate_analysis(resultado, expected_level=caso["expected_risk_level"])
print(f"Válido: {validacion['is_valid']}")

# 4. Guardar en BD
caso_id = db.guardar_caso({
    "rol": caso["rol"],
    "tipo_producto": caso["tipo_producto"],
    "riesgo_score": resultado["overall_score"],
    "nivel_riesgo": resultado["overall_level"],
    "confianza": resultado["confidence"],
})

# 5. Generar métricas
todos_casos = db.listar_casos(limite=100)
reporte = InstitucionalMetrics.generar_reporte_ejecutivo(todos_casos)

print(f"Casos analizados: {reporte['resumen_general']['total_casos_analizados']}")
print(f"Tasa de riesgo: {reporte['tasas_por_nivel']}")
print(f"Recomendaciones: {reporte['recomendaciones_estrategicas']}")
```

---

## 📝 Requisitos Adicionales

Si usas las nuevas características, actualiza `requirements.txt`:

```bash
pip install sqlite3  # Usualmente ya incluido en Python
```

---

## ✅ Checklist de Validación

- [x] 5 casos de prueba con diferentes niveles de riesgo
- [x] Modelo de análisis con pesos ponderados
- [x] Factores contextuales por rol y producto
- [x] Persistencia completa en base de datos
- [x] Métricas agregadas para análisis institucional
- [x] Suite completa de tests automatizados
- [x] Documentación de integración
- [x] Ejemplos de uso

---

## 🔮 Próximas Fases Sugeridas

1. **Fase 2**: Integración con Streamlit UI
2. **Fase 3**: Paneles comparativos por programa/cohorte
3. **Fase 4**: API REST para integración institucional
4. **Fase 5**: Machine learning para mejora continua del modelo
5. **Fase 6**: Integración con sistemas de gestión académica

---

**Versión**: 2.0  
**Fecha**: Enero 2026  
**Autor**: Prof. Anderson Díaz Pérez (Centinela Digital)  
**Estado**: Listo para testing e integración
