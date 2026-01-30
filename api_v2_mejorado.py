"""
API REST Centinela Digital v2.2 - MEJORADA
Con autenticación JWT, análisis de integridad, auditoría completa
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
from datetime import datetime, timedelta
import uuid
import json
import hashlib
import time
from functools import wraps
from typing import Dict, Tuple, Optional

from improved_analysis_model import analyze_with_improved_model
from database import CentinelaDatabase
from institutional_metrics import InstitucionalMetrics
from advanced_integrity_analysis import AnálisisIntegridad, AnálisisConMetadatos
from auditoria_sistema import auditoria

import jwt

# ============================================================
# CONFIGURACIÓN
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'centinela-digital-secret-2025'  # CAMBIAR EN PRODUCCIÓN
CORS(app)

swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Centinela Digital API v2.2",
        "description": "Sistema avanzado de detección de fraude académico con auditoría",
        "version": "2.2"
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http", "https"]
})

db = CentinelaDatabase()
metrics = InstitucionalMetrics()

# Usuarios de demostración
DEMO_USERS = {
    "admin": "admin123",
    "profesor": "prof123",
    "estudiante": "estud123"
}

# ============================================================
# AUTENTICACIÓN JWT
# ============================================================

def token_required(f):
    """Decorador para proteger endpoints con token JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            auditoria.crear_alerta(
                "MEDIO",
                "intento_acceso_sin_token",
                f"Intento de acceso sin token a {request.path}",
                "desconocido"
            )
            return jsonify({
                'error': 'Token faltante',
                'code': 'NO_TOKEN'
            }), 401
        
        try:
            token = token.split(' ')[1] if ' ' in token else token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user = data
            request.user_id = data.get('user_id')
        except jwt.ExpiredSignatureError:
            return jsonify({
                'error': 'Token expirado',
                'code': 'TOKEN_EXPIRED'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'error': 'Token inválido',
                'code': 'INVALID_TOKEN'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated


# ============================================================
# ENDPOINTS DE AUTENTICACIÓN
# ============================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Obtener token JWT
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Token generado
      401:
        description: Credenciales inválidas
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        auditoria.crear_alerta("BAJO", "login_incompleto", "Intento de login sin credenciales", username)
        return jsonify({'error': 'Credenciales faltantes'}), 400
    
    if username in DEMO_USERS and DEMO_USERS[username] == password:
        token = jwt.encode({
            'user_id': username,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        auditoria.registrar_actividad(
            username, "login", "/api/auth/login", "POST",
            estado="exitosa"
        )
        
        return jsonify({
            'token': token,
            'usuario': username,
            'expira_en': 86400
        }), 200
    
    auditoria.crear_alerta("MEDIO", "login_fallido", f"Intento fallido de login para {username}", username)
    return jsonify({'error': 'Credenciales inválidas'}), 401


@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Registrar nuevo usuario
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      201:
        description: Usuario registrado
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Datos faltantes'}), 400
    
    if username in DEMO_USERS:
        return jsonify({'error': 'Usuario ya existe'}), 409
    
    DEMO_USERS[username] = password
    
    auditoria.registrar_actividad(
        username, "register", "/api/auth/register", "POST",
        estado="exitosa"
    )
    
    return jsonify({
        'mensaje': 'Usuario registrado exitosamente',
        'usuario': username
    }), 201


# ============================================================
# ENDPOINTS DE ANÁLISIS MEJORADO
# ============================================================

@app.route('/api/analyze', methods=['POST'])
@token_required
def analyze():
    """
    Analizar documento
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            contenido:
              type: string
            tipo_documento:
              type: string
            rol:
              type: string
            temperatura:
              type: number
            prompts:
              type: array
    responses:
      200:
        description: Análisis completo con metadatos
    """
    data = request.json
    contenido = data.get('contenido')
    tipo_documento = data.get('tipo_documento', 'general')
    rol = data.get('rol', 'Estudiante')
    temperatura = data.get('temperatura', 0.7)
    prompts_usados = data.get('prompts', [])
    
    start_time = time.time()
    
    if not contenido:
        return jsonify({'error': 'Contenido faltante'}), 400
    
    try:
        # Análisis completo con metadatos
        analisis = AnálisisConMetadatos.crear_análisis_completo(
            contenido={'contenido': contenido, 'tipo_documento': tipo_documento},
            usuario=request.user_id,
            version_modelo='2.2',
            temperatura=temperatura,
            prompts_usados=prompts_usados
        )
        
        # Guardar en BD
        doc_hash = hashlib.sha256(contenido.encode()).hexdigest()
        
        # Registrar en auditoría
        duracion = int((time.time() - start_time) * 1000)
        auditoria.registrar_análisis(
            usuario=request.user_id,
            tipo_documento=tipo_documento,
            rol_autor=rol,
            version_modelo='2.2',
            temperatura=temperatura,
            score_general=analisis['análisis']['score_general'],
            nivel_riesgo=analisis['análisis']['nivel_riesgo'],
            recomendaciones=analisis['análisis']['recomendaciones'],
            documento_hash=doc_hash,
            duracion_ms=duracion
        )
        
        auditoria.registrar_actividad(
            request.user_id, "análisis_simple", "/api/analyze", "POST",
            estado="exitosa",
            detalles={'tipo_documento': tipo_documento, 'rol': rol},
            resultado=analisis['análisis']['nivel_riesgo'],
            duracion_ms=duracion
        )
        
        return jsonify(analisis), 200
    
    except Exception as e:
        auditoria.crear_alerta(
            "ALTO",
            "error_análisis",
            f"Error en análisis: {str(e)}",
            request.user_id
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/reporte-integridad', methods=['POST'])
@token_required
def reporte_integridad():
    """
    Análisis avanzado de integridad científica
    Detecta: plagio conceptual, desviaciones metodológicas, 
    mala conducta científica, fabricación de datos, falacias
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            contenido:
              type: string
            rol:
              type: string
    responses:
      200:
        description: Reporte completo de integridad
    """
    data = request.json
    contenido = data.get('contenido')
    rol = data.get('rol', 'Investigador')
    
    if not contenido:
        return jsonify({'error': 'Contenido faltante'}), 400
    
    start_time = time.time()
    
    try:
        documento = {
            'contenido': contenido,
            'tipo_documento': 'investigación',
            'rol': rol
        }
        
        # Análisis de integridad completo
        análisis = AnálisisIntegridad.analizar_integridad_completa(documento, rol)
        
        duracion = int((time.time() - start_time) * 1000)
        
        # Registrar en auditoría
        doc_hash = hashlib.sha256(contenido.encode()).hexdigest()
        
        if análisis['nivel_riesgo'] in ['CRÍTICO', 'ALTO']:
            auditoria.crear_alerta(
                "CRÍTICO",
                "riesgo_integridad",
                f"Riesgo de integridad detectado: {análisis['nivel_riesgo']}",
                request.user_id
            )
        
        auditoria.registrar_análisis(
            usuario=request.user_id,
            tipo_documento='investigación',
            rol_autor=rol,
            version_modelo='2.2-integrity',
            temperatura=0.8,
            score_general=análisis['score_general'],
            nivel_riesgo=análisis['nivel_riesgo'],
            recomendaciones=análisis['recomendaciones'],
            documento_hash=doc_hash,
            duracion_ms=duracion
        )
        
        auditoria.registrar_actividad(
            request.user_id, "análisis_integridad", "/api/reporte-integridad", "POST",
            estado="exitosa",
            resultado=análisis['nivel_riesgo'],
            duracion_ms=duracion
        )
        
        return jsonify({
            'metadatos': {
                'fecha': datetime.now().isoformat(),
                'usuario': request.user_id,
                'version_modelo': '2.2-integrity',
                'duracion_ms': duracion
            },
            'análisis': análisis,
            'hallazgos_detallados': {
                'plagio_conceptual': análisis['plagio_conceptual'],
                'desviaciones_metodologicas': análisis['desviaciones_metodologicas'],
                'mala_conducta': análisis['mala_conducta'],
                'falacias': análisis['falacias']
            }
        }), 200
    
    except Exception as e:
        auditoria.crear_alerta(
            "ALTO",
            "error_integridad",
            f"Error en análisis de integridad: {str(e)}",
            request.user_id
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch/analyze', methods=['POST'])
@token_required
def batch_analyze():
    """
    Analizar múltiples documentos en lote
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            documentos:
              type: array
              items:
                properties:
                  contenido:
                    type: string
                  tipo_documento:
                    type: string
                  rol:
                    type: string
    responses:
      200:
        description: Análisis de todos los documentos
    """
    data = request.json
    documentos = data.get('documentos', [])
    
    if not documentos:
        return jsonify({'error': 'No hay documentos para analizar'}), 400
    
    start_time = time.time()
    resultados = []
    
    try:
        for i, doc in enumerate(documentos):
            contenido = doc.get('contenido')
            if not contenido:
                resultados.append({
                    'índice': i,
                    'error': 'Contenido faltante'
                })
                continue
            
            tipo_documento = doc.get('tipo_documento', 'general')
            rol = doc.get('rol', 'Estudiante')
            
            análisis = AnálisisConMetadatos.crear_análisis_completo(
                contenido={'contenido': contenido, 'tipo_documento': tipo_documento},
                usuario=request.user_id,
                version_modelo='2.2',
                temperatura=0.7,
                prompts_usados=[]
            )
            
            resultados.append({
                'índice': i,
                'análisis': análisis['análisis'],
                'score_general': análisis['resultados']['score_general'],
                'nivel_riesgo': análisis['resultados']['nivel_riesgo']
            })
        
        duracion = int((time.time() - start_time) * 1000)
        
        auditoria.registrar_actividad(
            request.user_id, "análisis_batch", "/api/batch/analyze", "POST",
            estado="exitosa",
            detalles={'documentos_procesados': len(documentos)},
            resultado=f"{len(resultados)} documentos analizados",
            duracion_ms=duracion
        )
        
        return jsonify({
            'metadatos': {
                'fecha': datetime.now().isoformat(),
                'usuario': request.user_id,
                'documentos_procesados': len(documentos),
                'duracion_ms': duracion
            },
            'resultados': resultados
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# ENDPOINTS DE AUDITORÍA Y LOG
# ============================================================

@app.route('/api/log-actividad', methods=['GET'])
@token_required
def log_actividad():
    """
    Obtener historial de actividades
    ---
    parameters:
      - name: usuario
        in: query
        type: string
      - name: tipo
        in: query
        type: string
      - name: días
        in: query
        type: integer
      - name: límite
        in: query
        type: integer
    responses:
      200:
        description: Historial de actividades
    """
    usuario_filtro = request.args.get('usuario', request.user_id)
    tipo_filtro = request.args.get('tipo')
    días = int(request.args.get('días', 30))
    límite = int(request.args.get('límite', 100))
    
    # Verificar permisos
    if usuario_filtro != request.user_id and request.user_id != 'admin':
        auditoria.crear_alerta(
            "MEDIO",
            "acceso_no_autorizado",
            f"Intento de acceso al log de {usuario_filtro}",
            request.user_id
        )
        return jsonify({'error': 'No autorizado'}), 403
    
    actividades = auditoria.obtener_log_actividad(
        usuario=usuario_filtro,
        tipo_actividad=tipo_filtro,
        dias=días,
        limite=límite
    )
    
    auditoria.registrar_actividad(
        request.user_id, "consulta_log", "/api/log-actividad", "GET",
        estado="exitosa",
        resultado=f"{len(actividades)} registros"
    )
    
    return jsonify({
        'fecha': datetime.now().isoformat(),
        'usuario': usuario_filtro,
        'total_registros': len(actividades),
        'actividades': actividades
    }), 200


@app.route('/api/auditoria/usuario/<usuario>', methods=['GET'])
@token_required
def reporte_auditoria_usuario(usuario: str):
    """
    Obtener reporte de auditoría de un usuario
    ---
    responses:
      200:
        description: Reporte completo de auditoría
    """
    # Verificar permisos
    if usuario != request.user_id and request.user_id != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    reporte = auditoria.generar_reporte_auditoria(usuario)
    
    auditoria.registrar_actividad(
        request.user_id, "reporte_auditoria", f"/api/auditoria/usuario/{usuario}", "GET",
        estado="exitosa"
    )
    
    return jsonify(reporte), 200


@app.route('/api/auditoria/análisis', methods=['GET'])
@token_required
def auditoría_análisis():
    """
    Obtener historial de análisis realizados
    ---
    responses:
      200:
        description: Historial de análisis
    """
    usuario = request.args.get('usuario', request.user_id)
    días = int(request.args.get('días', 30))
    límite = int(request.args.get('límite', 50))
    
    if usuario != request.user_id and request.user_id != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    análisis = auditoria.obtener_análisis_usuario(usuario, días, límite)
    
    return jsonify({
        'fecha': datetime.now().isoformat(),
        'usuario': usuario,
        'total_análisis': len(análisis),
        'análisis': análisis
    }), 200


@app.route('/api/auditoria/cambios-sensibles', methods=['GET'])
@token_required
def auditoría_cambios():
    """
    Obtener historial de cambios sensibles (admin)
    ---
    responses:
      200:
        description: Cambios sensibles registrados
    """
    if request.user_id != 'admin':
        auditoria.crear_alerta(
            "MEDIO",
            "acceso_no_autorizado",
            f"Intento de acceso a cambios sensibles",
            request.user_id
        )
        return jsonify({'error': 'No autorizado. Solo administrador'}), 403
    
    cambios = auditoria.obtener_cambios_sensibles(
        tipo_cambio=request.args.get('tipo'),
        días=int(request.args.get('días', 30))
    )
    
    return jsonify({
        'fecha': datetime.now().isoformat(),
        'total_cambios': len(cambios),
        'cambios': cambios
    }), 200


@app.route('/api/auditoria/alertas', methods=['GET'])
@token_required
def auditoría_alertas():
    """
    Obtener alertas del sistema
    ---
    responses:
      200:
        description: Alertas activas
    """
    if request.user_id != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    resuelta = request.args.get('resuelta', 'false').lower() == 'true'
    nivel = request.args.get('nivel')
    
    alertas = auditoria.obtener_alertas(resuelta=resuelta, nivel=nivel)
    
    return jsonify({
        'fecha': datetime.now().isoformat(),
        'total_alertas': len(alertas),
        'alertas': alertas
    }), 200


# ============================================================
# ENDPOINTS DE INFORMACIÓN Y DOCUMENTACIÓN
# ============================================================

@app.route('/api/info', methods=['GET'])
def info():
    """
    Información del API
    ---
    responses:
      200:
        description: Versión e información
    """
    return jsonify({
        'nombre': 'Centinela Digital API',
        'versión': '2.2',
        'descripción': 'Sistema avanzado de detección de fraude académico',
        'características': [
            'Análisis de integridad científica',
            'Detección de plagio conceptual',
            'Análisis de falacias argumentativas',
            'Auditoría completa de actividades',
            'Autenticación JWT',
            'Procesamiento en lote'
        ],
        'endpoints': 15
    }), 200


@app.route('/api/metrics/institutional', methods=['GET'])
@token_required
def metricas_institucionales():
    """
    Obtener métricas institucionales
    ---
    responses:
      200:
        description: Métricas agregadas
    """
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'métricas': metrics.calculate_metrics()
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """
    Estado del API
    ---
    responses:
      200:
        description: API funcional
    """
    return jsonify({
        'estado': 'operativo',
        'timestamp': datetime.now().isoformat(),
        'versión': '2.2'
    }), 200


@app.route('/apidocs', methods=['GET'])
def documentación():
    """Documentación Swagger"""
    return jsonify({'mensaje': 'Acceder a /apidocs/'})


# ============================================================
# MANEJO DE ERRORES
# ============================================================

@app.errorhandler(404)
def no_encontrado(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404


@app.errorhandler(500)
def error_interno(error):
    auditoria.crear_alerta("CRÍTICO", "error_servidor", str(error), "sistema")
    return jsonify({'error': 'Error interno del servidor'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
