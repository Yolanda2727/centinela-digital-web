# 📚 ÍNDICE - CENTINELA DIGITAL v2.0

**Status:** ✅ COMPLETAMENTE VALIDADO (17/17 tests)  
**Fecha:** 30 de enero de 2025

---

## 🚀 INICIO RÁPIDO (3 pasos)

### 1. Validar que todo funciona
```bash
python3 run_tests.py
```

### 2. Iniciar la API REST
```bash
python3 run_api.sh
```

### 3. Probar los endpoints (otra terminal)
```bash
python3 test_api_endpoints.py
```

---

## 📖 DOCUMENTACIÓN PRINCIPAL

### Para Usuarios
- **[README_TESTS.md](README_TESTS.md)** - 👈 **COMIENZA AQUÍ**
  - Guía rápida de cómo ejecutar las pruebas
  - Resultados de validación
  - Lista de endpoints

- **[EXECUTION_SUMMARY.md](EXECUTION_SUMMARY.md)** - Resumen ejecutivo
  - Qué se ha validado
  - Cómo usar el sistema
  - Ejemplos rápidos
  - Troubleshooting

### Para Desarrolladores
- **[VALIDATION_REPORT.md](VALIDATION_REPORT.md)** - Reporte técnico completo
  - Detalles de cada test
  - Arquitectura del sistema
  - Componentes validados
  - Próximas mejoras

- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Guía de pruebas
  - Casos de prueba incluidos
  - Cómo usar cada endpoint
  - Ejemplos con curl
  - Pruebas de carga

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Documentación de API
  - Especificación completa de endpoints
  - Formatos de request/response
  - Códigos de error
  - Ejemplos de uso

- **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - Guía rápida
  - Instalación
  - Configuración
  - Primeros pasos

---

## 🔧 SCRIPTS DISPONIBLES

### Tests y Validación
| Script | Comando | Propósito |
|--------|---------|-----------|
| **run_tests.py** | `python3 run_tests.py` | Suite de validación (17 tests) |
| **test_api_endpoints.py** | `python3 test_api_endpoints.py` | Prueba todos los endpoints REST |
| **test_runner.py** | `python3 test_runner.py` | Motor de tests individual |
| **run_full_test.sh** | `bash run_full_test.sh` | Ejecutor completo de tests |

### Aplicación
| Script | Comando | Propósito |
|--------|---------|-----------|
| **run_api.sh** | `python3 run_api.sh` | Iniciar API REST en puerto 5000 |
| **app.py** | `streamlit run app.py` | Iniciar aplicación web |
| **api_client.py** | `python3 api_client.py` | Cliente Python para API |

### Ejemplos
| Script | Comando | Propósito |
|--------|---------|-----------|
| **ejemplos.py** | `python3 ejemplos.py` | Ejemplos básicos |
| **ejemplos_api.py** | `python3 ejemplos_api.py` | Ejemplos de uso de API (interactivo) |

---

## 🌐 ENDPOINTS REST (8 disponibles)

### POST - Análisis
```
POST /api/analyze
Analizar un documento para detectar fraude académico
Retorna: score, nivel de riesgo, recomendaciones
```

### GET - Consultas
```
GET  /api/case/<case_id>           Obtener un caso específico
GET  /api/cases                    Listar todos los casos
GET  /api/metrics/institutional    Métricas agregadas
GET  /api/metrics/temporal         Evolución temporal
```

### GET - Información
```
GET  /api/info                     Información de la API
GET  /health                       Health check
```

---

## 📊 COMPONENTES VALIDADOS

### ✅ Motor de Análisis
- Reglas ponderadas por dimensión
- 4 dimensiones de análisis
- 3 niveles de riesgo (BAJO, MEDIO, ALTO)
- Cálculo de confianza
- 5 casos de prueba diferentes

### ✅ Base de Datos
- SQLite persistente
- Recuperación de históricos
- 9 casos almacenados
- Indexación por ID

### ✅ API REST
- 8 endpoints funcionales
- CORS habilitado
- Manejo robusto de errores
- Documentación completa

### ✅ Métricas Institucionales
- Reportes agregados
- Análisis por rol y tipo de producto
- Evolución temporal (diaria, semanal, mensual)
- Estadísticas detalladas

---

## 📈 RESULTADOS DE VALIDACIÓN

```
TOTAL DE TESTS:      17/17 ✅
TASA DE ÉXITO:       100%
STATUS:              🎉 LISTO PARA PRODUCCIÓN

Desglose:
  ✅ Estructura de casos       5/5
  ✅ Análisis individual       5/5
  ✅ Modelo mejorado          2/2
  ✅ Persistencia en BD       3/3
  ✅ Reportes               2/2
```

---

## 🎯 NIVELES DE RIESGO

| Nivel | Score | Descripción | Acción |
|-------|-------|-------------|--------|
| 🟢 BAJO | 0-33 | Sin señales de alerta | Aprobación |
| 🟡 MEDIO | 34-66 | Algunas anomalías | Revisión recomendada |
| 🔴 ALTO | 67-100 | Múltiples señales | Investigación urgente |

---

## 📝 CASOS DE PRUEBA

