# 📖 Índice de Navegación - Centinela Digital v2.2

## 🚀 Comienza Aquí

### Para Comenzar Inmediatamente
1. Lee: [v2_2_COMPLETADO.md](v2_2_COMPLETADO.md) (5 min)
2. Ejecuta: `python3 api_v2_mejorado.py`
3. Prueba: `python3 demo_api_v2_2.py`

---

## 📚 Documentación por Rol

### 👨‍💻 Desarrolladores

**Arquitectura del Sistema**
- [ARQUITECTURA_v2_2.md](ARQUITECTURA_v2_2.md) - Diseño completo, flujos de datos, BD
  - Componentes principales
  - Flujos de datos detallados
  - Esquema de base de datos
  - Ejemplos de código

**API Reference**
- [API_V2_2_GUIA_COMPLETA.md](API_V2_2_GUIA_COMPLETA.md) - Documentación de endpoints
  - Métodos HTTP y parámetros
  - Ejemplos de peticiones
  - Respuestas esperadas
  - Códigos de error

**Código Fuente**
- [advanced_integrity_analysis.py](advanced_integrity_analysis.py) - Motor de análisis (388 líneas)
- [auditoria_sistema.py](auditoria_sistema.py) - Sistema de auditoría (467 líneas)
- [api_v2_mejorado.py](api_v2_mejorado.py) - API REST (724 líneas)
- [cliente_v2_2.py](cliente_v2_2.py) - Cliente Python (486 líneas)

---

### 🔧 DevOps / Sys Admin

**Instalación y Despliegue**
1. [RESUMEN_CAMBIOS_v2_2.md](RESUMEN_CAMBIOS_v2_2.md) - Cambios y mejoras (sección instalación)
2. [ARQUITECTURA_v2_2.md](ARQUITECTURA_v2_2.md) - Guía de implementación y production checklist

**Comandos Esenciales**
```bash
# Instalar
pip install -r requirements.txt

# Ejecutar API
python3 api_v2_mejorado.py

# Ejecutar pruebas
python3 demo_api_v2_2.py
```

**Base de Datos**
- Ubicación: `.centinela_data/auditoria.db`
- Tipo: SQLite
- Tablas: 4 (actividades, análisis_realizados, cambios_sensibles, alertas)

**Seguridad (TODO Producción)**
- [ ] Cambiar `SECRET_KEY` en `api_v2_mejorado.py` línea 26
- [ ] Configurar HTTPS/SSL
- [ ] Implementar bcrypt para passwords
- [ ] Agregar rate limiting
- [ ] Configurar CORS para dominio específico

---

### 👨‍⚕️ QA / Testing

**Pruebas Interactivas**
- [demo_api_v2_2.py](demo_api_v2_2.py) - Script con 7 demostraciones

**Ejemplos de Prueba**
- [EJEMPLOS_CURL_v2_2.md](EJEMPLOS_CURL_v2_2.md) - 50+ ejemplos cURL
  - Login y autenticación
  - Análisis simple
  - Análisis de integridad
  - Procesamiento en lote
  - Auditoría
  - Cambios sensibles
  - Alertas

**Checklist de Testing**
```
Autenticación:
  [ ] Login exitoso
  [ ] Login fallido genera alerta
  [ ] Token expira después de 24h

Análisis:
  [ ] Análisis simple incluye metadatos
  [ ] Análisis integridad detecta 5 dimensiones
  [ ] Batch procesa múltiples documentos

Auditoría:
  [ ] Log registra todas las actividades
  [ ] Cambios sensibles se alertan
  [ ] Alertas se muestran por nivel

Errores:
  [ ] 404 no encontrado
  [ ] 401 sin token
  [ ] 403 no autorizado
  [ ] 500 error servidor
```

---

### 👨‍💼 Product Managers / Stakeholders

**Resumen Ejecutivo**
- [v2_2_COMPLETADO.md](v2_2_COMPLETADO.md) - Overview completo

**Comparativa de Mejoras**
- [RESUMEN_CAMBIOS_v2_2.md](RESUMEN_CAMBIOS_v2_2.md) - Tabla de mejoras v2.1→v2.2

