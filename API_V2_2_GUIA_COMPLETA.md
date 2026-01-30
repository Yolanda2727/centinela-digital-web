# API v2.2 - Guía Completa con Integridad y Auditoría

## 🎯 Nuevas Características

### 1. Metadatos Completos en Análisis
Cada análisis incluye:
- **Fecha**: Timestamp ISO
- **Usuario**: ID del usuario que realizó el análisis
- **Versión del modelo**: v2.2
- **Prompts usados**: Lista de prompts del modelo
- **Temperatura**: Ajuste de creatividad (0.7 por defecto)
- **Resultados**: Scores y nivel de riesgo

### 2. Análisis de Integridad Científica (`/api/reporte-integridad`)

#### Detecta:
- **Plagio Conceptual**: Ideas sin atribución, reutilización excesiva
- **Desviaciones Metodológicas**: Método no descrito, incompatibilidades, cambios posteriori
- **Mala Conducta**: Fabricación de datos, falsificación, conflictos de interés
- **Falacias Argumentativas**: Ad hominem, falsa causalidad, generalización excesiva

#### Ejemplo de uso:
```bash
curl -X POST http://localhost:5000/api/reporte-integridad \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contenido": "Este estudio demuestra que... los datos muestran...",
    "rol": "Investigador"
  }'
```

#### Respuesta:
```json
{
  "metadatos": {
    "fecha": "2025-01-30T10:30:45.123456",
    "usuario": "admin",
    "version_modelo": "2.2-integrity",
    "duracion_ms": 245
  },
  "análisis": {
    "plagio_conceptual": {
      "score": 15,
      "hallazgos": ["Pocas referencias/atribuciones detectadas"],
      "detalles": {...}
    },
    "desviaciones_metodologicas": {
      "score": 0,
      "hallazgos": [],
      "detalles": {...}
    },
    "mala_conducta": {
      "score": 15,
      "hallazgos": ["No declara posibles conflictos de interés"]
    },
    "falacias": {
      "score": 10,
      "hallazgos": ["Posible falacia: falsa_causalidad"]
    },
    "score_general": 10,
    "nivel_riesgo": "BAJO",
    "recomendaciones": [
      "Revisar atribuciones y referencias",
      "Declarar todos los conflictos de interés"
    ]
  }
}
```

### 3. Sistema de Auditoría Completo

#### `/api/log-actividad`
Historial de todas las actividades:

```bash
# Obtener tu historial
curl -X GET "http://localhost:5000/api/log-actividad?días=30&límite=50" \
  -H "Authorization: Bearer $TOKEN"

# Admin: ver actividades de otro usuario
curl -X GET "http://localhost:5000/api/log-actividad?usuario=profesor&tipo=análisis_simple" \
  -H "Authorization: Bearer $TOKEN"
```

Respuesta:
```json
{
  "fecha": "2025-01-30T10:35:00",
  "usuario": "admin",
  "total_registros": 25,
  "actividades": [
    {
      "id": 1,
      "timestamp": "2025-01-30T10:33:15",
      "usuario": "admin",
      "tipo_actividad": "análisis_simple",
      "endpoint": "/api/analyze",
      "metodo_http": "POST",
      "estado": "exitosa",
      "detalles": {"tipo_documento": "ensayo", "rol": "Estudiante"},
      "resultado": "BAJO",
      "duracion_ms": 245
    }
  ]
}
```

#### `/api/auditoria/usuario/<usuario>`
Reporte completo de un usuario:

```bash
curl -X GET "http://localhost:5000/api/auditoria/usuario/admin" \
  -H "Authorization: Bearer $TOKEN"
```

Respuesta:
```json
{
  "usuario": "admin",
  "fecha_generación": "2025-01-30T10:35:00",
  "resumen": {
    "total_actividades": 42,
    "total_análisis": 15,
    "cambios_sensibles": 2
  },
  "análisis": {
    "score_promedio": 25.3,
    "documentos_críticos": 0,
    "documentos_alto_riesgo": 2,
    "documentos_medio_riesgo": 5,
    "documentos_bajo_riesgo": 8
  },
  "actividades_recientes": [...],
  "análisis_recientes": [...],
  "cambios_recientes": [...]
}
```

#### `/api/auditoria/análisis`
Historial de análisis realizados:

```bash
curl -X GET "http://localhost:5000/api/auditoria/análisis?usuario=admin&días=7" \
  -H "Authorization: Bearer $TOKEN"
```

#### `/api/auditoria/cambios-sensibles`
Cambios críticos del sistema (solo admin):

```bash
curl -X GET "http://localhost:5000/api/auditoria/cambios-sensibles?tipo=eliminación_datos" \
  -H "Authorization: Bearer $TOKEN"
```

Respuesta:
```json
{
  "fecha": "2025-01-30T10:35:00",
  "total_cambios": 5,
  "cambios": [
    {
      "id": 1,
      "timestamp": "2025-01-30T09:45:12",
      "usuario": "admin",
      "tipo_cambio": "modificación_resultados",
      "descripcion": "Corrección de análisis erróneo",
      "antes": "CRÍTICO",
      "despues": "ALTO",
      "razon": "Error en cálculo de score"
    }
  ]
}
```

#### `/api/auditoria/alertas`
Alertas del sistema (solo admin):

```bash
curl -X GET "http://localhost:5000/api/auditoria/alertas?nivel=CRÍTICO&resuelta=false" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 Flujo de Análisis Mejorado

### Análisis Simple con Metadatos
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contenido": "El documento a analizar...",
    "tipo_documento": "ensayo",
    "rol": "Estudiante",
    "temperatura": 0.7,
    "prompts": ["prompt_1", "prompt_2"]
  }'
```

