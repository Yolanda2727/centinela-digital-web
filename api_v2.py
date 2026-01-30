"""
API REST Mejorada para Centinela Digital v2.1
Con autenticación, Swagger/OpenAPI, y endpoints adicionales
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
from datetime import datetime, timedelta
import uuid
import json
import traceback
import jwt
from functools import wraps
from typing import Dict, Tuple

from improved_analysis_model import analyze_with_improved_model
from database import CentinelaDatabase
from institutional_metrics import InstitucionalMetrics

# ============================================================
# CONFIGURACIÓN
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'centinela-digital-secret-2025'  # Cambiar en producción
CORS(app)

# Inicializar Swagger para documentación automática
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Centinela Digital API",
        "description": "Sistema de detección de fraude académico",
        "version": "2.1"
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http", "https"]
})

db = CentinelaDatabase()

# Usuarios de demostración (en producción usar BD)
DEMO_USERS = {
    "admin": "admin123",
    "usuario": "user123"
}

# ============================================================
# AUTENTICACIÓN
# ============================================================

def token_required(f):
    """Decorador para proteger endpoints con token JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({
                'error': 'Token faltante',
                'code': 'NO_TOKEN'
            }), 401
        
        try:
            # Extraer token de "Bearer <token>"
            token = token.split(' ')[1] if ' ' in token else token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user = data
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


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Autenticarse y obtener token JWT
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            username:
              type: string
              example: admin
            password:
              type: string
              example: admin123
    responses:
      200:
        description: Login exitoso
        schema:
          properties:
            token:
              type: string
              example: eyJ0eXAiOiJKV1QiLCJhbGc...
            usuario:
              type: string
      401:
        description: Credenciales inválidas
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            'error': 'Usuario y contraseña requeridos',
            'code': 'MISSING_CREDENTIALS'
        }), 400
    
    if username not in DEMO_USERS or DEMO_USERS[username] != password:
        return jsonify({
            'error': 'Credenciales inválidas',
            'code': 'INVALID_CREDENTIALS'
        }), 401
    
    # Generar token JWT (válido por 24 horas)
    token = jwt.encode({
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'token': token,
        'usuario': username,
        'mensaje': 'Login exitoso'
    }), 200


@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Registrar nuevo usuario (demo)
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
            email:
              type: string
    responses:
      201:
        description: Usuario creado
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password:
        return jsonify({
            'error': 'Usuario y contraseña requeridos',
            'code': 'MISSING_FIELDS'
        }), 400
    
    if username in DEMO_USERS:
        return jsonify({
            'error': 'Usuario ya existe',
            'code': 'USER_EXISTS'
        }), 409
    
    # En producción, hashear contraseña y guardar en BD
    DEMO_USERS[username] = password
    
    return jsonify({
        'mensaje': 'Usuario creado exitosamente',
        'username': username,
        'email': email
    }), 201


# ============================================================
# RUTAS DE SALUD
# ============================================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Verificar que la API está disponible
    ---
    responses:
      200:
        description: API sana
        schema:
          properties:
            status:
              type: string
              example: healthy
            timestamp:
              type: string
            version:
              type: string
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.1'
    }), 200


# ============================================================
# RUTAS DE ANÁLISIS
# ============================================================

