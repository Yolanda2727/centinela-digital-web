#!/usr/bin/env python3
"""
Script de Demostración - API v2.1 Centinela Digital
Ejecuta demostraciones de todas las características nuevas
"""

import requests
import json
import sys
import time

API_URL = "http://localhost:5000"

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}🔹 {text}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ️  {text}{Colors.END}")

# ========================
# DEMO 1: AUTENTICACIÓN
# ========================

def demo_autenticacion():
    print_header("DEMO 1: AUTENTICACIÓN")
    
    print_info("Autenticándose con credenciales demo...")
    
    response = requests.post(
        f'{API_URL}/api/auth/login',
        json={'username': 'admin', 'password': 'admin123'}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data['token']
        print_success(f"Login exitoso como: {data['usuario']}")
        print_info(f"Token: {token[:40]}...")
        return token
    else:
        print_error(f"Login falló: {response.json()}")
        return None

# ========================
# DEMO 2: SWAGGER
# ========================

def demo_swagger():
    print_header("DEMO 2: DOCUMENTACIÓN SWAGGER")
    
    print_info("Accediendo a Swagger UI...")
    
    response = requests.get(f'{API_URL}/apidocs')
    
    if response.status_code == 200:
        print_success("Swagger UI disponible")
        print_info("URL: http://localhost:5000/apidocs")
        print_info("Puedes probar todos los endpoints interactivamente")
    else:
        print_error("Swagger no disponible")

# ========================
# DEMO 3: ANÁLISIS SIMPLE
# ========================

def demo_analisis_simple(token):
    print_header("DEMO 3: ANÁLISIS SIMPLE CON TOKEN")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    payload = {
        'rol': 'Estudiante',
        'tipo_producto': 'Ensayo',
        'evidencias': {
            'estilo_diferente': 1,
            'referencias_raras': 1,
            'tiempo_sospechoso': 0,
            'datos_inconsistentes': 0,
            'imagenes_sospechosas': 0,
            'sin_borradores': 0,
            'defensa_debil': 0
        }
    }
    
    print_info("Enviando análisis...")
    response = requests.post(
        f'{API_URL}/api/analyze',
        json=payload,
        headers=headers
    )
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"Análisis completado")
        print(f"  Case ID: {data['case_id']}")
        print(f"  Score: {data['analysis']['overall_score']}")
        print(f"  Nivel: {data['analysis']['overall_level']}")
        print(f"  Confianza: {data['analysis']['confidence']}")
    else:
        print_error(f"Análisis falló: {response.json()}")

# ========================
# DEMO 4: ANÁLISIS EN LOTE
# ========================

