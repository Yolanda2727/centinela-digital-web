"""
Cliente REST para probar la API de Centinela Digital
Demuestra cómo consumir los endpoints
"""

import requests
import json
from typing import Dict, Optional

# ============================================================
# CONFIGURACIÓN
# ============================================================

API_BASE_URL = "http://localhost:5000"

class CentinelaAPIClient:
    """Cliente para interactuar con la API de Centinela Digital"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    # ========== ANÁLISIS ==========
    
    def analyze(
        self,
        texto: str,
        rol: str = "Estudiante",
        tipo_producto: str = "Ensayo",
        titulo: Optional[str] = None,
        autor: Optional[str] = None,
        evidencias: Optional[Dict] = None
    ) -> Dict:
        """
        Analizar un documento
        
        Args:
            texto: Contenido del documento
            rol: Estudiante, Docente-investigador, Coinvestigador externo
            tipo_producto: Tipo de documento
            titulo: Título opcional
            autor: Autor opcional
            evidencias: Dict con evidencias detectadas
        """
        if evidencias is None:
            evidencias = {}
        
        payload = {
            'texto': texto,
            'metadata': {
                'rol': rol,
                'tipo_producto': tipo_producto,
                'titulo': titulo,
                'autor': autor
            },
            'evidencias': evidencias
        }
        
        response = self.session.post(
            f"{self.base_url}/api/analyze",
            json=payload
        )
        return response.json()
    
    # ========== CONSULTAS ==========
    
    def get_case(self, case_id: str) -> Dict:
        """Obtener un caso específico"""
        response = self.session.get(f"{self.base_url}/api/case/{case_id}")
        return response.json()
    
    def list_cases(
        self,
        nivel: Optional[str] = None,
        rol: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict:
        """Listar casos con filtros"""
        params = {
            'limit': limit,
            'offset': offset
        }
        if nivel:
            params['nivel'] = nivel
        if rol:
            params['rol'] = rol
        
        response = self.session.get(
            f"{self.base_url}/api/cases",
            params=params
        )
        return response.json()
    
    # ========== MÉTRICAS ==========
    
    def get_metrics_institutional(self) -> Dict:
        """Obtener métricas institucionales"""
        response = self.session.get(f"{self.base_url}/api/metrics/institutional")
        return response.json()
    
    def get_metrics_temporal(self, period: str = "daily") -> Dict:
        """Obtener análisis temporal"""
        response = self.session.get(
            f"{self.base_url}/api/metrics/temporal",
            params={'period': period}
        )
        return response.json()
    
    # ========== INFORMACIÓN ==========
    
    def get_info(self) -> Dict:
        """Obtener información de la API"""
        response = self.session.get(f"{self.base_url}/api/info")
        return response.json()
    
    def health_check(self) -> Dict:
        """Verificar salud de la API"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()


# ============================================================
# EJEMPLOS DE USO
# ============================================================

def ejemplo_1_basic_analysis():
    """Ejemplo 1: Análisis básico"""
    print("\n" + "="*70)
    print("EJEMPLO 1: Análisis básico de un documento")
    print("="*70)
    
    client = CentinelaAPIClient()
    
    texto = """
    Este ensayo discute la importancia del análisis crítico en la educación moderna.
    La educación ha evolucionado significativamente en las últimas décadas, pasando
    de un modelo centrado en la transmisión de información a uno que enfatiza el
    pensamiento crítico y la resolución de problemas. La relevancia de este cambio
    no puede ser subestimada, ya que prepara a los estudiantes para un mundo en
    constante cambio y complejidad creciente.
    """
    
    result = client.analyze(
        texto=texto,
        rol="Estudiante",
        tipo_producto="Ensayo",
        titulo="La importancia del análisis crítico",
        autor="Juan García",
        evidencias={
            'estilo_diferente': 0,
            'defensa_debil': 0,
            'tiempo_sospechoso': 0
        }
    )
    
    print(f"Status: {result.get('status')}")
    print(f"Case ID: {result.get('case_id')}")
    print(f"\nAnálisis:")
    if 'analysis' in result:
        print(f"  Puntuación: {result['analysis']['overall_score']}")
        print(f"  Nivel: {result['analysis']['overall_level']}")
        print(f"  Confianza: {result['analysis']['confidence']:.2f}")