**Características Nuevas**
1. **Metadatos Completos** - Fecha, usuario, versión, prompts, temperatura
2. **Análisis de Integridad** - 5 dimensiones de análisis
3. **Auditoría Completa** - Tracking de todas las actividades
4. **Alertas del Sistema** - Notificaciones de eventos críticos

---

### 👨‍🎓 Usuarios Finales / Académicos

**Guía de Uso**
- [API_V2_2_GUIA_COMPLETA.md](API_V2_2_GUIA_COMPLETA.md) - Cómo usar el API

**Ejemplos Prácticos**
- [EJEMPLOS_CURL_v2_2.md](EJEMPLOS_CURL_v2_2.md) - Cómo hacer peticiones
  - Mediante cURL (línea de comandos)
  - Mediante Python (script)

**Flujo Típico**
```
1. Obtener Token
   curl -X POST /api/auth/login

2. Enviar Documento
   curl -X POST /api/analyze

3. Ver Resultados
   - Score general
   - Nivel de riesgo
   - Recomendaciones

4. Análisis Avanzado
   curl -X POST /api/reporte-integridad
   - Plagio
   - Desviaciones
   - Mala conducta
   - Falacias
```

---

## 🗂️ Estructura de Archivos

```
centinela-digital-web/
├── 📝 Documentación
│   ├── v2_2_COMPLETADO.md ...................... 🎯 Punto de partida
│   ├── API_V2_2_GUIA_COMPLETA.md ............... 📖 Endpoints
│   ├── ARQUITECTURA_v2_2.md .................... 🏗️ Diseño
│   ├── RESUMEN_CAMBIOS_v2_2.md ................ 📊 Cambios
│   ├── EJEMPLOS_CURL_v2_2.md ................... 💻 Ejemplos
│   └── INDICE_DE_NAVEGACION.md ................ 📋 Este archivo
│
├── 🐍 Código Python
│   ├── advanced_integrity_analysis.py ......... 🔍 Análisis integridad
│   ├── auditoria_sistema.py ................... 📊 Auditoría
│   ├── api_v2_mejorado.py ..................... 🚀 API REST
│   ├── cliente_v2_2.py ........................ 📦 Cliente
│   └── demo_api_v2_2.py ....................... 🎬 Demo
│
├── ⚙️ Configuración
│   └── requirements.txt ....................... 📦 Dependencias
│
└── 💾 Base de Datos (generada)
    └── .centinela_data/
        ├── centinela.db ....................... 📄 Principal
        ├── auditoria.db ....................... 📊 Auditoría (NUEVA)
        └── logs/ ............................. 📝 Backups JSON
```

---

## 🔄 Flujos de Trabajo

### Desarrollador Local

```
1. Clonar repositorio
   git clone ...

2. Instalar dependencias
   pip install -r requirements.txt

3. Ejecutar API
   python3 api_v2_mejorado.py

4. Leer documentación
   Abrir: ARQUITECTURA_v2_2.md

5. Ejecutar demo
   python3 demo_api_v2_2.py

6. Probar endpoints
   Ver: EJEMPLOS_CURL_v2_2.md
```

### QA / Tester

```
1. Revisar checklist de features
   [v2_2_COMPLETADO.md](v2_2_COMPLETADO.md)

2. Ejecutar demo automático
   python3 demo_api_v2_2.py

3. Probar manual con cURL
   Ver: EJEMPLOS_CURL_v2_2.md

4. Verificar auditoría
   GET /api/log-actividad
   GET /api/auditoria/alertas

5. Reportar issues
   Con ejemplos de cURL
```

### Producción

```
1. Revisar checklist de producción
   [ARQUITECTURA_v2_2.md](ARQUITECTURA_v2_2.md) - sección Producción

2. Cambiar configuración
   SECRET_KEY → valor seguro
   CORS → dominio específico
   Database → usuario real

3. Ejecutar API
   python3 api_v2_mejorado.py

4. Configurar monitoreo
   Logs → archivo
   Alertas → canal

5. Documentar deployment
   Guardar cambios de configuración
```

---

## 🎯 Quick Links por Tarea

### "Necesito entender qué es v2.2"
→ [v2_2_COMPLETADO.md](v2_2_COMPLETADO.md)

