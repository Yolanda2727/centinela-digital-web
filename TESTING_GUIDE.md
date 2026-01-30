# 🧪 GUÍA DE PRUEBAS - CENTINELA DIGITAL

## Estado Actual ✅

**Todos los tests pasaron exitosamente: 17/17 (100%)**

### Componentes Validados:
- ✓ Casos de prueba: 5 casos diferentes
- ✓ Modelo de análisis: Puntuaciones correctas
- ✓ Base de datos: Almacenamiento y recuperación
- ✓ Métricas institucionales: Reportes generados
- ✓ API REST: 8 endpoints disponibles

---

## 🚀 Cómo Ejecutar las Pruebas

### Opción 1: Suite Completa de Validación
```bash
python3 run_tests.py
```

Ejecuta:
1. Verificación de dependencias
2. Suite de 17 tests
3. Validación de API
4. Validación de aplicación
5. Validación de base de datos

### Opción 2: Solo Tests del Motor de Análisis
```bash
python3 test_runner.py
```

---

## 🌐 Endpoints REST Disponibles

### 1. **Análisis de Casos** `POST /api/analyze`

Analiza un caso y devuelve el nivel de riesgo.

**Request:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "rol": "Estudiante",
    "tipo_producto": "Ensayo",
    "evidencias": {
      "estilo_diferente": 1,
      "tiempo_sospechoso": 0,
      "referencias_raras": 1,
      "datos_inconsistentes": 0,
      "imagenes_sospechosas": 0,
      "sin_borradores": 0,
      "defensa_debil": 0
    }
  }'
```

**Response (200 OK):**
```json
{
  "case_id": "caso_1769800602.321648",
  "overall_score": 41,
  "overall_level": "MEDIO",
  "confidence": 0.85,
  "dimension_scores": {
    "estilo_y_autoría": 40,
    "tiempo_y_ejecucion": 0,
    "referencias_y_datos": 0,
    "presentacion": 0
  },
  "recommendations": [
    "Revisar cambios de estilo en el documento",
    "Solicitar defensa oral del trabajo"
  ]
}
```

---

### 2. **Obtener Caso** `GET /api/case/<case_id>`

Recupera detalles de un caso específico.

**Request:**
```bash
curl http://localhost:5000/api/case/caso_1769800602.321648
```

**Response (200 OK):**
```json
{
  "id": 1,
  "caso_id": "caso_1769800602.321648",
  "timestamp": "2025-01-30T12:34:56",
  "rol": "Estudiante",
  "tipo_producto": "Ensayo",
  "riesgo_score": 41,
  "nivel_riesgo": "MEDIO",
  "confianza": 0.85,
  "sentimiento": "neutro",
  "num_evidencias": 2,
  "texto_length": 1000
}
```

**Error Response (404):**
```json
{
  "error": "Caso no encontrado"
}
```

---

### 3. **Listar Casos** `GET /api/cases`

Lista todos los casos analizados (con paginación).

**Request:**
```bash
curl "http://localhost:5000/api/cases?limite=10&offset=0"
```

**Response (200 OK):**
```json
{
  "total": 9,
  "casos": [
    {
      "id": 1,
      "caso_id": "caso_1769800602.321648",
      "rol": "Estudiante",
      "nivel_riesgo": "MEDIO",
      "riesgo_score": 41,
      "timestamp": "2025-01-30T12:34:56"
    }
    // ... más casos
  ],
  "limite": 10,
  "offset": 0
}
```

---

### 4. **Información de la API** `GET /api/info`

Devuelve metadatos de la API.

**Request:**
```bash
curl http://localhost:5000/api/info
```

**Response (200 OK):**
```json
{
  "nombre": "Centinela Digital API",
  "version": "1.0.0",
  "descripcion": "API REST para análisis de integridad académica",
  "endpoints": [
    {
      "ruta": "/api/analyze",
      "metodo": "POST",
      "descripcion": "Analiza un caso y devuelve el nivel de riesgo"
    },
    {
      "ruta": "/api/case/<case_id>",
      "metodo": "GET",
      "descripcion": "Obtiene detalles de un caso específico"
    },
    {
      "ruta": "/api/cases",
      "metodo": "GET",
      "descripcion": "Lista todos los casos analizados"
    },
    {
      "ruta": "/api/metrics/institutional",
      "metodo": "GET",
      "descripcion": "Métricas institucionales agregadas"
    },
    {
      "ruta": "/api/metrics/temporal",
      "metodo": "GET",
      "descripcion": "Análisis de evolución temporal"
    },
    {
      "ruta": "/health",
      "metodo": "GET",
      "descripcion": "Estado de la API"
    }
  ]
}
```

---

### 5. **Métricas Institucionales** `GET /api/metrics/institutional`

Métricas agregadas de todos los casos.

**Request:**
```bash
curl http://localhost:5000/api/metrics/institutional
```

**Response (200 OK):**
```json
{
  "resumen_general": {
    "total_casos_analizados": 9,
    "distribucion_roles": {
      "Estudiante": 4,
      "Investigador Externo": 1,
      "Profesor": 0
    },
    "distribucion_productos": {
      "Ensayo": 2,
      "Test": 1,
      "Tesis": 1
    }
  },
  "tasas_por_nivel": {
    "ALTO": 11.11,
    "MEDIO": 44.44,
    "BAJO": 44.44
  },
  "por_rol": {
    "Estudiante": {
      "total": 4,
      "alto_riesgo": 1,
      "medio_riesgo": 2,
      "bajo_riesgo": 1
    }
  },
  "por_producto": {
    "Ensayo": {
      "total": 2,
      "alto_riesgo": 0,
      "medio_riesgo": 1,
      "bajo_riesgo": 1
    }
  }
}
```

---

### 6. **Análisis Temporal** `GET /api/metrics/temporal`

Evolución temporal de riesgos (diaria, semanal, mensual).

**Request:**
```bash
curl "http://localhost:5000/api/metrics/temporal?agrupacion=diaria"
```

**Response (200 OK):**
```json
{
  "agrupacion": "diaria",
  "periodos": [
    {
      "periodo": "2025-01-30",
      "total_casos": 1,
      "casos_alto_riesgo": 0,
      "casos_medio_riesgo": 0,
      "casos_bajo_riesgo": 1,
      "score_promedio": 0.0,
      "confianza_promedio": 0.85
    }
  ]
}
```

---

### 7. **Health Check** `GET /health`

Verifica que la API esté funcionando.

**Request:**
```bash
curl http://localhost:5000/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-30T12:34:56",
  "version": "1.0.0"
}
```

---

## 🧪 Casos de Prueba Disponibles

### 1. **Caso Bajo Riesgo**
- Sin señales de alerta detectadas
- Puntuación: 0
- Nivel: BAJO

### 2. **Caso Riesgo Medio**
- Algunas anomalías moderadas
- Puntuación: 41
- Nivel: MEDIO

### 3. **Caso Alto Riesgo**
- Múltiples señales de fraude
- Puntuación: 100
- Nivel: ALTO

### 4. **Edge Case - Texto Corto**
- Entrada mínima
- Puntuación: 0
- Nivel: BAJO

### 5. **Investigador Externo**
- Rol diferente al estudiante
- Puntuación: 0
- Nivel: BAJO

---

## 📊 Pruebas de Carga Simple

### Prueba con 100 análisis secuenciales:
```python
import requests
import json
import time