@app.route('/api/analyze', methods=['POST'])
@token_required
def analyze():
    """
    Analizar un documento para detectar fraude académico
    ---
    security:
      - Bearer: []
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "Bearer token (obtener en /api/auth/login)"
      - name: body
        in: body
        required: true
        schema:
          properties:
            rol:
              type: string
              example: Estudiante
            tipo_producto:
              type: string
              example: Ensayo
            evidencias:
              type: object
              properties:
                estilo_diferente:
                  type: integer
                tiempo_sospechoso:
                  type: integer
    responses:
      201:
        description: Análisis completado
      401:
        description: No autorizado
      400:
        description: Datos inválidos
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'code': 'INVALID_REQUEST'
            }), 400
        
        rol = data.get('rol', 'Estudiante')
        tipo_producto = data.get('tipo_producto', 'Ensayo')
        evidencias = data.get('evidencias', {})
        
        # Validación
        valid_roles = ['Estudiante', 'Docente-investigador', 'Coinvestigador externo']
        if rol not in valid_roles:
            rol = 'Estudiante'
        
        # Asegurar todas las evidencias
        evidencias_default = {
            'estilo_diferente': 0,
            'defensa_debil': 0,
            'tiempo_sospechoso': 0,
            'sin_borradores': 0,
            'referencias_raras': 0,
            'datos_inconsistentes': 0,
            'imagenes_sospechosas': 0
        }
        evidencias_default.update(evidencias)
        
        num_evidencias = sum(1 for v in evidencias_default.values() if v > 0)
        
        # Ejecutar análisis
        resultado = analyze_with_improved_model(
            evidencias=evidencias_default,
            rol=rol,
            tipo_producto=tipo_producto,
            num_evidencias_marked=num_evidencias
        )
        
        # Generar ID único
        case_id = f"case_{uuid.uuid4().hex[:12]}"
        
        # Guardar en BD
        case_data = {
            'caso_id': case_id,
            'rol': rol,
            'tipo_producto': tipo_producto,
            'riesgo_score': resultado['overall_score'],
            'nivel_riesgo': resultado['overall_level'],
            'confianza': resultado['confidence'],
            'timestamp': datetime.now().isoformat(),
            'num_evidencias': num_evidencias,
            'usuario': request.user.get('username', 'anónimo')
        }
        
        db.guardar_caso(case_data)
        
        return jsonify({
            'status': 'success',
            'case_id': case_id,
            'analysis': {
                'overall_score': resultado['overall_score'],
                'overall_level': resultado['overall_level'],
                'confidence': resultado['confidence'],
                'recommendations': resultado.get('recommendations', [])
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'code': 'ANALYSIS_ERROR'
        }), 500


@app.route('/api/case/<case_id>', methods=['GET'])
@token_required
def get_case(case_id):
    """
    Obtener detalles de un caso específico
    ---
    security:
      - Bearer: []
    parameters:
      - name: case_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Caso encontrado
      404:
        description: Caso no encontrado
    """
    try:
        caso = db.obtener_caso(case_id)
        
        if not caso:
            return jsonify({
                'error': 'Case not found',
                'code': 'NOT_FOUND'
            }), 404
        
        return jsonify({
            'status': 'success',
            'case': caso
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'code': 'QUERY_ERROR'
        }), 500


@app.route('/api/cases', methods=['GET'])
@token_required
def list_cases():
    """
    Listar casos con filtros opcionales
    ---
    security:
      - Bearer: []
    parameters:
      - name: limit
        in: query
        type: integer
        default: 50
      - name: offset
        in: query
        type: integer
        default: 0
      - name: nivel
        in: query
        type: string
        description: "ALTO, MEDIO, BAJO"
      - name: rol
        in: query
        type: string
    responses:
      200:
        description: Lista de casos
    """
    try:
        nivel = request.args.get('nivel', None)
        rol = request.args.get('rol', None)
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        casos_raw = db.listar_casos(limite=limit + offset)
        casos_paginated = casos_raw[offset:offset+limit]
        
        return jsonify({
            'status': 'success',
            'total': len(casos_raw),
            'returned': len(casos_paginated),
            'cases': casos_paginated
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'code': 'QUERY_ERROR'
        }), 500


# ============================================================
# RUTAS DE BATCH ANALYSIS
# ============================================================

@app.route('/api/batch/analyze', methods=['POST'])
@token_required
def batch_analyze():
    """
    Analizar múltiples documentos en lote
    ---
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            casos:
              type: array
              items:
                type: object
    responses:
      200:
        description: Análisis completado
    """
    try:
        data = request.get_json()
        casos = data.get('casos', [])
        
        if not casos:
            return jsonify({
                'error': 'No casos provided',
                'code': 'INVALID_REQUEST'
            }), 400
        
        resultados = []
        
        for caso in casos:
            try:
                rol = caso.get('rol', 'Estudiante')
                tipo_producto = caso.get('tipo_producto', 'Ensayo')
                evidencias = caso.get('evidencias', {})
                
                evidencias_default = {
                    'estilo_diferente': 0,
                    'defensa_debil': 0,
                    'tiempo_sospechoso': 0,
                    'sin_borradores': 0,
                    'referencias_raras': 0,
                    'datos_inconsistentes': 0,
                    'imagenes_sospechosas': 0
                }
                evidencias_default.update(evidencias)
                
                resultado = analyze_with_improved_model(
                    evidencias=evidencias_default,
                    rol=rol,
                    tipo_producto=tipo_producto,
                    num_evidencias_marked=sum(1 for v in evidencias_default.values() if v > 0)
                )
                
                resultados.append({
                    'status': 'success',
                    'score': resultado['overall_score'],
                    'level': resultado['overall_level']
                })
            
            except Exception as e:
                resultados.append({
                    'status': 'error',
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'total': len(casos),
            'procesados': len([r for r in resultados if r['status'] == 'success']),
            'resultados': resultados
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'code': 'BATCH_ERROR'
        }), 500


# ============================================================
# RUTAS DE MÉTRICAS
# ============================================================

@app.route('/api/metrics/institutional', methods=['GET'])
@token_required
def metrics_institutional():
    """
    Obtener métricas institucionales
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Métricas calculadas
    """
    try:
        casos_raw = db.listar_casos()
        
        if casos_raw:
            reporte = InstitucionalMetrics.generar_reporte_ejecutivo(casos_raw)
            return jsonify({
                'status': 'success',
                'metrics': reporte
            }), 200
        else:
            return jsonify({
                'status': 'success',
                'metrics': {
                    'total_casos': 0
                }
            }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'code': 'METRICS_ERROR'
        }), 500


@app.route('/api/metrics/temporal', methods=['GET'])
@token_required
def metrics_temporal():
    """
    Obtener análisis de evolución temporal
    ---
    security:
      - Bearer: []
    parameters:
      - name: period
        in: query
        type: string
        default: daily
        description: "daily, weekly, monthly"
    responses:
      200:
        description: Análisis temporal
    """
    try:
        period = request.args.get('period', 'daily')
        casos_raw = db.listar_casos()
        
        if period == 'daily':
            temporal = InstitucionalMetrics.analizar_evolucion_temporal(casos_raw, agrupacion="diaria")
        elif period == 'weekly':
            temporal = InstitucionalMetrics.analizar_evolucion_temporal(casos_raw, agrupacion="semanal")
        elif period == 'monthly':
            temporal = InstitucionalMetrics.analizar_evolucion_temporal(casos_raw, agrupacion="mensual")
        else:
            temporal = {}
        
        return jsonify({
            'status': 'success',
            'period': period,
            'data': temporal
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'code': 'TEMPORAL_ERROR'
        }), 500


# ============================================================
# RUTAS DE INFORMACIÓN
# ============================================================

@app.route('/api/info', methods=['GET'])
def info():
    """
    Información de la API
    ---
    responses:
      200:
        description: Información general
    """
    return jsonify({
        'name': 'Centinela Digital API',
        'version': '2.1',
        'description': 'Sistema de detección de fraude académico',
        'endpoints': {
            'auth': {
                'POST /api/auth/login': 'Obtener token',
                'POST /api/auth/register': 'Registrar usuario'
            },
            'analysis': {
                'POST /api/analyze': 'Analizar documento',
                'POST /api/batch/analyze': 'Analizar múltiples documentos',
                'GET /api/case/<id>': 'Obtener caso',
                'GET /api/cases': 'Listar casos'
            },
            'metrics': {
                'GET /api/metrics/institutional': 'Métricas agregadas',
                'GET /api/metrics/temporal': 'Evolución temporal'
            },
            'info': {
                'GET /api/info': 'Información API',
                'GET /health': 'Health check',
                'GET /apidocs': 'Swagger UI'
            }
        }
    }), 200


@app.route('/api/documentation', methods=['GET'])
def documentation():
    """Documentación en formato OpenAPI/Swagger"""
    return jsonify({
        'swagger': '2.0',
        'info': {
            'title': 'Centinela Digital API',
            'version': '2.1'
        }
    }), 200


# ============================================================
# MANEJO DE ERRORES
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint no encontrado',
        'code': 'NOT_FOUND'
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'error': 'Error interno del servidor',
        'code': 'SERVER_ERROR'
    }), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Centinela Digital API v2.1")
    print("="*70)
    print("\n📚 Documentación Swagger: http://localhost:5000/apidocs")
    print("🔐 Login: POST http://localhost:5000/api/auth/login")
    print("   Usuario: admin / Contraseña: admin123")
    print("\n" + "="*70 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
