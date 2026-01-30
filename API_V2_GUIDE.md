# 🚀 API v2.1 - MEJORAS IMPLEMENTADAS

**Fecha:** 30 de enero de 2026  
**Versión:** 2.1  
**Estado:** ✅ Completamente Integrada

---

## 📋 Resumen de Mejoras

### ✅ 1. Autenticación JWT
- Login seguro con tokens JWT
- Registro de nuevos usuarios
- Tokens con expiración de 24 horas
- Protección de endpoints con decorador `@token_required`

### ✅ 2. Swagger/OpenAPI Documentation
- Documentación automática en `/apidocs`
- Especificación OpenAPI 2.0
- Pruebas interactivas de endpoints

### ✅ 3. Nuevos Endpoints
- `POST /api/batch/analyze` - Análisis en lote de múltiples documentos
- `POST /api/auth/login` - Obtener token JWT
- `POST /api/auth/register` - Registrar usuario
- `GET /api/documentation` - Especificación OpenAPI

### ✅ 4. Clientes de Ejemplo
- **Cliente React** - Interfaz web moderna
- **Cliente Python v2** - Herramienta mejorada con lotes

### ✅ 5. Mejoras Técnicas
- Headers de autenticación en todos los endpoints
- Manejo robusto de errores
- Documentación completa con docstrings

---

## 🔐 AUTENTICACIÓN

### Login

**Endpoint:** `POST /api/auth/login`

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Respuesta:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "usuario": "admin",
  "mensaje": "Login exitoso"
}
```

### Usar Token en Requests

Todos los endpoints protegidos requieren el header:

```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Registro (Demo)

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevouser",
    "password": "pass123",
    "email": "user@example.com"
  }'
```

---

## 📦 ANÁLISIS EN LOTE

### POST /api/batch/analyze

Analizar múltiples documentos en una sola petición.

```bash
curl -X POST http://localhost:5000/api/batch/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "casos": [
      {
        "rol": "Estudiante",
        "tipo_producto": "Ensayo",
        "evidencias": {
          "estilo_diferente": 1,
          "referencias_raras": 0
        }
      },
      {
        "rol": "Estudiante",
        "tipo_producto": "Tesis",
        "evidencias": {
          "estilo_diferente": 0,
          "referencias_raras": 1
        }
      }
    ]
  }'
```

**Respuesta:**
```json
{
  "status": "success",
  "total": 2,
  "procesados": 2,
  "resultados": [
    {
      "status": "success",
      "score": 41,
      "level": "MEDIO"
    },
    {
      "status": "success",
      "score": 40,
      "level": "MEDIO"
    }
  ]
}
```

---

## 🎨 CLIENTE REACT

### Instalación

```bash
npx create-react-app centinela-app
cd centinela-app
npm install axios react-router-dom

# Copiar cliente_react.jsx a src/App.js
cp cliente_react.jsx src/App.js

npm start
```

### Características

- Login con credenciales
- Formulario interactivo de análisis
- Selección de evidencias con checkboxes
- Resultado con código de color según riesgo
- Responsive design

### Flujo de Uso

1. **Login:** admin / admin123
2. **Formulario:** Seleccionar rol, tipo, evidencias
3. **Análisis:** Click en botón "Analizar"
4. **Resultado:** Visualizar score, nivel, recomendaciones

---

## 🐍 CLIENTE PYTHON v2

### Instalación

```bash
pip install requests PyJWT
python cliente_python_v2.py
```

### Uso Básico

```python
from cliente_python_v2 import CentinelaAPIClient

# Inicializar cliente
client = CentinelaAPIClient()

# Login
client.login('admin', 'admin123')

# Análisis simple
resultado = client.analyze(
    rol="Estudiante",
    tipo_producto="Ensayo",
    evidencias={
        'estilo_diferente': 1,
        'referencias_raras': 1
    }
)
print(resultado['analysis']['overall_level'])

# Análisis en lote
casos = [
    {'rol': 'Estudiante', 'tipo_producto': 'Ensayo', 'evidencias': {...}},
    {'rol': 'Estudiante', 'tipo_producto': 'Tesis', 'evidencias': {...}},
]
batch_resultado = client.batch_analyze(casos)

# Métricas
metricas = client.get_metrics()
print(metricas['resumen_general']['total_casos_analizados'])
```

### Métodos Disponibles

```python
# Autenticación
client.login(username, password)
client.register(username, password, email)

# Análisis
client.analyze(rol, tipo_producto, evidencias)
client.batch_analyze(casos)

# Consultas
client.get_case(case_id)
client.list_cases(limit, offset)

# Métricas
client.get_metrics()
client.get_temporal(period)

