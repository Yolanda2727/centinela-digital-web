#!/usr/bin/env python3
"""
Cliente Python Centinela Digital v2.2
Soporte completo para análisis de integridad y auditoría
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime


class CentinelaAPIClientV2_2:
    """Cliente completo para API v2.2 con auditoría"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Inicializa cliente
        
        Args:
            base_url: URL base del API
        """
        self.base_url = base_url
        self.token = None
        self.usuario = None
        self.session = requests.Session()
    
    def login(self, username: str, password: str) -> Dict:
        """
        Autenticarse
        
        Args:
            username: Usuario
            password: Contraseña
        
        Returns:
            Información de autenticación
        """
        response = self.session.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            self.usuario = data['usuario']
            self._actualizar_headers()
            print(f"✓ Autenticado como {self.usuario}")
            return data
        else:
            raise Exception(f"Login fallido: {response.json()['error']}")
    
    def register(self, username: str, password: str) -> Dict:
        """Registrar nuevo usuario"""
        response = self.session.post(
            f"{self.base_url}/api/auth/register",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(response.json()['error'])
    
    def _actualizar_headers(self):
        """Actualiza headers con token"""
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        })
    
    # ============================================================
    # ANÁLISIS SIMPLES
    # ============================================================
    
    def analyze(
        self,
        contenido: str,
        tipo_documento: str = "general",
        rol: str = "Estudiante",
        temperatura: float = 0.7,
        prompts: Optional[List[str]] = None
    ) -> Dict:
        """
        Analizar documento con metadatos completos
        
        Args:
            contenido: Contenido a analizar
            tipo_documento: Tipo (ensayo, investigación, etc.)
            rol: Rol del autor
            temperatura: Parámetro de generación
            prompts: Prompts utilizados
        
        Returns:
            Análisis completo con metadatos
        """
        if prompts is None:
            prompts = []
        
        response = self.session.post(
            f"{self.base_url}/api/analyze",
            json={
                "contenido": contenido,
                "tipo_documento": tipo_documento,
                "rol": rol,
                "temperatura": temperatura,
                "prompts": prompts
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error en análisis: {response.json()['error']}")
    
    # ============================================================
    # ANÁLISIS DE INTEGRIDAD CIENTÍFICA
    # ============================================================
    
    def reporte_integridad(
        self,
        contenido: str,
        rol: str = "Investigador"
    ) -> Dict:
        """
        Análisis completo de integridad científica
        
        Detecta:
        - Plagio conceptual
        - Desviaciones metodológicas
        - Mala conducta científica
        - Fabricación de datos
        - Falacias argumentativas
        
        Args:
            contenido: Documento a analizar
            rol: Rol del autor
        
        Returns:
            Análisis detallado de integridad
        """
        response = self.session.post(
            f"{self.base_url}/api/reporte-integridad",
            json={
                "contenido": contenido,
                "rol": rol
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.json()['error']}")
    
    # ============================================================
    # PROCESAMIENTO EN LOTE
    # ============================================================
    
    def batch_analyze(self, documentos: List[Dict]) -> Dict:
        """
        Analizar múltiples documentos
        
        Args:
            documentos: Lista de documentos con campos:
                - contenido: Contenido
                - tipo_documento: Tipo
                - rol: Rol del autor
        
        Returns:
            Análisis de todos los documentos
        """
        response = self.session.post(
            f"{self.base_url}/api/batch/analyze",
            json={"documentos": documentos}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.json()['error']}")
    
    # ============================================================
    # AUDITORÍA Y LOG
    # ============================================================
    
    def obtener_log_actividad(
        self,
        usuario: Optional[str] = None,
        tipo: Optional[str] = None,
        días: int = 30,
        límite: int = 100
    ) -> Dict:
        """
        Obtener historial de actividades
        
        Args:
            usuario: Filtrar por usuario
            tipo: Filtrar por tipo de actividad
            días: Últimos N días
            límite: Máximo de registros
        
        Returns:
            Historial completo
        """
        params = {
            "días": días,
            "límite": límite
        }
        if usuario:
            params["usuario"] = usuario
        if tipo:
            params["tipo"] = tipo
        
        response = self.session.get(
            f"{self.base_url}/api/log-actividad",
            params=params
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.json()['error']}")
    
    def obtener_reporte_auditoria(self, usuario: Optional[str] = None) -> Dict:
        """
        Obtener reporte completo de auditoría
        
        Args:
            usuario: Usuario a auditar (default: usuario actual)
        
        Returns:
            Reporte detallado
        """
        if usuario is None:
            usuario = self.usuario
        
        response = self.session.get(
            f"{self.base_url}/api/auditoria/usuario/{usuario}"
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.json()['error']}")
    
    def obtener_análisis_realizados(
        self,
        usuario: Optional[str] = None,
        días: int = 30,
        límite: int = 50
    ) -> Dict:
        """
        Obtener historial de análisis realizados
        
        Args:
            usuario: Usuario a consultar
            días: Últimos N días
            límite: Máximo de registros
        
        Returns:
            Historial de análisis
        """
        if usuario is None:
            usuario = self.usuario
        
        params = {
            "usuario": usuario,
            "días": días
        }
        
        response = self.session.get(
            f"{self.base_url}/api/auditoria/análisis",
            params=params
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.json()['error']}")
    
    def obtener_cambios_sensibles(self) -> Dict:
        """
        Obtener cambios sensibles del sistema (solo admin)
        
        Returns:
            Historial de cambios
        """
        response = self.session.get(
            f"{self.base_url}/api/auditoria/cambios-sensibles"
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            print("✗ Solo administrador puede acceder a cambios sensibles")
            return {"cambios": []}
        else:
            raise Exception(f"Error: {response.json()['error']}")
    
    def obtener_alertas(self) -> Dict:
        """
        Obtener alertas del sistema (solo admin)
        
        Returns:
            Alertas activas
        """
        response = self.session.get(
            f"{self.base_url}/api/auditoria/alertas"
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            print("✗ Solo administrador puede acceder a alertas")
            return {"alertas": []}
        else:
            raise Exception(f"Error: {response.json()['error']}")
    
    # ============================================================
    # INFORMACIÓN
    # ============================================================
    
    def obtener_info(self) -> Dict:
        """Obtener información del API"""
        response = self.session.get(f"{self.base_url}/api/info")
        return response.json()


# ============================================================
# EJEMPLOS DE USO
# ============================================================

def ejemplo_análisis_completo():
    """Ejemplo: Análisis completo con metadatos"""
    
    cliente = CentinelaAPIClientV2_2()
    cliente.login("admin", "admin123")
    
    print("\n" + "="*60)
    print("EJEMPLO 1: Análisis con Metadatos")
    print("="*60 + "\n")
    
    documento = """
    Este trabajo estudia el impacto de la IA en educación.
    Según Wang et al. (2023), la IA mejora resultados académicos.
    Nuestro análisis incluye 500 participantes de diferentes instituciones.
    Los datos muestran un aumento del 25% en desempeño académico.
    """
    
    análisis = cliente.analyze(
        contenido=documento,
        tipo_documento="investigación",
        rol="Investigador",
        temperatura=0.7,
        prompts=["análisis_académico", "verificación_fuentes"]
    )
    
    print(f"Fecha: {análisis['metadatos']['fecha']}")
    print(f"Usuario: {análisis['metadatos']['usuario']}")
    print(f"Versión Modelo: {análisis['metadatos']['version_modelo']}")
    print(f"Temperatura: {análisis['metadatos']['temperatura']}")
    print(f"Prompts: {', '.join(análisis['metadatos']['prompts_usados'])}")
    print(f"\nScore General: {análisis['resultados']['score_general']:.1f}")
    print(f"Nivel Riesgo: {análisis['resultados']['nivel_riesgo']}")


def ejemplo_integridad_científica():
    """Ejemplo: Análisis de integridad científica"""
    
    cliente = CentinelaAPIClientV2_2()
    cliente.login("admin", "admin123")
    
    print("\n" + "="*60)
    print("EJEMPLO 2: Reporte de Integridad Científica")
    print("="*60 + "\n")
    
    documento = """
    Metodología: Se utilizó un diseño experimental con control.
    Los datos muestran valores perfectos: 95.00%, 95.00%, 95.00%.
    Como dice el Dr. Smith, nuestras conclusiones son definitivas.
    Por lo tanto, esta teoría siempre es verdadera.
    Asumimos los datos faltantes basados en simulaciones sin documentar.
    """
    
    integridad = cliente.reporte_integridad(
        contenido=documento,
        rol="Investigador"
    )
    
    print(f"Score Plagio Conceptual: {integridad['análisis']['plagio_conceptual']['score']}")
    print(f"Score Desviaciones: {integridad['análisis']['desviaciones_metodologicas']['score']}")
    print(f"Score Mala Conducta: {integridad['análisis']['mala_conducta']['score']}")
    print(f"Score Falacias: {integridad['análisis']['falacias']['score']}")
    print(f"\nScore General: {integridad['análisis']['score_general']:.1f}")
    print(f"Nivel Riesgo: {integridad['análisis']['nivel_riesgo']}")
    
    print("\nRecomendaciones:")
    for rec in integridad['análisis']['recomendaciones']:
        print(f"  • {rec}")


def ejemplo_procesamiento_lote():
    """Ejemplo: Procesamiento en lote"""
    
    cliente = CentinelaAPIClientV2_2()
    cliente.login("admin", "admin123")
    
    print("\n" + "="*60)
    print("EJEMPLO 3: Procesamiento en Lote")
    print("="*60 + "\n")
    
    documentos = [
        {
            "contenido": "Primer documento sobre educación...",
            "tipo_documento": "ensayo",
            "rol": "Estudiante"
        },
        {
            "contenido": "Segundo documento de investigación...",
            "tipo_documento": "investigación",
            "rol": "Investigador"
        },
        {
            "contenido": "Tercer artículo académico...",
            "tipo_documento": "artículo",
            "rol": "Académico"
        }
    ]
    
    batch = cliente.batch_analyze(documentos)
    
    print(f"Documentos procesados: {batch['metadatos']['documentos_procesados']}")
    print(f"Duración total: {batch['metadatos']['duracion_ms']}ms\n")
    
    for resultado in batch['resultados']:
        idx = resultado['índice']
        if 'error' in resultado:
            print(f"Documento {idx}: ERROR - {resultado['error']}")
        else:
            print(f"Documento {idx}: Score {resultado['score_general']:.1f} - {resultado['nivel_riesgo']}")


def ejemplo_auditoría():
    """Ejemplo: Consultar auditoría"""
    
    cliente = CentinelaAPIClientV2_2()
    cliente.login("admin", "admin123")
    
    print("\n" + "="*60)
    print("EJEMPLO 4: Auditoría y Log")
    print("="*60 + "\n")
    
    # Log de actividades
    log = cliente.obtener_log_actividad(días=7, límite=5)
    print(f"Total de actividades (últimos 7 días): {log['total_registros']}\n")
    
    print("Últimas actividades:")
    for actividad in log['actividades'][:3]:
        print(f"  {actividad['timestamp']}: {actividad['tipo_actividad']}")
        print(f"    Estado: {actividad['estado']}, Duración: {actividad['duracion_ms']}ms")
    
    # Reporte de auditoría
    print("\n" + "-"*60 + "\n")
    
    reporte = cliente.obtener_reporte_auditoria()
    print(f"Usuario: {reporte['usuario']}")
    print(f"Total actividades: {reporte['resumen']['total_actividades']}")
    print(f"Total análisis: {reporte['resumen']['total_análisis']}")
    print(f"Score promedio: {reporte['análisis'].get('score_promedio', 0):.1f}")
    print(f"Documentos críticos: {reporte['análisis'].get('documentos_críticos', 0)}")


if __name__ == "__main__":
    try:
        ejemplo_análisis_completo()
        ejemplo_integridad_científica()
        ejemplo_procesamiento_lote()
        ejemplo_auditoría()
        
        print("\n" + "="*60)
        print("✓ Todos los ejemplos completados exitosamente")
        print("="*60 + "\n")
    
    except Exception as e:
        print(f"\n✗ Error: {str(e)}\n")
