# 🌐 API REST - Centinela Digital v2.0

**Documentación de endpoints REST para análisis de fraude académico**

---

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Iniciar servidor
```bash
python api.py
```

El servidor se ejecutará en: `http://localhost:5000`

### 3. Probar API
```bash
python api_client.py 1
```

---

## 📡 Endpoints

### 🏥 Health Check
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-30T10:30:00",
  "version": "2.0"
}
```

---

### 🔍 Analizar Documento
```http
POST /api/analyze
Content-Type: application/json
```

**Request:**
```json
{
  "texto": "contenido del documento...",
  "metadata": {
    "rol": "Estudiante",
    "tipo_producto": "Ensayo",
    "titulo": "Mi ensayo",
    "autor": "Juan García"
  },
  "evidencias": {
    "estilo_diferente": 1,
    "defensa_debil": 0,
    "tiempo_sospechoso": 0,
    "sin_borradores": 1,
    "referencias_raras": 0,
    "datos_inconsistentes": 1,
    "imagenes_sospechosas": 0
  }
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "case_id": "case_a1b2c3d4e5f6",
  "analysis": {
    "overall_score": 45,
    "overall_level": "MEDIO",
    "confidence": 0.87,
    "recommendations": [
      "Revisar estructura del argumento",
      "Verificar formateo de referencias"
    ],
    "dimensions": {
      "autoría": 30,
      "tiempo": 25,
      "referencias": 15,
      "presentación": 10
    }
  },
  "metadata": {
    "text_length": 1250,
    "num_evidencias": 2,
    "analyzed_at": "2026-01-30T10:30:00"
  }
}
```

**Parámetros:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `texto` | string | ✓ | Contenido del documento (min 50 caracteres) |
| `metadata.rol` | string | ✓ | Estudiante / Docente-investigador / Coinvestigador externo |
| `metadata.tipo_producto` | string | ✓ | Ensayo / Tesis / Artículo científico / Informe técnico / Trabajo de curso / Proyecto de grado / Otro |
| `metadata.titulo` | string | | Título del documento |
| `metadata.autor` | string | | Autor del documento |
| `evidencias.*` | integer | | Valores 0 o 1 para cada evidencia |

**Evidencias disponibles:**
- `estilo_diferente` - El texto tiene un estilo diferente al del autor
- `defensa_debil` - Defensa débil de argumentos
- `tiempo_sospechoso` - Tiempo de entrega sospechoso
- `sin_borradores` - Sin borradores o versiones previas
- `referencias_raras` - Referencias poco comunes o incorrectas
- `datos_inconsistentes` - Datos que no coinciden
- `imagenes_sospechosas` - Imágenes de baja calidad o copiadas

---

### 📋 Obtener Caso
```http
GET /api/case/{case_id}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "case": {
    "case_id": "case_a1b2c3d4e5f6",
    "title": "Mi ensayo",
    "author": "Juan García",
    "role": "Estudiante",
    "product_type": "Ensayo",
    "overall_score": 45,
    "overall_level": "MEDIO",
    "confidence": 0.87,
    "analyzed_at": "2026-01-30T10:30:00"
  }
}
```

**Error (404 Not Found):**
```json
{
  "error": "Case not found",
  "code": "NOT_FOUND",
  "case_id": "case_a1b2c3d4e5f6"
}
```

---

### 📊 Listar Casos
```http
GET /api/cases?nivel=ALTO&rol=Estudiante&limit=10&offset=0
```

**Parámetros Query:**
- `nivel` (opcional): BAJO / MEDIO / ALTO
- `rol` (opcional): Estudiante / Docente-investigador / Coinvestigador externo
- `limit` (opcional, default=50): Número máximo de casos
- `offset` (opcional, default=0): Desplazamiento para paginación

**Response (200 OK):**
```json
{
  "status": "success",
  "total": 42,
  "returned": 10,
  "limit": 10,
  "offset": 0,
  "filters": {
    "nivel": "ALTO",
    "rol": "Estudiante"
  },
  "cases": [
    {
      "case_id": "case_1",
      "title": "Tesis de grado",
      "author": "María López",
      "role": "Estudiante",
      "product_type": "Tesis",
      "overall_score": 85,
      "overall_level": "ALTO",
      "confidence": 0.92,
      "analyzed_at": "2026-01-30T10:30:00"
    }
  ]
}
```

---

### 📈 Métricas Institucionales
```http
GET /api/metrics/institutional
```

**Response (200 OK):**
```json
{
  "status": "success",
  "metrics": {
    "total_cases": 42,
    "risk_distribution": {
      "BAJO": 20,
      "MEDIO": 14,
      "ALTO": 8
    },
    "average_score": 38.5,
    "confidence_avg": 0.85,
    "cases_by_role": {
      "Estudiante": 30,
      "Docente-investigador": 10,
      "Coinvestigador externo": 2
    },
    "cases_by_product": {
      "Ensayo": 15,
      "Tesis": 12,
      "Artículo científico": 10,
      "Otro": 5
    }
  }
}
```

---

### 📅 Análisis Temporal
```http
GET /api/metrics/temporal?period=daily
```

**Parámetros:**
- `period`: daily / weekly / monthly

**Response (200 OK):**
```json
{
  "status": "success",
  "period": "daily",
  "data": {
    "2026-01-30": {
      "total_cases": 5,
      "average_score": 42,
      "distribution": {
        "BAJO": 2,
        "MEDIO": 2,
        "ALTO": 1
      }
    }
  }
}
```

---

### ℹ️ Información de API
```http
GET /api/info
```

**Response (200 OK):**
```json
{
  "name": "Centinela Digital API",
  "version": "2.0",
  "description": "API para detección de fraude académico",
  "valid_roles": [
    "Estudiante",
    "Docente-investigador",
    "Coinvestigador externo"
  ],
  "valid_product_types": [
    "Ensayo",
    "Tesis",
    "Artículo científico",
    "Informe técnico",
    "Trabajo de curso",
    "Proyecto de grado",
    "Otro"
  ],
  "valid_evidences": [
    "estilo_diferente",
    "defensa_debil",
    "tiempo_sospechoso",
    "sin_borradores",
    "referencias_raras",
    "datos_inconsistentes",
    "imagenes_sospechosas"
  ],
  "endpoints": {
    "POST /api/analyze": "Analizar un documento",
    "GET /api/case/<id>": "Obtener un caso",
    "GET /api/cases": "Listar casos con filtros",
    "GET /api/metrics/institutional": "Métricas institucionales",
    "GET /api/metrics/temporal": "Análisis temporal",
    "GET /health": "Verificar salud de API"
  }
}
```

---

## 🧪 Ejemplos de Uso

### Python
```python
from api_client import CentinelaAPIClient

