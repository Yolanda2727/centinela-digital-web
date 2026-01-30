# Arquitectura Centinela Digital v2.2
## Sistema Integrado de Análisis de Integridad y Auditoría

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Componentes Principales](#componentes-principales)
3. [Nuevas Características](#nuevas-características)
4. [Flujos de Datos](#flujos-de-datos)
5. [Base de Datos](#base-de-datos)
6. [Seguridad](#seguridad)
7. [Guía de Implementación](#guía-de-implementación)

---

## 🎯 Visión General

Centinela Digital v2.2 es una plataforma enterprise de detección de fraude académico que combina:

- **Análisis Inteligente**: Evaluación multiidimensional de documentos
- **Integridad Científica**: Detección avanzada de mala conducta
- **Auditoría Completa**: Registro de todas las actividades
- **Seguridad Robusta**: Autenticación JWT y permisos granulares

### Mejoras respecto a v2.1

| Característica | v2.1 | v2.2 |
|---|---|---|
| Endpoints | 11 | 15 |
| Metadatos | Básicos | Completos |
| Auditoría | No | Sí |
| Análisis Integridad | No | Sí |
| Cambios Sensibles | No | Sí |
| Alertas | No | Sí |
| BD Auditoría | No | SQLite |

---

## 🏗️ Componentes Principales

### 1. API REST (`api_v2_mejorado.py` - 455 líneas)

**Responsabilidades:**
- Gestión de endpoints REST
- Autenticación JWT
- Validación de requests
- Registro de auditoría

**Endpoints Principales:**
```
POST   /api/auth/login                      # Autenticación
POST   /api/auth/register                   # Registro
POST   /api/analyze                         # Análisis simple
POST   /api/reporte-integridad              # Análisis integridad
POST   /api/batch/analyze                   # Lote
GET    /api/log-actividad                   # Historial actividades
GET    /api/auditoria/usuario/<usuario>     # Reporte usuario
GET    /api/auditoria/análisis              # Historial análisis
GET    /api/auditoria/cambios-sensibles     # Cambios críticos
GET    /api/auditoria/alertas               # Alertas sistema
GET    /api/metrics/institutional           # Métricas
GET    /health                              # Estado
```

### 2. Análisis de Integridad (`advanced_integrity_analysis.py` - 280 líneas)

**Clases:**
- `AnálisisIntegridad`: Motor de análisis científico
- `AnálisisConMetadatos`: Envolvedor con metadatos

**Módulos de Análisis:**

#### A. Plagio Conceptual
```python
PLAGIO_CONCEPTUAL = {
    "sin_atribución": {
        "indicadores": ["Ideas idénticas sin cita", ...],
        "peso": 30
    },
    "reutilización_excesiva": {
        "indicadores": [">40% contenido parafraseado", ...],
        "peso": 20
    }
}
```

#### B. Desviaciones Metodológicas
```python
DESVIACIONES_METODOLOGICAS = {
    "método_no_descrito": {"indicadores": [...], "peso": 25},
    "incompatibilidad_método_objetivo": {"indicadores": [...], "peso": 25},
    "cambios_posteriori": {"indicadores": [...], "peso": 20}
}
```

#### C. Mala Conducta Científica
```python
MALA_CONDUCTA = {
    "fabricación": {"indicadores": [Datos exactos improbables], "peso": 40},
    "falsificación": {"indicadores": [Datos omitidos selectivamente], "peso": 35},
    "conflicto_interés": {"indicadores": [Financiamiento no declarado], "peso": 25}
}
```

#### D. Falacias Argumentativas
```python
FALACIAS = {
    "ad_hominem": "Ataque a la persona",
    "falsa_causalidad": "Confundir correlación con causación",
    "generalización_excesiva": "Extrapolar más allá de datos",
    "apelación_autoridad": "Usar autoridad en lugar de evidencia",
    "argumento_circular": "Usar conclusión como premisa"
}
```

### 3. Sistema de Auditoría (`auditoria_sistema.py` - 400 líneas)

**Clase Principal:** `SistemaAuditoria`

**Métodos Clave:**
```python
# Registro
registrar_análisis()              # Guarda análisis
registrar_actividad()             # Guarda actividad
registrar_cambio_sensible()       # Guarda cambio crítico
crear_alerta()                    # Crea alerta

# Consulta
obtener_log_actividad()           # Historial actividades
obtener_análisis_usuario()        # Análisis de usuario
obtener_cambios_sensibles()       # Cambios críticos
obtener_alertas()                 # Alertas activas
generar_reporte_auditoria()       # Reporte completo
```

### 4. Cliente Python (`cliente_v2_2.py` - 350 líneas)

**Clase:** `CentinelaAPIClientV2_2`

**Métodos:**
```python
# Autenticación
login(username, password)
register(username, password)

# Análisis
analyze(contenido, tipo_documento, rol, temperatura, prompts)
reporte_integridad(contenido, rol)
batch_analyze(documentos)

# Auditoría
obtener_log_actividad()
obtener_reporte_auditoria()
obtener_análisis_realizados()
obtener_cambios_sensibles()
obtener_alertas()
```

### 5. Demo Script (`demo_api_v2_2.py` - 400 líneas)

Demostraciones interactivas de:
1. Autenticación JWT
2. Análisis con metadatos
3. Análisis de integridad
4. Procesamiento en lote
5. Log de actividades
6. Reporte de auditoría
7. Historial de análisis

---

## 🆕 Nuevas Características

### 1. Metadatos Completos

**En cada análisis se registran:**
```json
{
  "metadatos": {
    "fecha": "2025-01-30T10:30:45.123456",
    "usuario": "admin",
    "version_modelo": "2.2",
    "temperatura": 0.7,
    "prompts_usados": ["análisis_académico"],
    "ajustes": {
      "temperatura": 0.7,
      "top_p": 0.9,
      "max_tokens": 2000
    }
  }
}
```

**Beneficios:**
- Trazabilidad completa
- Reproducibilidad
- Auditoría detallada
- Análisis histórico

### 2. Análisis de Integridad Científica

**Nuevo endpoint:** `POST /api/reporte-integridad`

**Detecta:**
- Plagio conceptual (sin atribución, reutilización excesiva)
- Desviaciones metodológicas (método no descrito, cambios posteriori)
- Mala conducta científica (fabricación, falsificación, conflictos)
- Falacias argumentativas (ad hominem, falsa causalidad, etc.)

**Output:**
```json
{
  "plagio_conceptual": {
    "score": 15,
    "hallazgos": ["Pocas referencias detectadas"],
    "detalles": {...}
  },
  "desviaciones_metodologicas": {...},
  "mala_conducta": {...},
  "falacias": {...},
  "score_general": 10,
  "nivel_riesgo": "BAJO",
  "recomendaciones": [...]
}
```

### 3. Sistema de Auditoría Completo

**Tabla: `actividades`** - Todas las acciones del sistema
```
id | timestamp | usuario | tipo_actividad | endpoint | estado | duracion_ms
```

**Tabla: `análisis_realizados`** - Historial de análisis
```
id | timestamp | usuario | score_general | nivel_riesgo | recomendaciones
```

**Tabla: `cambios_sensibles`** - Modificaciones críticas
```
id | timestamp | usuario | tipo_cambio | antes | despues | razon
```

**Tabla: `alertas`** - Eventos de seguridad
```
id | timestamp | nivel | tipo_alerta | descripcion | resuelta
```

### 4. Endpoints de Auditoría

| Endpoint | Método | Descripción | Permisos |
|---|---|---|---|
| `/api/log-actividad` | GET | Historial de actividades | Propio/Admin |
| `/api/auditoria/usuario/<usuario>` | GET | Reporte usuario | Propio/Admin |
| `/api/auditoria/análisis` | GET | Historial análisis | Propio/Admin |
| `/api/auditoria/cambios-sensibles` | GET | Cambios críticos | Admin |
| `/api/auditoria/alertas` | GET | Alertas sistema | Admin |

---

## 🔄 Flujos de Datos

### Flujo 1: Análisis Simple

```
Usuario
  ↓
POST /api/analyze
  ↓
[Autenticación JWT]
  ↓
[Análisis de Integridad]
  ↓
[Recolectar Metadatos]
  ↓
[Guardar en BD Auditoría]
  ↓
Respuesta JSON
```

### Flujo 2: Análisis de Integridad

```
Usuario
  ↓
POST /api/reporte-integridad
  ↓
[Verificar Token]
  ↓
[AnálisisIntegridad.analizar_integridad_completa()]
  ├─ Plagio Conceptual
  ├─ Desviaciones Metodológicas
  ├─ Mala Conducta
  ├─ Falacias
  └─ Score General
  ↓
[Crear Alerta si Crítico]
  ↓
[Registrar en Auditoría]
  ↓
Respuesta Detallada
```

### Flujo 3: Procesamiento en Lote

```
Usuario
  ↓
POST /api/batch/analyze
  ↓
[Autenticación]
  ↓
Para cada documento:
  ├─ Análisis Individual
  ├─ Recolectar Metadatos
  └─ Guardar resultado
  ↓
[Registrar Batch en Auditoría]
  ↓
Resultados Agregados
```

### Flujo 4: Consulta de Auditoría

```
Usuario/Admin
  ↓
GET /api/log-actividad
  ↓
[Verificar Permisos]
  ├─ Si Admin: Ver todo
  └─ Si Usuario: Ver solo propio
  ↓
[Consultar BD Auditoría]
  ↓
[Filtrar por parámetros]
  ↓
JSON con Historial
```

---

## 🗄️ Base de Datos

### Ubicación
```
.centinela_data/
├── centinela.db          # Base de datos principal (existente)
├── auditoria.db          # Base de datos de auditoría (NUEVA)
└── logs/
    ├── análisis_admin.jsonl
    ├── análisis_profesor.jsonl
    └── ...
```

### Esquema: `auditoria.db`

#### Tabla: actividades
```sql
CREATE TABLE actividades (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    usuario TEXT NOT NULL,
    tipo_actividad TEXT NOT NULL,
    endpoint TEXT,
    metodo_http TEXT,
    ip_origen TEXT,
    estado TEXT,
    detalles TEXT,          -- JSON
    resultado TEXT,
    duracion_ms INTEGER
);

CREATE INDEX idx_usuario_fecha ON actividades(usuario, timestamp);
CREATE INDEX idx_tipo ON actividades(tipo_actividad);
```

#### Tabla: análisis_realizados
```sql
CREATE TABLE análisis_realizados (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    usuario TEXT NOT NULL,
    tipo_documento TEXT,
    rol_autor TEXT,
    version_modelo TEXT,
    temperatura REAL,
    score_general REAL,
    nivel_riesgo TEXT,
    recomendaciones TEXT,    -- JSON
    documento_hash TEXT UNIQUE,
    duracion_ms INTEGER
);

CREATE INDEX idx_usuario_nivel ON análisis_realizados(usuario, nivel_riesgo);
CREATE INDEX idx_hash ON análisis_realizados(documento_hash);
```

#### Tabla: cambios_sensibles
```sql
CREATE TABLE cambios_sensibles (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    usuario TEXT NOT NULL,
    tipo_cambio TEXT,
    descripcion TEXT,
    antes TEXT,
    despues TEXT,
    razon TEXT
);

CREATE INDEX idx_usuario_tipo ON cambios_sensibles(usuario, tipo_cambio);
```

#### Tabla: alertas
```sql
CREATE TABLE alertas (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    nivel TEXT,
    tipo_alerta TEXT,
    descripcion TEXT,
    usuario_afectado TEXT,
    resuelta INTEGER DEFAULT 0
);

CREATE INDEX idx_nivel ON alertas(nivel, resuelta);
```

---

## 🔐 Seguridad

### 1. Autenticación

**Mecanismo:** JWT (JSON Web Tokens)

```python
token = jwt.encode({
    'user_id': username,
    'exp': datetime.utcnow() + timedelta(hours=24)
}, app.config['SECRET_KEY'], algorithm='HS256')
```

**Header requerido:**
```
Authorization: Bearer eyJ0eXAi...
```

### 2. Autorización

**Niveles:**
- **Público:** `/health`, `/api/info`
- **Autenticado:** `/api/analyze`, `/api/reporte-integridad`, `/api/log-actividad`
- **Mismo Usuario:** `/api/auditoria/usuario/{usuario}` (puede consultar propio)
- **Admin:** `/api/auditoria/cambios-sensibles`, `/api/auditoria/alertas`

### 3. Auditoría de Seguridad

**Se registran:**
- Intentos de login fallidos
- Accesos no autorizados
- Cambios sensibles del sistema
- Errores del servidor
- Acceso a auditoría de otros usuarios

**Ejemplos de Alertas:**
```python
if usuario_filtro != request.user_id and request.user_id != 'admin':
    auditoria.crear_alerta(
        "MEDIO",
        "acceso_no_autorizado",
        f"Intento de acceso al log de {usuario_filtro}",
        request.user_id
    )
```

### 4. Protección de Datos

- **Hash de documentos:** SHA256
- **Passwords:** Requieren hashing en producción (bcrypt)
- **Tokens:** 24 horas de expiración
- **CORS:** Configurado para localhost (cambiar en producción)

---

## 🚀 Guía de Implementación

### Instalación

```bash
# 1. Clonar/actualizar
cd /workspaces/centinela-digital-web

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear directorios
mkdir -p .centinela_data/logs
```

### Ejecución

```bash
# Opción 1: API v2.2 mejorado
python3 api_v2_mejorado.py

# Opción 2: Ejecutar demo
python3 demo_api_v2_2.py

# Opción 3: Cliente Python interactivo
python3 cliente_v2_2.py
```

### Acceso

```bash
# Swagger API
http://localhost:5000/apidocs/

# Health check
curl http://localhost:5000/health

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 📊 Ejemplo: Flujo Completo

```python
from cliente_v2_2 import CentinelaAPIClientV2_2

# 1. Crear cliente
cliente = CentinelaAPIClientV2_2("http://localhost:5000")

# 2. Autenticarse
cliente.login("admin", "admin123")

# 3. Analizar documento
análisis = cliente.analyze(
    contenido="Documento académico...",
    tipo_documento="investigación",
    rol="Investigador",
    temperatura=0.7,
    prompts=["análisis_académico"]
)

# 4. Ver resultado
print(f"Score: {análisis['resultados']['score_general']}")
print(f"Riesgo: {análisis['resultados']['nivel_riesgo']}")
print(f"Fecha: {análisis['metadatos']['fecha']}")
print(f"Usuario: {análisis['metadatos']['usuario']}")

# 5. Análisis de integridad
integridad = cliente.reporte_integridad(
    contenido="Investigación con posibles problemas...",
    rol="Investigador"
)

print(f"Plagio: {integridad['análisis']['plagio_conceptual']['score']}")
print(f"Falacias: {integridad['análisis']['falacias']['score']}")

# 6. Ver historial
reporte = cliente.obtener_reporte_auditoria()
print(f"Total análisis: {reporte['resumen']['total_análisis']}")
```

---

## ✅ Checklist de Producción

- [ ] Cambiar `SECRET_KEY` a valor seguro
- [ ] Configurar HTTPS/SSL
- [ ] Usar base de datos real para usuarios
- [ ] Implementar bcrypt para passwords
- [ ] Configurar rate limiting
- [ ] Habilitar logging a archivo
- [ ] Configurar CORS apropiadamente
- [ ] Implementar backup de BD auditoría
- [ ] Configurar alertas en monitoreo
- [ ] Documento de políticas de privacidad/GDPR

---

## 🎯 Roadmap v2.3

- [ ] Exportación de reportes a PDF
- [ ] Gráficos de tendencias en dashboard
- [ ] Webhooks para alertas en tiempo real
- [ ] Integración con LMS (Canvas, Moodle, Blackboard)
- [ ] Machine learning mejorado
- [ ] API de validación de fuentes académicas
- [ ] Soporte multiidioma
- [ ] Mobile app
- [ ] Análisis de plagio visual (tablas, gráficos)
- [ ] Integración con plagiarism detection (Turnitin, Copyscape)
