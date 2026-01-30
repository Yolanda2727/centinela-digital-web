"""
API REST para Centinela Digital v2.0
Endpoints para análisis de fraude académico
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid
import json
import traceback

from improved_analysis_model import analyze_with_improved_model
from database import CentinelaDatabase
from institutional_metrics import InstitucionalMetrics

# ============================================================
# INICIALIZACIÓN
# ============================================================

app = Flask(__name__)
CORS(app)
db = CentinelaDatabase()

# ============================================================
# RUTAS DE SALUD
# ============================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Verificar que la API está disponible"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    }), 200


# ============================================================
# RUTAS DE ANÁLISIS
# ============================================================

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analizar un documento/texto para detectar fraude académico
    
    Request JSON:
    {
        "texto": "contenido del documento",
        "metadata": {
            "rol": "Estudiante",  # Estudiante, Docente-investigador, Coinvestigador externo
            "tipo_producto": "Ensayo",  # Ensayo, Tesis, Artículo, etc.
            "titulo": "opcional",
            "autor": "opcional"
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
    """
    try:
        data = request.get_json()
        
        # Validar que hay datos
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'code': 'INVALID_REQUEST'
            }), 400
        
        # Extraer campos
        texto = data.get('texto', '')
        metadata = data.get('metadata', {})
        evidencias = data.get('evidencias', {})
        
        # Validar texto
        if not texto or len(texto.strip()) < 50:
            return jsonify({
                'error': 'Text must be at least 50 characters',
                'code': 'INVALID_TEXT'
            }), 400
        
        # Valores por defecto
        rol = metadata.get('rol', 'Estudiante')
        tipo_producto = metadata.get('tipo_producto', 'Ensayo')
        
        # Validar rol y tipo
        valid_roles = ['Estudiante', 'Docente-investigador', 'Coinvestigador externo']
        valid_tipos = ['Ensayo', 'Tesis', 'Artículo científico', 'Informe técnico', 
                      'Trabajo de curso', 'Proyecto de grado', 'Otro']
        
        if rol not in valid_roles:
            rol = 'Estudiante'
        if tipo_producto not in valid_tipos:
            tipo_producto = 'Ensayo'
        
        # Asegurar que todas las evidencias existan con valores por defecto
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
        
        # Contar evidencias marcadas
        num_evidencias = sum(1 for v in evidencias_default.values() if v > 0)
        
        # Ejecutar análisis mejorado
        resultado = analyze_with_improved_model(
            evidencias=evidencias_default,
            rol=rol,
            tipo_producto=tipo_producto,
            num_evidencias_marked=num_evidencias
        )
        
        # Generar ID único para el caso
        case_id = f"case_{uuid.uuid4().hex[:12]}"
        
        # Preparar datos para guardar en BD
        case_data = {
            'caso_id': case_id,
            'rol': rol,
            'tipo_producto': tipo_producto,
            'riesgo_score': resultado['overall_score'],
            'nivel_riesgo': resultado['overall_level'],
            'confianza': resultado['confidence'],
            'timestamp': datetime.now().isoformat(),
            'num_evidencias': num_evidencias,
            'texto_length': len(texto),
            'sentimiento': 'neutral',
            'json_data': {
                'titulo': metadata.get('titulo', 'Sin título'),
                'autor': metadata.get('autor', 'Anónimo'),
                'evidencias': evidencias_default,
                'recomendaciones': resultado.get('recommendations', []),
                'dimensiones': resultado.get('dimensions', {})
            }
        }
        
        # Guardar en base de datos
        db.guardar_caso(case_data)
        
        return jsonify({
            'status': 'success',
            'case_id': case_id,
            'analysis': {
                'overall_score': resultado['overall_score'],
                'overall_level': resultado['overall_level'],
                'confidence': resultado['confidence'],
                'recommendations': resultado.get('recommendations', []),
                'dimensions': resultado.get('dimensions', {})
            },
            'metadata': {
                'text_length': len(texto),
                'num_evidencias': num_evidencias,
                'analyzed_at': datetime.now().isoformat()
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'code': 'ANALYSIS_ERROR',
            'traceback': traceback.format_exc() if app.debug else None
        }), 500


# ============================================================
# RUTAS DE CONSULTA
# ============================================================

@app.route('/api/case/<case_id>', methods=['GET'])
def get_case(case_id):
    """Obtener un caso específico por ID"""
    try:
        caso = db.obtener_caso(case_id)
        if not caso:
            return jsonify({
                'error': 'Case not found',
                'code': 'NOT_FOUND',
                'case_id': case_id
            }), 404
        
        # El caso ya es un diccionario
        if isinstance(caso, dict):
            caso_dict = {
                'case_id': caso.get('caso_id'),
                'title': caso.get('json_data', {}).get('titulo'),
                'author': caso.get('json_data', {}).get('autor'),
                'role': caso.get('rol'),
                'product_type': caso.get('tipo_producto'),
                'overall_score': caso.get('riesgo_score'),
                'overall_level': caso.get('nivel_riesgo'),
                'confidence': caso.get('confianza'),
                'analyzed_at': caso.get('timestamp')
            }
        else:
            caso_dict = caso
        
        return jsonify({
            'status': 'success',
            'case': caso_dict
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'code': 'QUERY_ERROR'
        }), 500


@app.route('/api/cases', methods=['GET'])
def list_cases():
    """Listar casos con filtros opcionales"""
    try:
        # Parámetros de filtro
        nivel = request.args.get('nivel', None)
        rol = request.args.get('rol', None)
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Obtener casos
        casos_raw = db.listar_casos(
            filtro_nivel=nivel,
            filtro_rol=rol,
            limite=limit + offset
        )
        
        # Aplicar paginación
        casos_paginated = casos_raw[offset:offset+limit]
        
        # Convertir a diccionarios
        casos_list = []
        for caso_data in casos_paginated:
            # El dato viene como JSON string
            if isinstance(caso_data, tuple):
                caso = json.loads(caso_data[0])
            else:
                caso = caso_data if isinstance(caso_data, dict) else json.loads(caso_data)
            
            casos_list.append({
                'case_id': caso.get('caso_id'),
                'title': caso.get('json_data', {}).get('titulo'),
                'author': caso.get('json_data', {}).get('autor'),
                'role': caso.get('rol'),
                'product_type': caso.get('tipo_producto'),
                'overall_score': caso.get('riesgo_score'),
                'overall_level': caso.get('nivel_riesgo'),
                'confidence': caso.get('confianza'),
                'analyzed_at': caso.get('timestamp')
            })
        
        return jsonify({
            'status': 'success',
            'total': len(casos_raw),
            'returned': len(casos_list),
            'limit': limit,
            'offset': offset,
            'cases': casos_list,
            'filters': {
                'nivel': nivel,
                'rol': rol
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'code': 'QUERY_ERROR'
        }), 500


# ============================================================
# RUTAS DE MÉTRICAS E INFORMES
# ============================================================

@app.route('/api/metrics/institutional', methods=['GET'])
def metrics_institutional():
    """Obtener métricas institucionales"""
    try:
        # Obtener todos los casos de la BD
        casos_raw = db.listar_casos()
        
        # Convertir a diccionarios
        casos_list = []
        for caso_data in casos_raw:
            if isinstance(caso_data, tuple):
                caso = json.loads(caso_data[0])
            else:
                caso = caso_data if isinstance(caso_data, dict) else json.loads(caso_data)
            casos_list.append(caso)
        
        # Generar reporte
        if casos_list:
            reporte = InstitucionalMetrics.generar_reporte_ejecutivo(casos_list)
            return jsonify({
                'status': 'success',
                'metrics': reporte
            }), 200
        else:
            return jsonify({
                'status': 'success',
                'metrics': {
                    'total_casos': 0,
                    'tasa_riesgo': {'ALTO': 0.0, 'MEDIO': 0.0, 'BAJO': 0.0},
                    'promedio_score': 0,
                    'confianza_promedio': 0
                }
            }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'code': 'METRICS_ERROR'
        }), 500


@app.route('/api/metrics/temporal', methods=['GET'])
def metrics_temporal():
    """Obtener análisis temporal"""
    try:
        period = request.args.get('period', 'daily')
        
        # Obtener todos los casos de la BD
        casos_raw = db.listar_casos()
        
        # Convertir a diccionarios
        casos_list = []
        for caso_data in casos_raw:
            if isinstance(caso_data, tuple):
                caso = json.loads(caso_data[0])
            else:
                caso = caso_data if isinstance(caso_data, dict) else json.loads(caso_data)
            casos_list.append(caso)
        
        # Generar análisis temporal
        if period == 'daily':
            temporal = InstitucionalMetrics.analizar_evolucion_temporal(casos_list, agrupacion="diaria")
        elif period == 'weekly':
            temporal = InstitucionalMetrics.analizar_evolucion_temporal(casos_list, agrupacion="semanal")
        elif period == 'monthly':
            temporal = InstitucionalMetrics.analizar_evolucion_temporal(casos_list, agrupacion="mensual")
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
    """Información de la API y opciones válidas"""
    return jsonify({
        'name': 'Centinela Digital API',
        'version': '2.0',
        'description': 'API para detección de fraude académico',
        'valid_roles': ['Estudiante', 'Docente-investigador', 'Coinvestigador externo'],
        'valid_product_types': ['Ensayo', 'Tesis', 'Artículo científico', 'Informe técnico', 
                               'Trabajo de curso', 'Proyecto de grado', 'Otro'],
        'valid_evidences': [
            'estilo_diferente',
            'defensa_debil',
            'tiempo_sospechoso',
            'sin_borradores',
            'referencias_raras',
            'datos_inconsistentes',
            'imagenes_sospechosas'
        ],
        'endpoints': {
            'POST /api/analyze': 'Analizar un documento',
            'GET /api/case/<id>': 'Obtener un caso',
            'GET /api/cases': 'Listar casos con filtros',
            'GET /api/metrics/institutional': 'Métricas institucionales',
            'GET /api/metrics/temporal': 'Análisis temporal',
            'GET /health': 'Verificar salud de API'
        }
    }), 200


# ============================================================
# MANEJO DE ERRORES
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'code': 'NOT_FOUND',
        'status': 404
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'error': 'Internal server error',
        'code': 'SERVER_ERROR',
        'status': 500
    }), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    # En desarrollo
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