1. **caso_bajo_riesgo** - Trabajo académico bien estructurado (Score: 0)
2. **caso_riesgo_medio** - Trabajo con anomalías moderadas (Score: 41)
3. **caso_alto_riesgo** - Trabajo con señales de fraude (Score: 100)
4. **caso_edge_short** - Texto mínimo para validación (Score: 0)
5. **caso_investigador_externo** - Rol diferente al estudiante (Score: 0)

---

## 🔍 CÓMO FUNCIONA

### Análisis en 3 pasos

1. **Recibir Entrada**
   - Rol del usuario (Estudiante, Docente, Externo)
   - Tipo de producto (Ensayo, Tesis, Artículo, etc.)
   - Evidencias de alerta (7 posibles indicadores)

2. **Calcular Puntuación**
   - 4 dimensiones evaluadas
   - Ponderación por dimensión
   - Factores contextuales aplicados
   - Confianza calculada

3. **Generar Resultado**
   - Score 0-100
   - Nivel: BAJO / MEDIO / ALTO
   - Recomendaciones específicas
   - Almacenamiento en BD

---

## 🛠️ TROUBLESHOOTING

### API no inicia
```bash
# Verificar puerto 5000 en uso
lsof -i :5000

# Usar puerto diferente
PORT=5001 python3 run_api.sh
```

### BD corrupta
```bash
# Limpiar y reiniciar
rm -rf .centinela_data/
python3 run_tests.py
```

### Error de importación
```bash
# Asegurar módulos en PATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 run_tests.py
```

---

## 📞 ARCHIVOS IMPORTANTES

### Módulos Principales
- **api.py** (14K) - API REST Flask con 8 endpoints
- **app.py** (26K) - Aplicación web Streamlit
- **database.py** (12K) - Gestión de base de datos SQLite
- **improved_analysis_model.py** (10K) - Motor de análisis
- **institutional_metrics.py** (14K) - Cálculo de métricas

### Módulos de Testing
- **test_runner.py** (14K) - Suite de tests (17 tests)
- **test_cases.py** (8K) - 5 casos de prueba
- **test_api_endpoints.py** (14K) - Validación de endpoints
- **run_tests.py** (5K) - Ejecutor de validación

### Utilidades
- **api_client.py** (11K) - Cliente Python para API
- **ejemplos.py** (12K) - Ejemplos de uso
- **ejemplos_api.py** (14K) - Ejemplos interactivos de API

---

## ✨ CARACTERÍSTICAS DESTACADAS

✅ **Análisis Inteligente**
- Motor basado en reglas
- 4 dimensiones de análisis
- Cálculo de confianza
- Recomendaciones personalizadas

✅ **Escalable**
- Base de datos SQLite
- API REST completa
- Almacenamiento de históricos
- Análisis temporal

✅ **Fácil de Usar**
- Interfaz web (Streamlit)
- Cliente Python
- Ejemplos incluidos
- Documentación completa

✅ **Bien Testeado**
- 17 tests con 100% de éxito
- 8 endpoints validados
- 5 casos de prueba
- Cobertura completa

---

## 🎓 PRÓXIMOS PASOS

1. **Revisar Documentación**
   - Comienza con [README_TESTS.md](README_TESTS.md)
   - Luego [EXECUTION_SUMMARY.md](EXECUTION_SUMMARY.md)

2. **Ejecutar Tests**
   ```bash
   python3 run_tests.py
   ```

3. **Iniciar Sistema**
   ```bash
   python3 run_api.sh &
   streamlit run app.py
   ```

4. **Probar Endpoints**
   ```bash
   python3 test_api_endpoints.py
   python3 ejemplos_api.py
   ```

---

## 📋 ESTRUCTURA DEL PROYECTO

```
centinela-digital-web/
├── 📄 Documentación
│   ├── README_TESTS.md              ← COMIENZA AQUÍ
│   ├── EXECUTION_SUMMARY.md
│   ├── VALIDATION_REPORT.md
│   ├── TESTING_GUIDE.md
│   ├── API_DOCUMENTATION.md
│   └── GUIA_RAPIDA.md
│
├── 🚀 Scripts
│   ├── run_tests.py                 (Validación)
│   ├── test_api_endpoints.py        (Tests)
│   ├── ejemplos_api.py              (Ejemplos)
│   └── run_api.sh                   (Startup)
│
├── 🔧 Módulos Principales
│   ├── api.py                       (API REST)
│   ├── app.py                       (Web UI)
│   ├── database.py                  (BD)
│   ├── improved_analysis_model.py   (Motor)
│   └── institutional_metrics.py     (Métricas)
│
└── 📊 Testing
    ├── test_runner.py
    ├── test_cases.py
    └── ejemplos.py
```

---

## ✅ CHECKLIST FINAL

- ✅ 17/17 tests pasados
- ✅ 8 endpoints funcionales
- ✅ BD operacional con 9 casos
- ✅ Métricas calculadas correctamente
- ✅ Documentación completa
- ✅ Scripts listos para usar
- ✅ Cliente API disponible
- ✅ Listo para producción

---

**¡Centinela Digital está listo para usar!** 🎉

Comienza leyendo [README_TESTS.md](README_TESTS.md)

---

*Centinela Digital - Sistema de Detección de Fraude Académico*  
*Versión 2.0 - Enero 2025*