def ejemplo_2_analysis_with_flags():
    """Ejemplo 2: Análisis con alertas"""
    print("\n" + "="*70)
    print("EJEMPLO 2: Análisis con múltiples alertas")
    print("="*70)
    
    client = CentinelaAPIClient()
    
    texto = """
    Este es un documento sospechoso. El contenido parece estar desconectado
    y no sigue una estructura lógica clara. Hay demasiadas referencias extrañas
    y datos que no coinciden con lo que se espera. Las imágenes incluidas
    parecen de baja calidad y posiblemente copiadas.
    """ * 10  # Repetir para alcanzar longitud mínima
    
    result = client.analyze(
        texto=texto,
        rol="Estudiante",
        tipo_producto="Tesis",
        titulo="Tesis Sospechosa",
        autor="Anónimo",
        evidencias={
            'estilo_diferente': 1,
            'defensa_debil': 1,
            'tiempo_sospechoso': 1,
            'referencias_raras': 1,
            'datos_inconsistentes': 1
        }
    )
    
    print(f"Status: {result.get('status')}")
    print(f"Case ID: {result.get('case_id')}")
    print(f"\nAnálisis:")
    if 'analysis' in result:
        print(f"  Puntuación: {result['analysis']['overall_score']}")
        print(f"  Nivel: {result['analysis']['overall_level']}")
        print(f"  Confianza: {result['analysis']['confidence']:.2f}")
        if result['analysis']['recommendations']:
            print(f"  Recomendaciones:")
            for rec in result['analysis']['recommendations']:
                print(f"    - {rec}")


def ejemplo_3_list_and_metrics():
    """Ejemplo 3: Listar casos y ver métricas"""
    print("\n" + "="*70)
    print("EJEMPLO 3: Listar casos y ver métricas")
    print("="*70)
    
    client = CentinelaAPIClient()
    
    # Listar casos
    print("\n📋 Casos almacenados:")
    cases = client.list_cases(limit=5)
    if cases.get('status') == 'success':
        print(f"Total: {cases['total']} casos")
        for case in cases.get('cases', []):
            print(f"  - {case['case_id']}: {case['title']} ({case['overall_level']})")
    
    # Métricas
    print("\n📊 Métricas institucionales:")
    metrics = client.get_metrics_institutional()
    if metrics.get('status') == 'success':
        m = metrics.get('metrics', {})
        resumen = m.get('resumen_general', {})
        print(f"  Total de casos: {resumen.get('total_casos_analizados', 0)}")
        print(f"  Puntuación promedio: {resumen.get('tasa_riesgo_general', 0):.2f}")
        tasas = m.get('tasas_por_nivel', {})
        print(f"  Distribución de riesgo: {tasas}")


def ejemplo_4_filter_cases():
    """Ejemplo 4: Filtrar casos por nivel"""
    print("\n" + "="*70)
    print("EJEMPLO 4: Filtrar casos por nivel de riesgo")
    print("="*70)
    
    client = CentinelaAPIClient()
    
    for nivel in ['BAJO', 'MEDIO', 'ALTO']:
        print(f"\n🔍 Casos con nivel {nivel}:")
        result = client.list_cases(nivel=nivel, limit=3)
        if result.get('status') == 'success':
            total = result.get('total', 0)
            print(f"  Total encontrados: {total}")
            for case in result.get('cases', []):
                print(f"  - {case['case_id']}: {case['title']}")


def ejemplo_5_api_info():
    """Ejemplo 5: Información y salud de API"""
    print("\n" + "="*70)
    print("EJEMPLO 5: Información y estado de la API")
    print("="*70)
    
    client = CentinelaAPIClient()
    
    # Health check
    print("\n🏥 Health Check:")
    health = client.health_check()
    print(f"  Status: {health.get('status')}")
    print(f"  Version: {health.get('version')}")
    
    # Info
    print("\n ℹ️  Información de API:")
    info = client.get_info()
    print(f"  Nombre: {info.get('name')}")
    print(f"  Versión: {info.get('version')}")
    print(f"  Roles válidos: {', '.join(info.get('valid_roles', []))}")
    print(f"  Tipos de producto: {', '.join(info.get('valid_product_types', []))}")


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    import sys
    
    try:
        if len(sys.argv) > 1:
            ejemplo = sys.argv[1]
            if ejemplo == '1':
                ejemplo_1_basic_analysis()
            elif ejemplo == '2':
                ejemplo_2_analysis_with_flags()
            elif ejemplo == '3':
                ejemplo_3_list_and_metrics()
            elif ejemplo == '4':
                ejemplo_4_filter_cases()
            elif ejemplo == '5':
                ejemplo_5_api_info()
            else:
                print("Ejemplo no válido. Opciones: 1, 2, 3, 4, 5")
        else:
            print("🚀 API REST - Cliente de Prueba")
            print("\nUso: python api_client.py [número de ejemplo]")
            print("\nEjemplos disponibles:")
            print("  1 - Análisis básico")
            print("  2 - Análisis con alertas")
            print("  3 - Listar casos y métricas")
            print("  4 - Filtrar casos por nivel")
            print("  5 - Información y estado de API")
            print("\nPrimero, inicia el servidor:")
            print("  python api.py")
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar a la API")
        print("Asegúrate de que el servidor está corriendo:")
        print("  python api.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