### "Necesito ver los endpoints disponibles"
→ [API_V2_2_GUIA_COMPLETA.md](API_V2_2_GUIA_COMPLETA.md)

### "Necesito ejemplos de cURL"
→ [EJEMPLOS_CURL_v2_2.md](EJEMPLOS_CURL_v2_2.md)

### "Necesito entender la arquitectura"
→ [ARQUITECTURA_v2_2.md](ARQUITECTURA_v2_2.md)

### "Necesito ver qué cambió respecto v2.1"
→ [RESUMEN_CAMBIOS_v2_2.md](RESUMEN_CAMBIOS_v2_2.md)

### "Necesito ejecutar el código"
→ [demo_api_v2_2.py](demo_api_v2_2.py)

### "Necesito usar el cliente Python"
→ [cliente_v2_2.py](cliente_v2_2.py)

### "Necesito hacer un análisis de integridad"
→ [advanced_integrity_analysis.py](advanced_integrity_analysis.py)

### "Necesito auditar actividades"
→ [auditoria_sistema.py](auditoria_sistema.py)

---

## 📊 Estadísticas

| Métrica | Valor |
|---------|-------|
| Archivos nuevos | 9 |
| Líneas código Python | 2,430 |
| Líneas documentación | 2,021 |
| Total líneas | 4,451 |
| Endpoints totales | 15 |
| Endpoints nuevos | 5 |
| Tablas BD | 4 |
| Dimensiones análisis | 5 |
| Ejemplos cURL | 50+ |

---

## ✅ Validación

**Requisitos Cumplidos:**
- ✅ Fecha en cada análisis
- ✅ Usuario registrado en cada análisis
- ✅ Versión del modelo incluida
- ✅ Prompts usados documentados
- ✅ Temperatura/ajustes registrados
- ✅ Resultados completos
- ✅ Endpoint `/reporte-integridad` implementado
- ✅ Análisis de plagio conceptual
- ✅ Análisis de desviaciones metodológicas
- ✅ Análisis de mala conducta científica
- ✅ Análisis de falacias argumentativas
- ✅ Endpoint `/log-actividad` implementado
- ✅ Auditoría de todas las actividades
- ✅ Documentación completa

---

## 🚀 Próximos Pasos

### Inmediato (Esta semana)
1. [ ] Revisar documentación
2. [ ] Ejecutar demo
3. [ ] Probar endpoints principales

### Corto Plazo (Este mes)
1. [ ] Integración con LMS
2. [ ] Exportación a PDF
3. [ ] Dashboard de auditoría

### Mediano Plazo (Este trimestre)
1. [ ] Machine learning mejorado
2. [ ] Webhooks para alertas
3. [ ] Multi-idioma

---

## 💬 Soporte

Para preguntas sobre:

**Documentación:**
- Abrir archivo correspondiente en editor

**API:**
- Revisar [API_V2_2_GUIA_COMPLETA.md](API_V2_2_GUIA_COMPLETA.md)
- Probar en http://localhost:5000/apidocs/

**Código:**
- Revisar comentarios en archivo fuente
- Consultar [ARQUITECTURA_v2_2.md](ARQUITECTURA_v2_2.md)

**Deployment:**
- Seguir checklist en [ARQUITECTURA_v2_2.md](ARQUITECTURA_v2_2.md)
- Revisar guía de producción

---

## 📋 Tabla de Contenidos Rápida

| Sección | Archivo |
|---------|---------|
| Introducción | v2_2_COMPLETADO.md |
| Endpoints | API_V2_2_GUIA_COMPLETA.md |
| Arquitectura | ARQUITECTURA_v2_2.md |
| Cambios | RESUMEN_CAMBIOS_v2_2.md |
| Ejemplos | EJEMPLOS_CURL_v2_2.md |
| Análisis Integridad | advanced_integrity_analysis.py |
| Auditoría | auditoria_sistema.py |
| API | api_v2_mejorado.py |
| Cliente | cliente_v2_2.py |
| Demo | demo_api_v2_2.py |

---

**Última actualización:** 30 Enero 2025  
**Versión:** 2.2  
**Estado:** ✅ COMPLETADO