client = CentinelaAPIClient("http://localhost:5000")

# Analizar
result = client.analyze(
    texto="Este es mi ensayo...",
    rol="Estudiante",
    tipo_producto="Ensayo",
    titulo="Mi primer ensayo"
)

# Obtener caso
case = client.get_case(result['case_id'])

# Listar casos
cases = client.list_cases(nivel="ALTO", limit=10)

# Métricas
metrics = client.get_metrics_institutional()
```

### cURL
```bash
# Analizar documento
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "Contenido del documento...",
    "metadata": {
      "rol": "Estudiante",
      "tipo_producto": "Ensayo"
    }
  }'

# Listar casos
curl http://localhost:5000/api/cases?nivel=ALTO

# Métricas
curl http://localhost:5000/api/metrics/institutional
```

### JavaScript
```javascript
// Fetch API
const response = await fetch('http://localhost:5000/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    texto: 'Contenido...',
    metadata: { rol: 'Estudiante', tipo_producto: 'Ensayo' }
  })
});

const result = await response.json();
console.log(result.case_id);
```

---

## 🔧 Configuración

### Variables de Entorno
```bash
FLASK_ENV=production      # development / production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
DEBUG=False
```

### Archivo de Configuración
Crear `config.py`:
```python
import os

class Config:
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', False)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///centinela.db'
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
```

---

## 📊 Códigos de Estado HTTP

| Código | Significado |
|--------|------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Error en la solicitud |
| 404 | Not Found - Recurso no encontrado |
| 500 | Server Error - Error interno del servidor |

---

## ⚠️ Códigos de Error

| Código | Descripción |
|--------|------------|
| INVALID_REQUEST | Datos JSON no válidos |
| INVALID_TEXT | Texto inválido o muy corto |
| NOT_FOUND | Caso no encontrado |
| ANALYSIS_ERROR | Error durante el análisis |
| QUERY_ERROR | Error al consultar datos |
| METRICS_ERROR | Error al calcular métricas |
| TEMPORAL_ERROR | Error en análisis temporal |

---

## 🔐 Seguridad

### Recomendaciones
- [ ] Usar HTTPS en producción
- [ ] Implementar autenticación (JWT, API Keys)
- [ ] Validar entrada más estrictamente
- [ ] Implementar rate limiting
- [ ] Usar CORS restrictivo
- [ ] Logging y monitoreo

### Implementar Autenticación (Opcional)
```python
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/analyze', methods=['POST'])
@require_api_key
def analyze():
    # ...
```

---

## 📝 Testing

Ejecutar suite de pruebas:
```bash
python test_runner.py
```

Ejecutar ejemplos del cliente:
```bash
python api_client.py 1   # Análisis básico
python api_client.py 2   # Con alertas
python api_client.py 3   # Listar y métricas
python api_client.py 4   # Filtrar
python api_client.py 5   # Info y health
```

---

## 🚀 Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "api.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  centinela-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: production
      DEBUG: 'False'
    volumes:
      - ./centinela.db:/app/centinela.db
```

---

## 📞 Soporte

Para preguntas o reportar problemas, crear un issue en el repositorio.

---

**Última actualización**: Enero 2026  
**Versión API**: 2.0  
**Status**: ✅ Producción