**Respuesta incluye:**
- Metadatos (fecha, usuario, versión, temperatura, prompts)
- Análisis detallado
- Resultados con scores
- Recomendaciones

### Análisis de Integridad
```bash
curl -X POST http://localhost:5000/api/reporte-integridad \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contenido": "Documento académico...",
    "rol": "Investigador"
  }'
```

**Respuesta incluye:**
- Análisis de plagio conceptual
- Análisis de desviaciones metodológicas
- Análisis de mala conducta
- Análisis de falacias
- Score general y nivel de riesgo
- Recomendaciones específicas

### Procesamiento en Lote
```bash
curl -X POST http://localhost:5000/api/batch/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "documentos": [
      {
        "contenido": "Documento 1...",
        "tipo_documento": "ensayo",
        "rol": "Estudiante"
      },
      {
        "contenido": "Documento 2...",
        "tipo_documento": "investigación",
        "rol": "Investigador"
      }
    ]
  }'
```

---

## 🔐 Estructura de Base de Datos de Auditoría

### Tabla: `actividades`
```sql
- id: ID único
- timestamp: Cuándo ocurrió
- usuario: Quién realizó la acción
- tipo_actividad: login, análisis_simple, análisis_integridad, etc.
- endpoint: Ruta del API
- metodo_http: GET, POST, etc.
- ip_origen: IP del cliente
- estado: exitosa, error, rechazada
- detalles: JSON con parámetros
- resultado: Resultado de la acción
- duracion_ms: Milisegundos tardó
```

### Tabla: `análisis_realizados`
```sql
- id: ID único
- timestamp: Cuándo se realizó
- usuario: Quién lo realizó
- tipo_documento: ensayo, investigación, etc.
- rol_autor: Estudiante, Investigador, Profesor
- version_modelo: 2.2
- temperatura: Parámetro usado
- score_general: Score final
- nivel_riesgo: CRÍTICO, ALTO, MEDIO, BAJO
- recomendaciones: JSON
- documento_hash: SHA256 del contenido
- duracion_ms: Tiempo de procesamiento
```

### Tabla: `cambios_sensibles`
```sql
- id: ID único
- timestamp: Cuándo cambió
- usuario: Quién lo cambió
- tipo_cambio: eliminación_datos, modificación_resultados, cambio_configuración
- descripcion: Qué cambió
- antes: Valor anterior
- despues: Valor nuevo
- razon: Por qué cambió
```

### Tabla: `alertas`
```sql
- id: ID único
- timestamp: Cuándo se creó
- nivel: CRÍTICO, ALTO, MEDIO, BAJO
- tipo_alerta: Categoría de alerta
- descripcion: Detalles
- usuario_afectado: A quién afecta
- resuelta: 0 o 1
```

---

## 📈 Ejemplos Python Cliente v2.2

```python
from cliente_python_v2 import CentinelaAPIClient

# Inicializar cliente
cliente = CentinelaAPIClient("http://localhost:5000")

# Autenticarse
token = cliente.login("admin", "admin123")

# Análisis simple con metadatos
análisis = cliente.analyze(
    contenido="El documento...",
    tipo_documento="ensayo",
    rol="Estudiante",
    temperatura=0.7,
    prompts=["prompt_análisis"]
)
print(f"Score: {análisis['resultados']['score_general']}")
print(f"Riesgo: {análisis['resultados']['nivel_riesgo']}")
print(f"Fecha: {análisis['metadatos']['fecha']}")
print(f"Usuario: {análisis['metadatos']['usuario']}")

# Análisis de integridad
integridad = cliente.reporte_integridad(
    contenido="Investigación sobre...",
    rol="Investigador"
)
print(f"Plagio conceptual: {integridad['análisis']['plagio_conceptual']['score']}")
print(f"Falacias: {integridad['análisis']['falacias']['hallazgos']}")

# Obtener historial de actividades
actividades = cliente.get_actividades(días=30)
for actividad in actividades:
    print(f"{actividad['timestamp']}: {actividad['tipo_actividad']}")

# Obtener reporte de auditoría
reporte = cliente.reporte_auditoria()
print(f"Total análisis: {reporte['análisis']['total_análisis']}")
print(f"Documentos críticos: {reporte['análisis']['documentos_críticos']}")
```

---

## 🚀 Instalación y Ejecución

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar API v2.2
```bash
python3 api_v2_mejorado.py
```

### 3. Acceder a documentación Swagger
```
http://localhost:5000/apidocs/
```

### 4. Ejecutar análisis
```bash
# Obtener token
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.token')

# Realizar análisis
curl -X POST http://localhost:5000/api/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contenido":"Documento..."}'
```

---

## ⚠️ Consideraciones de Seguridad

### Producción
1. Cambiar `SECRET_KEY` a valor aleatorio
2. Usar HTTPS/SSL
3. Implementar base de datos real para usuarios
4. Hashear contraseñas con bcrypt
5. Implementar rate limiting
6. Habilitar CORS solo para dominios autorizados

### Privacidad
- Los análisis se registran en auditoría
- Solo admins pueden ver auditoría de otros
- Los documentos se hashean, no se guardan completos
- Se pueden borrar registros según GDPR

---

## 📝 Roadmap v2.3+

- [ ] Exportación de reportes a PDF
- [ ] Gráficos de tendencias en auditoría
- [ ] Webhooks para alertas
- [ ] Integración con LMS (Canvas, Moodle)
- [ ] Machine learning para detección mejorada
- [ ] API de validación de fuentes
- [ ] Múltiples idiomas
