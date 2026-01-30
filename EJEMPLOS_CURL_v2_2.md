# Ejemplos Prácticos - cURL para API v2.2

## 🔐 Autenticación

### Obtener Token JWT
```bash
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }' | jq -r '.token')

echo "Token obtenido: $TOKEN"
```

### Registrar Nuevo Usuario
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevo_usuario",
    "password": "contraseña123"
  }'
```

---

## 📊 Análisis Simple (CON METADATOS)

### Análisis Básico
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contenido": "Este es un documento que será analizado.",
    "tipo_documento": "ensayo",
    "rol": "Estudiante"
  }' | jq .
```

### Análisis con Parámetros Completos
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contenido": "Investigación sobre inteligencia artificial. Según Smith et al. (2023), la IA ha revolucionado la educación. Nuestro estudio incluye 200 participantes.",
    "tipo_documento": "investigación",
    "rol": "Investigador",
    "temperatura": 0.7,
    "prompts": ["análisis_académico", "detección_plagio"]
  }' | jq .
```

### Ver Solo Metadatos
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contenido": "Texto..."}' | jq '.metadatos'
```

### Ver Solo Resultados
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contenido": "Texto..."}' | jq '.resultados'
```

### Ver Solo Análisis
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contenido": "Texto..."}' | jq '.análisis'
```

---

## 🔍 Análisis de Integridad Científica

### Análisis de Integridad Simple
```bash
curl -X POST http://localhost:5000/api/reporte-integridad \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contenido": "Metodología: Se realizó estudio experimental. Los datos muestran resultados perfectos: 95.00%, 95.00%. Como dice el Dr. Experto, nuestras conclusiones son correctas.",
    "rol": "Investigador"
  }' | jq .
```

### Ver Score de Plagio Conceptual
```bash
curl -X POST http://localhost:5000/api/reporte-integridad \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contenido": "Documento...", "rol": "Investigador"}' | \
  jq '.análisis.plagio_conceptual'
```

### Ver Score de Falacias
```bash
curl -X POST http://localhost:5000/api/reporte-integridad \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contenido": "Documento...", "rol": "Investigador"}' | \
  jq '.análisis.falacias'
```

### Ver Hallazgos de Mala Conducta
```bash
curl -X POST http://localhost:5000/api/reporte-integridad \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contenido": "Documento...", "rol": "Investigador"}' | \
  jq '.análisis.mala_conducta.hallazgos'
```

### Ver Recomendaciones
```bash
curl -X POST http://localhost:5000/api/reporte-integridad \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contenido": "Documento...", "rol": "Investigador"}' | \
  jq '.análisis.recomendaciones'
```

---

## 📦 Procesamiento en Lote

### Analizar 3 Documentos
```bash
curl -X POST http://localhost:5000/api/batch/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "documentos": [
      {
        "contenido": "Primer documento de ensayo...",
        "tipo_documento": "ensayo",
        "rol": "Estudiante"
      },
      {
        "contenido": "Segunda investigación...",
        "tipo_documento": "investigación",
        "rol": "Investigador"
      },
      {
        "contenido": "Tercer artículo académico...",
        "tipo_documento": "artículo",
        "rol": "Académico"
      }
    ]
  }' | jq .
```

### Ver Solo Resultados del Lote
```bash
curl -X POST http://localhost:5000/api/batch/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"documentos": [...]}' | jq '.resultados'
```

### Contar Documentos Procesados
```bash
curl -X POST http://localhost:5000/api/batch/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"documentos": [...]}' | jq '.metadatos.documentos_procesados'
```

---

## 📋 Log de Actividades (AUDITORÍA)

### Ver Mi Historial Completo
```bash
curl -X GET "http://localhost:5000/api/log-actividad" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Últimas 10 Actividades
```bash
curl -X GET "http://localhost:5000/api/log-actividad?límite=10" \
  -H "Authorization: Bearer $TOKEN" | jq '.actividades'
```

### Actividades de los Últimos 7 Días
```bash
curl -X GET "http://localhost:5000/api/log-actividad?días=7" \
  -H "Authorization: Bearer $TOKEN" | jq '.actividades'
```

### Solo Análisis Simples
```bash
curl -X GET "http://localhost:5000/api/log-actividad?tipo=análisis_simple" \
  -H "Authorization: Bearer $TOKEN" | jq '.actividades'