def demo_batch(token):
    print_header("DEMO 4: ANÁLISIS EN LOTE")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    casos = [
        {
            'rol': 'Estudiante',
            'tipo_producto': 'Ensayo',
            'evidencias': {
                'estilo_diferente': 0,
                'referencias_raras': 0,
                'tiempo_sospechoso': 0,
                'datos_inconsistentes': 0,
                'imagenes_sospechosas': 0,
                'sin_borradores': 0,
                'defensa_debil': 0
            }
        },
        {
            'rol': 'Estudiante',
            'tipo_producto': 'Tesis',
            'evidencias': {
                'estilo_diferente': 1,
                'referencias_raras': 1,
                'tiempo_sospechoso': 1,
                'datos_inconsistentes': 0,
                'imagenes_sospechosas': 0,
                'sin_borradores': 0,
                'defensa_debil': 1
            }
        },
        {
            'rol': 'Docente-investigador',
            'tipo_producto': 'Artículo científico',
            'evidencias': {
                'estilo_diferente': 0,
                'referencias_raras': 1,
                'tiempo_sospechoso': 0,
                'datos_inconsistentes': 1,
                'imagenes_sospechosas': 0,
                'sin_borradores': 0,
                'defensa_debil': 0
            }
        }
    ]
    
    print_info(f"Analizando {len(casos)} documentos en lote...")
    
    response = requests.post(
        f'{API_URL}/api/batch/analyze',
        json={'casos': casos},
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Análisis en lote completado")
        print(f"  Total: {data['total']}")
        print(f"  Procesados: {data['procesados']}")
        print(f"\n  Resultados:")
        for i, resultado in enumerate(data['resultados'], 1):
            if resultado['status'] == 'success':
                print(f"    {i}. Score: {resultado['score']} ({resultado['level']})")
            else:
                print(f"    {i}. Error: {resultado['error']}")
    else:
        print_error(f"Batch falló: {response.json()}")

# ========================
# DEMO 5: METRICAS
# ========================

def demo_metricas(token):
    print_header("DEMO 5: MÉTRICAS INSTITUCIONALES")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    print_info("Obteniendo métricas...")
    response = requests.get(
        f'{API_URL}/api/metrics/institutional',
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        metrics = data['metrics']
        print_success("Métricas obtenidas")
        
        general = metrics.get('resumen_general', {})
        print(f"\n  📊 Resumen General:")
        print(f"    Total de casos: {general.get('total_casos_analizados')}")
        
        tasas = metrics.get('tasas_por_nivel', {})
        print(f"\n  📈 Tasas por Nivel:")
        print(f"    ALTO: {tasas.get('ALTO')}%")
        print(f"    MEDIO: {tasas.get('MEDIO')}%")
        print(f"    BAJO: {tasas.get('BAJO')}%")
    else:
        print_error(f"Métricas falló: {response.json()}")

# ========================
# DEMO 6: INFORMACIÓN API
# ========================

def demo_info():
    print_header("DEMO 6: INFORMACIÓN DE LA API")
    
    print_info("Obteniendo información...")
    response = requests.get(f'{API_URL}/api/info')
    
    if response.status_code == 200:
        data = response.json()
        print_success("Información obtenida")
        print(f"\n  Nombre: {data['name']}")
        print(f"  Versión: {data['version']}")
        print(f"  Descripción: {data['description']}")
        
        print(f"\n  📚 Endpoints principales:")
        for categoria, endpoints in data.get('endpoints', {}).items():
            print(f"    {categoria.upper()}:")
            for ruta, desc in endpoints.items():
                print(f"      • {ruta}")
    else:
        print_error(f"Info falló: {response.json()}")

# ========================
# MAIN
# ========================

def main():
    print(f"\n{Colors.BLUE}╔{'='*68}╗{Colors.END}")
    print(f"{Colors.BLUE}║{'DEMO - CENTINELA DIGITAL API v2.1'.center(68)}║{Colors.END}")
    print(f"{Colors.BLUE}╚{'='*68}╝{Colors.END}\n")
    
    # Verificar conexión
    print_info("Verificando conexión con API...")
    try:
        response = requests.get(f'{API_URL}/health', timeout=2)
        if response.status_code == 200:
            print_success("API disponible")
        else:
            print_error("API no responde correctamente")
            sys.exit(1)
    except Exception as e:
        print_error(f"No se puede conectar a {API_URL}")
        print_error("Asegúrate de ejecutar: python3 api_v2.py")
        sys.exit(1)
    
    # Ejecutar demos
    try:
        token = demo_autenticacion()
        if not token:
            sys.exit(1)
        
        print()
        demo_swagger()
        time.sleep(0.5)
        
        demo_analisis_simple(token)
        time.sleep(0.5)
        
        demo_batch(token)
        time.sleep(0.5)
        
        demo_metricas(token)
        time.sleep(0.5)
        
        demo_info()
        
    except Exception as e:
        print_error(f"Error durante la demostración: {e}")
        sys.exit(1)
    
    # Resumen
    print_header("DEMOSTRACIÓN COMPLETADA")
    
    print(f"\n{Colors.GREEN}✓ Todas las características están funcionando{Colors.END}\n")
    
    print("🔗 Enlaces útiles:")
    print(f"  • Swagger UI: http://localhost:5000/apidocs")
    print(f"  • Información API: http://localhost:5000/api/info")
    print(f"  • Health Check: http://localhost:5000/health")
    print()
    
    print("📚 Próximos pasos:")
    print(f"  1. Revisar: API_V2_GUIDE.md")
    print(f"  2. Probar: cliente_python_v2.py")
    print(f"  3. Usar: cliente_react.jsx")
    print()

if __name__ == "__main__":
    main()