# Info
client.get_info()
client.health_check()
```

---

## 📚 DOCUMENTACIÓN INTERACTIVA

### Swagger UI

Acceder a: http://localhost:5000/apidocs

Características:
- Lista completa de endpoints
- Esquemas de request/response
- Pruebas interactivas
- Autenticación integrada

---

## 🗄️ LISTA COMPLETA DE ENDPOINTS

### Autenticación (No requiere token)
```
POST   /api/auth/login              Obtener token
POST   /api/auth/register           Registrar usuario
```

### Análisis (Requiere token)
```
POST   /api/analyze                 Analizar documento
POST   /api/batch/analyze           Analizar múltiples
GET    /api/case/<case_id>          Obtener caso
GET    /api/cases                   Listar casos
```

### Métricas (Requiere token)
```
GET    /api/metrics/institutional   Métricas agregadas
GET    /api/metrics/temporal        Evolución temporal
```

### Información
```
GET    /api/info                    Información API
GET    /api/documentation           Especificación OpenAPI
GET    /health                      Health check
GET    /apidocs                     Swagger UI
```

---

## 🚀 CÓMO USAR API v2.1

### Paso 1: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 2: Iniciar API v2.1

```bash
# Opción A: API mejorada (recomendado)
python3 api_v2.py

# Opción B: API original
python3 run_api.sh
```

### Paso 3: Autenticarse

```bash
# Obtener token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.token')

echo $TOKEN
```

### Paso 4: Usar Endpoints Protegidos

```bash
# Analizar con token
curl -X POST http://localhost:5000/api/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'

# Ver documentación
# http://localhost:5000/apidocs
```

---

## 📊 COMPARATIVA: API v1 vs v2.1

| Característica | v1 | v2.1 |
|---|---|---|
| **Autenticación** | ❌ | ✅ JWT |
| **Swagger/OpenAPI** | ❌ | ✅ Automático |
| **Análisis en lote** | ❌ | ✅ Batch API |
| **Endpoints** | 7 | 11 |
| **Cliente React** | ❌ | ✅ Incluido |
| **Cliente Python** | ✅ | ✅ Mejorado |
| **Documentación** | ✅ | ✅ + Interactiva |

---

## 🔧 CONFIGURACIÓN EN PRODUCCIÓN

### 1. Cambiar Secret Key

En `api_v2.py`:
```python
app.config['SECRET_KEY'] = 'tu-clave-segura-aleatoria'
```

### 2. Base de Datos de Usuarios

Reemplazar `DEMO_USERS` con BD real:
```python
# En producción usar:
# - PostgreSQL / MongoDB
# - Hash bcrypt para contraseñas
# - Roles y permisos
```

### 3. HTTPS

```python
# Usar gunicorn con SSL
gunicorn --certfile=cert.pem --keyfile=key.pem api_v2:app
```

### 4. Rate Limiting

```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10/minute")
def analyze():
    ...
```

---

## 📈 EJEMPLOS COMPLETOS

### Ejemplo 1: Flujo Completo en Python

```python
from cliente_python_v2 import CentinelaAPIClient

# Conectar
client = CentinelaAPIClient('http://localhost:5000')

# Autenticarse
client.login('admin', 'admin123')

# Análisis simple
resultado = client.analyze(
    rol="Estudiante",
    tipo_producto="Tesis",
    evidencias={
        'estilo_diferente': 1,
        'referencias_raras': 1,
        'defensa_debil': 1
    }
)

# Ver resultado
print(f"Score: {resultado['analysis']['overall_score']}")
print(f"Nivel: {resultado['analysis']['overall_level']}")

# Obtener métricas
metricas = client.get_metrics()
print(f"Total casos: {metricas['resumen_general']['total_casos_analizados']}")
```

### Ejemplo 2: Batch Processing

```python
casos = [
    {'rol': 'Estudiante', 'tipo_producto': f'Documento {i}', 
     'evidencias': {'estilo_diferente': i % 2}} 
    for i in range(100)
]

resultado = client.batch_analyze(casos)
print(f"Procesados: {resultado['procesados']}/{resultado['total']}")
```

---

## ✅ VALIDACIÓN COMPLETA

Ejecutar:
```bash
python3 run_tests.py
```

Debe mostrar:
- ✅ 17/17 tests
- ✅ API disponible
- ✅ Endpoints funcionales

---

## 🎓 PRÓXIMAS MEJORAS (Roadmap)

- [ ] WebSocket para análisis en tiempo real
- [ ] Caché de resultados con Redis
- [ ] Base de datos de usuarios real
- [ ] Roles y permisos granulares
- [ ] Exportación de reportes (PDF, Excel)
- [ ] Machine Learning con históricos
- [ ] Integración con Slack/Teams
- [ ] Monitoreo y alertas

---

**Versión:** 2.1 - API REST Completa y Segura  
**Próxima actualización:** v2.2 con WebSocket

Comienza en: http://localhost:5000/apidocs