```

### Ver Duraciones de Análisis
```bash
curl -X GET "http://localhost:5000/api/log-actividad?tipo=análisis_simple" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.actividades[] | {timestamp, duracion_ms, resultado}'
```

### Contar Actividades por Tipo
```bash
curl -X GET "http://localhost:5000/api/log-actividad" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '[.actividades[] | .tipo_actividad] | group_by(.) | map({tipo: .[0], cantidad: length})'
```

---

## 👤 Reporte de Auditoría de Usuario

### Mi Reporte Completo
```bash
curl -X GET "http://localhost:5000/api/auditoria/usuario/admin" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Ver Resumen
```bash
curl -X GET "http://localhost:5000/api/auditoria/usuario/admin" \
  -H "Authorization: Bearer $TOKEN" | jq '.resumen'
```

### Ver Análisis del Usuario
```bash
curl -X GET "http://localhost:5000/api/auditoria/usuario/admin" \
  -H "Authorization: Bearer $TOKEN" | jq '.análisis'
```

### Ver Score Promedio
```bash
curl -X GET "http://localhost:5000/api/auditoria/usuario/admin" \
  -H "Authorization: Bearer $TOKEN" | jq '.análisis.score_promedio'
```

### Ver Distribución de Riesgos
```bash
curl -X GET "http://localhost:5000/api/auditoria/usuario/admin" \
  -H "Authorization: Bearer $TOKEN" | jq '{
    crítico: .análisis.documentos_críticos,
    alto: .análisis.documentos_alto_riesgo,
    medio: .análisis.documentos_medio_riesgo,
    bajo: .análisis.documentos_bajo_riesgo
  }'
```

---

## 📊 Historial de Análisis

### Ver Todos Mis Análisis
```bash
curl -X GET "http://localhost:5000/api/auditoria/análisis" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Solo Últimos 5 Análisis
```bash
curl -X GET "http://localhost:5000/api/auditoria/análisis" \
  -H "Authorization: Bearer $TOKEN" | jq '.análisis[0:5]'
```

### Análisis de Últimos 7 Días
```bash
curl -X GET "http://localhost:5000/api/auditoria/análisis?días=7" \
  -H "Authorization: Bearer $TOKEN" | jq '.análisis'
```

### Ver Documentos Críticos
```bash
curl -X GET "http://localhost:5000/api/auditoria/análisis" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.análisis[] | select(.nivel_riesgo=="CRÍTICO")'
```

### Análisis por Tipo de Documento
```bash
curl -X GET "http://localhost:5000/api/auditoria/análisis" \
  -H "Authorization: Bearer $TOKEN" | \
  jq 'group_by(.tipo_documento)'
```

---

## ⚠️ Cambios Sensibles (ADMIN ONLY)

### Ver Todos los Cambios
```bash
curl -X GET "http://localhost:5000/api/auditoria/cambios-sensibles" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Solo Modificaciones de Resultados
```bash
curl -X GET "http://localhost:5000/api/auditoria/cambios-sensibles?tipo=modificación_resultados" \
  -H "Authorization: Bearer $TOKEN" | jq '.cambios'
```

### Ver Cambios de Últimos 30 Días
```bash
curl -X GET "http://localhost:5000/api/auditoria/cambios-sensibles?días=30" \
  -H "Authorization: Bearer $TOKEN" | jq '.cambios'
```

### Ver Quién Hizo Cambios
```bash
curl -X GET "http://localhost:5000/api/auditoria/cambios-sensibles" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.cambios[] | {usuario, tipo_cambio, descripcion, timestamp}'
```

---

## 🚨 Alertas del Sistema (ADMIN ONLY)

### Ver Todas las Alertas
```bash
curl -X GET "http://localhost:5000/api/auditoria/alertas" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Solo Alertas Críticas Sin Resolver
```bash
curl -X GET "http://localhost:5000/api/auditoria/alertas?nivel=CRÍTICO&resuelta=false" \
  -H "Authorization: Bearer $TOKEN" | jq '.alertas'