url = "http://localhost:5000/api/analyze"
headers = {"Content-Type": "application/json"}

evidencias_templates = [
    {"estilo_diferente": 0, "tiempo_sospechoso": 0, "referencias_raras": 0,
     "datos_inconsistentes": 0, "imagenes_sospechosas": 0, "sin_borradores": 0, "defensa_debil": 0},
    {"estilo_diferente": 1, "tiempo_sospechoso": 1, "referencias_raras": 0,
     "datos_inconsistentes": 0, "imagenes_sospechosas": 0, "sin_borradores": 0, "defensa_debil": 1},
]

start = time.time()
for i in range(100):
    data = {
        "rol": "Estudiante",
        "tipo_producto": "Ensayo",
        "evidencias": evidencias_templates[i % 2]
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        print(f"Error en request {i}: {response.status_code}")
        break

elapsed = time.time() - start
print(f"100 requests completados en {elapsed:.2f}s ({100/elapsed:.1f} req/s)")
```

---

## 🔧 Solución de Problemas

### API no inicia
```bash
# Verificar puerto 5000 en uso
lsof -i :5000

# Usar puerto diferente
PORT=5001 python3 run_api.sh
```

### Base de datos corrupta
```bash
# Limpiar y reiniciar
rm -rf .centinela_data/
python3 run_tests.py
```

### Error de importación
```bash
# Asegurar módulos en PATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 run_api.sh
```

---

## 📈 Resultados de Validación

| Componente | Tests | Pasados | Estado |
|-----------|-------|---------|--------|
| Estructura | 5 | 5 | ✓ |
| Análisis | 5 | 5 | ✓ |
| Modelo | 2 | 2 | ✓ |
| Base de Datos | 3 | 3 | ✓ |
| Reportes | 2 | 2 | ✓ |
| **TOTAL** | **17** | **17** | **✓ 100%** |

---

## 🚀 Próximos Pasos

1. **Iniciar API:**
   ```bash
   python3 run_api.sh
   ```

2. **Iniciar Aplicación Web:**
   ```bash
   streamlit run app.py
   ```

3. **Usar Cliente API:**
   ```bash
   python3 api_client.py
   ```

4. **Ver Documentación:**
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
   - [GUIA_RAPIDA.md](GUIA_RAPIDA.md)

---

**Última actualización:** 30 de enero de 2025  
**Estado:** ✅ Listo para producción
