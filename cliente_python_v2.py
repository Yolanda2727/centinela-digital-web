"""
Cliente Python mejorado para Centinela Digital API v2.1
Con autenticación, batch processing, y utilidades
"""

import requests
import json
from typing import Dict, List, Optional
import time

class CentinelaAPIClient:
    """Cliente Python para API de Centinela Digital v2.1"""
    
    def __init__(self, base_url: str = "http://localhost:5000", token: str = None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        if token:
            self._set_auth_header()
    
    def _set_auth_header(self):
        """Configurar header de autenticación"""
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        })
    
    # ========================
    # AUTENTICACIÓN
    # ========================
    
    def login(self, username: str, password: str) -> Dict:
        """
        Autenticarse y obtener token JWT
        
        Args:
            username: Nombre de usuario
            password: Contraseña
        
        Returns:
            Dict con token
        """
        response = self.session.post(
            f'{self.base_url}/api/auth/login',
            json={'username': username, 'password': password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            self._set_auth_header()
            print(f"✓ Login exitoso: {username}")
            return data
        else:
            raise Exception(f"Login falló: {response.json()}")
    
    def register(self, username: str, password: str, email: str) -> Dict:
        """Registrar nuevo usuario"""
        response = self.session.post(
            f'{self.base_url}/api/auth/register',
            json={'username': username, 'password': password, 'email': email}
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Registro falló: {response.json()}")
    
    # ========================
    # ANÁLISIS
    # ========================
    
    def analyze(self,
                rol: str = "Estudiante",
                tipo_producto: str = "Ensayo",
                evidencias: Dict = None) -> Dict:
        """
        Analizar un documento
        
        Args:
            rol: Rol del usuario
            tipo_producto: Tipo de producto académico
            evidencias: Dict con señales de alerta
        
        Returns:
            Dict con resultado del análisis
        """
        if not self.token:
            raise Exception("No autenticado. Ejecutar login() primero")
        
        if evidencias is None:
            evidencias = {
                'estilo_diferente': 0,
                'tiempo_sospechoso': 0,
                'referencias_raras': 0,
                'datos_inconsistentes': 0,
                'imagenes_sospechosas': 0,
                'sin_borradores': 0,
                'defensa_debil': 0,
            }
        
        response = self.session.post(
            f'{self.base_url}/api/analyze',
            json={
                'rol': rol,
                'tipo_producto': tipo_producto,
                'evidencias': evidencias
            }
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Análisis falló: {response.json()}")
    
    def batch_analyze(self, casos: List[Dict]) -> Dict:
        """
        Analizar múltiples documentos en lote
        
        Args:
            casos: Lista de casos a analizar
        
        Returns:
            Dict con resultados
        """
        if not self.token:
            raise Exception("No autenticado. Ejecutar login() primero")
        
        response = self.session.post(
            f'{self.base_url}/api/batch/analyze',
            json={'casos': casos}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Análisis en lote falló: {response.json()}")
    
    # ========================
    # CONSULTAS
    # ========================
    
    def get_case(self, case_id: str) -> Dict:
        """Obtener detalles de un caso específico"""
        if not self.token:
            raise Exception("No autenticado. Ejecutar login() primero")
        
        response = self.session.get(f'{self.base_url}/api/case/{case_id}')
        
        if response.status_code == 200:
            return response.json()['case']
        else:
            raise Exception(f"Caso no encontrado: {case_id}")
    
    def list_cases(self, limit: int = 50, offset: int = 0) -> Dict:
        """Listar casos"""
        if not self.token:
            raise Exception("No autenticado. Ejecutar login() primero")
        
        response = self.session.get(
            f'{self.base_url}/api/cases',
            params={'limit': limit, 'offset': offset}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error listando casos: {response.json()}")
    
    # ========================
    # MÉTRICAS
    # ========================
    
    def get_metrics(self) -> Dict:
        """Obtener métricas institucionales"""
        if not self.token:
            raise Exception("No autenticado. Ejecutar login() primero")
        
        response = self.session.get(f'{self.base_url}/api/metrics/institutional')
        
        if response.status_code == 200:
            return response.json()['metrics']
        else:
            raise Exception(f"Error obteniendo métricas: {response.json()}")
    
    def get_temporal(self, period: str = 'daily') -> Dict:
        """
        Obtener análisis temporal
        
        Args:
            period: 'daily', 'weekly', 'monthly'
        """
        if not self.token:
            raise Exception("No autenticado. Ejecutar login() primero")
        
        response = self.session.get(
            f'{self.base_url}/api/metrics/temporal',
            params={'period': period}
        )
        
        if response.status_code == 200:
            return response.json()['data']
        else:
            raise Exception(f"Error obteniendo análisis temporal: {response.json()}")
    
    # ========================
    # INFORMACIÓN
    # ========================
    
    def get_info(self) -> Dict:
        """Obtener información de la API"""
        response = self.session.get(f'{self.base_url}/api/info')
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error obteniendo info: {response.json()}")
    
    def health_check(self) -> bool:
        """Verificar que API está disponible"""
        try:
            response = self.session.get(f'{self.base_url}/health')
            return response.status_code == 200
        except:
            return False


# ========================
# EJEMPLOS DE USO
# ========================

def ejemplo_1_login():
    """Ejemplo 1: Autenticación"""
    print("\n" + "="*70)
    print("EJEMPLO 1: Autenticación")
    print("="*70)
    
    client = CentinelaAPIClient()
    
    # Autenticarse
    auth = client.login('admin', 'admin123')
    print(f"✓ Token: {auth['token'][:20]}...")


def ejemplo_2_analisis():
    """Ejemplo 2: Análisis simple"""
    print("\n" + "="*70)
    print("EJEMPLO 2: Análisis Simple")
    print("="*70)
    
    client = CentinelaAPIClient()
    client.login('admin', 'admin123')
    
    # Analizar
    resultado = client.analyze(
        rol="Estudiante",
        tipo_producto="Ensayo",
        evidencias={
            'estilo_diferente': 1,
            'referencias_raras': 1,
        }
    )
    
    print(f"✓ Case ID: {resultado['case_id']}")
    print(f"✓ Score: {resultado['analysis']['overall_score']}")
    print(f"✓ Nivel: {resultado['analysis']['overall_level']}")


def ejemplo_3_batch():
    """Ejemplo 3: Análisis en lote"""
    print("\n" + "="*70)
    print("EJEMPLO 3: Análisis en Lote")
    print("="*70)
    
    client = CentinelaAPIClient()
    client.login('admin', 'admin123')
    
    casos = [
        {
            'rol': 'Estudiante',
            'tipo_producto': 'Ensayo',
            'evidencias': {'estilo_diferente': 0, 'referencias_raras': 0}
        },
        {
            'rol': 'Estudiante',
            'tipo_producto': 'Tesis',
            'evidencias': {'estilo_diferente': 1, 'referencias_raras': 1}
        },
    ]
    
    resultado = client.batch_analyze(casos)
    print(f"✓ Total: {resultado['total']}")
    print(f"✓ Procesados: {resultado['procesados']}")


def ejemplo_4_metricas():
    """Ejemplo 4: Obtener métricas"""
    print("\n" + "="*70)
    print("EJEMPLO 4: Métricas Institucionales")
    print("="*70)
    
    client = CentinelaAPIClient()
    client.login('admin', 'admin123')
    
    metricas = client.get_metrics()
    print(f"✓ Total de casos: {metricas['resumen_general']['total_casos_analizados']}")


def main():
    """Función principal"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*20 + "CLIENTE PYTHON - CENTINELA DIGITAL 2.1" + " "*10 + "║")
    print("╚" + "="*68 + "╝")
    
    print("\nEjemplos disponibles:")
    print("  1. Autenticación")
    print("  2. Análisis simple")
    print("  3. Análisis en lote")
    print("  4. Obtener métricas")
    print("  5. Ejecutar todos")
    
    opcion = input("\nSelecciona ejemplo (1-5): ").strip()
    
    try:
        if opcion == "1":
            ejemplo_1_login()
        elif opcion == "2":
            ejemplo_2_analisis()
        elif opcion == "3":
            ejemplo_3_batch()
        elif opcion == "4":
            ejemplo_4_metricas()
        elif opcion == "5":
            ejemplo_1_login()
            ejemplo_2_analisis()
            ejemplo_3_batch()
            ejemplo_4_metricas()
        else:
            print("Opción no válida")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