```

### Alertas de Último Día
```bash
curl -X GET "http://localhost:5000/api/auditoria/alertas" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.alertas[] | select(.timestamp > now - 86400)'
```

### Contar por Nivel
```bash
curl -X GET "http://localhost:5000/api/auditoria/alertas" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '[.alertas[] | .nivel] | group_by(.) | map({nivel: .[0], cantidad: length})'
```

---

## ℹ️ Información del API

### Ver Información General
```bash
curl -X GET "http://localhost:5000/api/info" | jq .
```

### Ver Versión
```bash
curl -X GET "http://localhost:5000/api/info" | jq '.versión'
```

### Ver Características
```bash
curl -X GET "http://localhost:5000/api/info" | jq '.características'
```

### Verificar Estado del API
```bash
curl -X GET "http://localhost:5000/health" | jq .
```

---

## 📝 Scriptable Examples

### Script: Analizar Archivo de Texto

```bash
#!/bin/bash

# Leer archivo
CONTENIDO=$(cat documento.txt)

# Obtener token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.token')

# Analizar
curl -X POST http://localhost:5000/api/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"contenido\":\"$CONTENIDO\",\"tipo_documento\":\"investigación\"}" | \
  jq '.resultados'
```

### Script: Monitorear Análisis Diarios

```bash
#!/bin/bash

# Obtener token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.token')

# Obtener análisis de hoy
curl -s -X GET "http://localhost:5000/api/auditoria/análisis?días=1" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.análisis | length' > /tmp/análisis_hoy.txt

CANTIDAD=$(cat /tmp/análisis_hoy.txt)
echo "Análisis realizados hoy: $CANTIDAD"
```

### Script: Exportar Alertas a CSV

```bash
#!/bin/bash

# Obtener token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.token')

# Exportar alertas
curl -s -X GET "http://localhost:5000/api/auditoria/alertas" \
  -H "Authorization: Bearer $TOKEN" | \
  jq -r '.alertas[] | [.id, .timestamp, .nivel, .tipo_alerta, .descripcion] | @csv' > alertas.csv

echo "Alertas exportadas a alertas.csv"
```

---

## 🎯 Casos de Uso Comunes

### Caso 1: Revisor - Analizar Trabajo de Estudiante

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"profesor","password":"prof123"}' | jq -r '.token')

# 2. Analizar
curl -X POST http://localhost:5000/api/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "contenido": "Contenido del trabajo...",
    "tipo_documento": "ensayo",
    "rol": "Estudiante"
  }' | jq '.resultados'

# 3. Ver mi historial
curl -X GET "http://localhost:5000/api/log-actividad" \
  -H "Authorization: Bearer $TOKEN" | jq '.actividades | length'
```

### Caso 2: Admin - Auditar Actividades

```bash
# 1. Login como admin
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.token')

# 2. Ver cambios sensibles
curl -X GET "http://localhost:5000/api/auditoria/cambios-sensibles" \
  -H "Authorization: Bearer $TOKEN" | jq '.cambios'

# 3. Ver alertas
curl -X GET "http://localhost:5000/api/auditoria/alertas" \
  -H "Authorization: Bearer $TOKEN" | jq '.alertas[]'

# 4. Generar reporte
curl -X GET "http://localhost:5000/api/auditoria/usuario/profesor" \
  -H "Authorization: Bearer $TOKEN" | jq '.resumen'
```

### Caso 3: Investigador - Verificar Integridad

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"investigador","password":"inv123"}' | jq -r '.token')

# 2. Análisis de integridad
curl -X POST http://localhost:5000/api/reporte-integridad \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"contenido": "Investigación...", "rol": "Investigador"}' | \
  jq '.análisis | {score_general, nivel_riesgo, recomendaciones}'
```

---

## 💡 Tips y Trucos

### Ver bonita cualquier respuesta JSON
```bash
curl -s ... | jq '.' | less
```

### Guardar respuesta en archivo
```bash
curl -s ... | jq . > respuesta.json
```

### Extraer solo errores
```bash
curl -s ... | jq '.error' 2>/dev/null
```

### Medir tiempo de respuesta
```bash
time curl -s ... | jq .
```

### Ver headers de respuesta
```bash
curl -i ... | head -20
```

### Hacer requests silenciosos
```bash
curl -s -S ...  # -s: silencioso, -S: muestra errores
```

---

**Última actualización:** 30 de Enero, 2025  
**Versión API:** 2.2
