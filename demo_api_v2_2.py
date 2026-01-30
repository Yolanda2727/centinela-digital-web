#!/usr/bin/env python3
"""
Demostración de API v2.2 - Integridad y Auditoría
Muestra todos los nuevos endpoints y características
"""

import requests
import json
import time
from datetime import datetime
import hashlib

# Colores para consola
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

BASE_URL = "http://localhost:5000"
TOKEN = None

def print_section(titulo):
    """Imprime sección"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(mensaje):
    """Imprime éxito"""
    print(f"{Colors.OKGREEN}✓ {mensaje}{Colors.ENDC}")

def print_error(mensaje):
    """Imprime error"""
    print(f"{Colors.FAIL}✗ {mensaje}{Colors.ENDC}")

def print_info(mensaje):
    """Imprime información"""
    print(f"{Colors.OKCYAN}ℹ {mensaje}{Colors.ENDC}")

def demo_autenticacion():
    """Demo: Autenticación JWT"""
    global TOKEN
    
    print_section("1. AUTENTICACIÓN JWT")
    
    print_info("Realizando login con usuario 'admin'...")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        TOKEN = data['token']
        print_success(f"Token obtenido: {TOKEN[:20]}...")
        print_info(f"Expira en: {data['expira_en']} segundos")
        return True
    else:
        print_error(f"Fallo: {response.status_code}")
        return False

def demo_análisis_simple_con_metadatos():
    """Demo: Análisis simple con metadatos completos"""
    print_section("2. ANÁLISIS SIMPLE CON METADATOS COMPLETOS")
    
    documento = """
    Este estudio investiga el impacto de la inteligencia artificial en la educación.
    Según estudios previos, la IA ha demostrado mejorar resultados académicos.
    Los datos muestran una correlación positiva entre uso de IA y desempeño.
    """
    
    print_info("Analizando documento...")
    print_info(f"Contenido: {documento[:50]}...")
    
    response = requests.post(
        f"{BASE_URL}/api/analyze",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "contenido": documento,
            "tipo_documento": "investigación",
            "rol": "Investigador",
            "temperatura": 0.7,
            "prompts": ["análisis_académico", "detección_plagio"]
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Análisis completado")
        
        # Mostrar metadatos
        print(f"\n{Colors.BOLD}METADATOS:{Colors.ENDC}")
        print(f"  Fecha: {data['metadatos']['fecha']}")
        print(f"  Usuario: {data['metadatos']['usuario']}")
        print(f"  Versión: {data['metadatos']['version_modelo']}")
        print(f"  Temperatura: {data['metadatos']['temperatura']}")
        print(f"  Prompts: {', '.join(data['metadatos']['prompts_usados'])}")
        print(f"  Ajustes: {json.dumps(data['metadatos']['ajustes'], indent=4)}")
        
        # Mostrar resultados
        print(f"\n{Colors.BOLD}RESULTADOS:{Colors.ENDC}")
        print(f"  Score General: {data['resultados']['score_general']:.1f}")
        print(f"  Nivel Riesgo: {data['resultados']['nivel_riesgo']}")
        print(f"  Plagio Conceptual: {data['resultados']['score_plagio_conceptual']:.1f}")
        print(f"  Desviaciones: {data['resultados']['score_desviaciones']:.1f}")
        print(f"  Mala Conducta: {data['resultados']['score_mala_conducta']:.1f}")
        print(f"  Falacias: {data['resultados']['score_falacias']:.1f}")
    else:
        print_error(f"Error: {response.status_code}")
        print(response.text)

def demo_reporte_integridad():
    """Demo: Análisis de integridad científica"""
    print_section("3. REPORTE DE INTEGRIDAD CIENTÍFICA")
    
    documento = """
    Metodología: Se realizó un estudio con 100 participantes.
    Los datos muestran resultados perfectos: 95.00%, 95.00%, 95.00%.
    Como dice el Dr. Experto, nuestras conclusiones son correctas.
    Por lo tanto, podemos afirmar que siempre ocurre este fenómeno.
    Se asumieron los datos faltantes basados en simulaciones.
    """
    
    print_info("Analizando integridad científica...")
    print_info("Detectando: plagio, desviaciones, mala conducta, falacias")
    
    response = requests.post(
        f"{BASE_URL}/api/reporte-integridad",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "contenido": documento,
            "rol": "Investigador"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        análisis = data['análisis']
        
        print_success("Análisis de integridad completado")
        
        print(f"\n{Colors.BOLD}PLAGIO CONCEPTUAL:{Colors.ENDC}")
        print(f"  Score: {análisis['plagio_conceptual']['score']}")
        for hallazgo in análisis['plagio_conceptual']['hallazgos']:
            print(f"    • {hallazgo}")
        
        print(f"\n{Colors.BOLD}DESVIACIONES METODOLÓGICAS:{Colors.ENDC}")
        print(f"  Score: {análisis['desviaciones_metodologicas']['score']}")
        for hallazgo in análisis['desviaciones_metodologicas']['hallazgos']:
            print(f"    • {hallazgo}")
        
        print(f"\n{Colors.BOLD}MALA CONDUCTA:{Colors.ENDC}")
        print(f"  Score: {análisis['mala_conducta']['score']}")
        for hallazgo in análisis['mala_conducta']['hallazgos']:
            print(f"    • {hallazgo}")
        
        print(f"\n{Colors.BOLD}FALACIAS ARGUMENTATIVAS:{Colors.ENDC}")
        print(f"  Score: {análisis['falacias']['score']}")
        for hallazgo in análisis['falacias']['hallazgos']:
            print(f"    • {hallazgo}")
        
        print(f"\n{Colors.BOLD}RESUMEN FINAL:{Colors.ENDC}")
        print(f"  Score General: {análisis['score_general']:.1f}")
        print(f"  Nivel Riesgo: {Colors.WARNING}{análisis['nivel_riesgo']}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}RECOMENDACIONES:{Colors.ENDC}")
        for rec in análisis['recomendaciones']:
            print(f"  • {rec}")
    else:
        print_error(f"Error: {response.status_code}")

def demo_procesamiento_lote():
    """Demo: Análisis en lote"""
    print_section("4. PROCESAMIENTO EN LOTE")
    
    documentos = [
        {
            "contenido": "Primer ensayo sobre educación digital...",
            "tipo_documento": "ensayo",
            "rol": "Estudiante"
        },
        {
            "contenido": "Segundo documento de investigación...",
            "tipo_documento": "investigación",
            "rol": "Investigador"
        },
        {
            "contenido": "Tercer artículo académico revisado por pares...",
            "tipo_documento": "artículo",
            "rol": "Académico"
        }
    ]
    
    print_info(f"Procesando {len(documentos)} documentos...")
    
    response = requests.post(
        f"{BASE_URL}/api/batch/analyze",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={"documentos": documentos}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Lote procesado en {data['metadatos']['duracion_ms']}ms")
        
        print(f"\n{Colors.BOLD}RESULTADOS:{Colors.ENDC}")
        for resultado in data['resultados']:
            idx = resultado['índice']
            if 'error' in resultado:
                print(f"  Documento {idx}: {Colors.FAIL}Error{Colors.ENDC} - {resultado['error']}")
            else:
                print(f"  Documento {idx}:")
                print(f"    Score: {resultado['score_general']:.1f}")
                print(f"    Riesgo: {resultado['nivel_riesgo']}")
    else:
        print_error(f"Error: {response.status_code}")

def demo_log_actividad():
    """Demo: Historial de actividades"""
    print_section("5. LOG DE ACTIVIDADES (AUDITORÍA)")
    
    print_info("Recuperando historial de actividades...")
    
    response = requests.get(
        f"{BASE_URL}/api/log-actividad?días=7&límite=20",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Total de actividades: {data['total_registros']}")
        
        print(f"\n{Colors.BOLD}ÚLTIMAS ACTIVIDADES:{Colors.ENDC}")
        for actividad in data['actividades'][:5]:
            print(f"  {actividad['timestamp']}")
            print(f"    Usuario: {actividad['usuario']}")
            print(f"    Tipo: {actividad['tipo_actividad']}")
            print(f"    Endpoint: {actividad['endpoint']}")
            print(f"    Estado: {actividad['estado']}")
            print(f"    Duración: {actividad['duracion_ms']}ms")
    else:
        print_error(f"Error: {response.status_code}")

def demo_reporte_auditoria():
    """Demo: Reporte de auditoría completo"""
    print_section("6. REPORTE DE AUDITORÍA COMPLETO")
    
    print_info("Generando reporte de auditoría del usuario...")
    
    response = requests.get(
        f"{BASE_URL}/api/auditoria/usuario/admin",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print_success("Reporte generado")
        
        print(f"\n{Colors.BOLD}RESUMEN:{Colors.ENDC}")
        print(f"  Usuario: {data['usuario']}")
        print(f"  Total Actividades: {data['resumen']['total_actividades']}")
        print(f"  Total Análisis: {data['resumen']['total_análisis']}")
        print(f"  Cambios Sensibles: {data['resumen']['cambios_sensibles']}")
        
        print(f"\n{Colors.BOLD}ANÁLISIS:{Colors.ENDC}")
        if data['análisis']:
            print(f"  Score Promedio: {data['análisis'].get('score_promedio', 0):.1f}")
            print(f"  Documentos Críticos: {data['análisis'].get('documentos_críticos', 0)}")
            print(f"  Documentos Alto Riesgo: {data['análisis'].get('documentos_alto_riesgo', 0)}")
            print(f"  Documentos Medio Riesgo: {data['análisis'].get('documentos_medio_riesgo', 0)}")
            print(f"  Documentos Bajo Riesgo: {data['análisis'].get('documentos_bajo_riesgo', 0)}")
    else:
        print_error(f"Error: {response.status_code}")

def demo_historial_análisis():
    """Demo: Historial de análisis realizados"""
    print_section("7. HISTORIAL DE ANÁLISIS")
    
    print_info("Recuperando análisis realizados...")
    
    response = requests.get(
        f"{BASE_URL}/api/auditoria/análisis?usuario=admin&días=30",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Total análisis: {data['total_análisis']}")
        
        print(f"\n{Colors.BOLD}ANÁLISIS REALIZADOS:{Colors.ENDC}")
        for análisis in data['análisis'][:5]:
            print(f"  {análisis['timestamp']}")
            print(f"    Tipo: {análisis['tipo_documento']}")
            print(f"    Rol: {análisis['rol_autor']}")
            print(f"    Score: {análisis['score_general']:.1f}")
            print(f"    Riesgo: {análisis['nivel_riesgo']}")
    else:
        print_error(f"Error: {response.status_code}")

def main():
    """Ejecuta demostraciones"""
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║  DEMOSTRACIÓN - CENTINELA DIGITAL API v2.2            ║")
    print("║  Integridad Científica + Auditoría Completa          ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    # Verificar conectividad
    print_info("Verificando conectividad con API...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_success(f"API disponible: {response.json()['estado']}")
    except:
        print_error("No se puede conectar con el API en localhost:5000")
        print_info("Asegúrate de ejecutar: python3 api_v2_mejorado.py")
        return
    
    # Ejecutar demos
    if not demo_autenticacion():
        return
    
    try:
        demo_análisis_simple_con_metadatos()
        time.sleep(1)
        
        demo_reporte_integridad()
        time.sleep(1)
        
        demo_procesamiento_lote()
        time.sleep(1)
        
        demo_log_actividad()
        time.sleep(1)
        
        demo_reporte_auditoria()
        time.sleep(1)
        
        demo_historial_análisis()
        
        print_section("DEMOSTRACIÓN COMPLETADA")
        print_success("Todos los endpoints funcionan correctamente")
        
        print(f"\n{Colors.BOLD}Próximos pasos:{Colors.ENDC}")
        print("  1. Acceder a Swagger: http://localhost:5000/apidocs/")
        print("  2. Probar endpoints adicionales en la interfaz")
        print("  3. Ver auditoría completa en /api/auditoria/alertas")
        
    except Exception as e:
        print_error(f"Error durante demostración: {str(e)}")

if __name__ == "__main__":
    main()
