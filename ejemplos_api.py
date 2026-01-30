#!/usr/bin/env python3
"""
Script de Ejemplo: Uso de la API Centinela Digital
Demuestra cómo consumir todos los endpoints
"""

import requests
import json
from typing import Dict

# Configuración
API_URL = "http://localhost:5000"

class CentinelaClient:
    """Cliente para consumir la API de Centinela Digital."""
    
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    # ========================
    # ANÁLISIS
    # ========================
    
    def analizar_documento(self, 
                          rol: str = "Estudiante",
                          tipo_producto: str = "Ensayo",
                          evidencias: Dict = None) -> Dict:
        """
        Analizar un documento para detectar fraude académico.
        
        Args:
            rol: 'Estudiante', 'Docente-investigador', 'Coinvestigador externo'
            tipo_producto: 'Ensayo', 'Tesis', 'Artículo científico', etc.
            evidencias: Dict con señales de alerta
        
        Returns:
            Dict con resultado del análisis
        
        Ejemplo:
        >>> client = CentinelaClient()
        >>> result = client.analizar_documento(
        ...     rol="Estudiante",
        ...     tipo_producto="Ensayo",
        ...     evidencias={
        ...         "estilo_diferente": 1,
        ...         "tiempo_sospechoso": 0,
        ...         "referencias_raras": 1,
        ...         "datos_inconsistentes": 0,
        ...         "imagenes_sospechosas": 0,
        ...         "sin_borradores": 0,
        ...         "defensa_debil": 0
        ...     }
        ... )
        >>> print(f"Riesgo: {result['overall_level']}")
        Riesgo: MEDIO
        """
        if evidencias is None:
            evidencias = {
                "estilo_diferente": 0,
                "tiempo_sospechoso": 0,
                "referencias_raras": 0,
                "datos_inconsistentes": 0,
                "imagenes_sospechosas": 0,
                "sin_borradores": 0,
                "defensa_debil": 0,
            }
        
        payload = {
            "rol": rol,
            "tipo_producto": tipo_producto,
            "evidencias": evidencias
        }
        
        response = self.session.post(
            f"{self.base_url}/api/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            return response.json()["analysis"]
        else:
            raise Exception(f"Error: {response.text}")
    
    # ========================
    # CONSULTAS
    # ========================
    
    def obtener_caso(self, case_id: str) -> Dict:
        """
        Obtener detalles de un caso específico.
        
        Args:
            case_id: ID del caso
        
        Returns:
            Dict con detalles del caso
        """
        response = self.session.get(f"{self.base_url}/api/case/{case_id}")
        
        if response.status_code == 200:
            return response.json()["case"]
        else:
            raise Exception(f"Caso no encontrado: {case_id}")
    
    def listar_casos(self, 
                     limit: int = 50,
                     offset: int = 0,
                     nivel: str = None,
                     rol: str = None) -> Dict:
        """
        Listar casos con filtros opcionales.
        
        Args:
            limit: Número de casos a retornar
            offset: Desplazamiento para paginación
            nivel: Filtrar por nivel ('ALTO', 'MEDIO', 'BAJO')
            rol: Filtrar por rol
        
        Returns:
            Dict con lista de casos
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if nivel:
            params["nivel"] = nivel
        if rol:
            params["rol"] = rol
        
        response = self.session.get(
            f"{self.base_url}/api/cases",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "total": data["total"],
                "casos": data["cases"],
                "limit": limit,
                "offset": offset
            }
        else:
            raise Exception(f"Error listando casos: {response.text}")
    
    # ========================
    # MÉTRICAS
    # ========================
    
    def metricas_institucionales(self) -> Dict:
        """
        Obtener métricas agregadas de todos los casos.
        
        Returns:
            Dict con métricas institucionales
        
        Incluye:
        - Total de casos analizados
        - Distribución por rol
        - Distribución por tipo de producto
        - Tasas de riesgo
        - Puntuaciones promedio
        """
        response = self.session.get(f"{self.base_url}/api/metrics/institutional")
        
        if response.status_code == 200:
            return response.json()["metrics"]
        else:
            raise Exception(f"Error obteniendo métricas: {response.text}")
    
    def metricas_temporales(self, periodo: str = "daily") -> Dict:
        """
        Obtener análisis de evolución temporal.
        
        Args:
            periodo: 'daily', 'weekly', 'monthly'
        
        Returns:
            Dict con evolución temporal
        
        Muestra:
        - Casos por período
        - Distribución de riesgo por período
        - Score promedio por período
        - Confianza promedio por período
        """
        response = self.session.get(
            f"{self.base_url}/api/metrics/temporal",
            params={"period": periodo}
        )
        
        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"Error obteniendo métricas temporales: {response.text}")
    
    # ========================
    # INFORMACIÓN
    # ========================
    
    def obtener_info(self) -> Dict:
        """
        Obtener información de la API y opciones válidas.
        
        Returns:
            Dict con información de la API
        """
        response = self.session.get(f"{self.base_url}/api/info")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error obteniendo info: {response.text}")
    
    def health_check(self) -> bool:
        """
        Verificar que la API está disponible.
        
        Returns:
            True si la API está sana, False en caso contrario
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False


def ejemplo_1_analisis_simple():
    """Ejemplo 1: Análisis simple de un documento."""
    print("\n" + "="*70)
    print("EJEMPLO 1: Análisis Simple")
    print("="*70)
    
    client = CentinelaClient()
    
    # Verificar que API está disponible
    if not client.health_check():
        print("❌ API no disponible. Ejecuta: python3 run_api.sh")
        return
    
    print("✓ API disponible")
    
    # Analizar documento con algunas señales de alerta
    resultado = client.analizar_documento(
        rol="Estudiante",
        tipo_producto="Ensayo",
        evidencias={
            "estilo_diferente": 1,      # Sí
            "tiempo_sospechoso": 0,      # No
            "referencias_raras": 1,      # Sí
            "datos_inconsistentes": 0,   # No
            "imagenes_sospechosas": 0,   # No
            "sin_borradores": 0,         # No
            "defensa_debil": 0,          # No
        }
    )
    
    print(f"\nResultado del análisis:")
    print(f"  Score: {resultado['overall_score']}")
    print(f"  Nivel: {resultado['overall_level']}")
    print(f"  Confianza: {resultado['confidence']}")
    print(f"  Recomendaciones:")
    for rec in resultado.get('recommendations', []):
        print(f"    - {rec}")


def ejemplo_2_listar_casos():
    """Ejemplo 2: Listar casos con filtros."""
    print("\n" + "="*70)
    print("EJEMPLO 2: Listar Casos")
    print("="*70)
    
    client = CentinelaClient()
    
    # Listar primeros 10 casos
    resultado = client.listar_casos(limit=10, offset=0)
    
    print(f"\nTotal de casos: {resultado['total']}")
    print(f"Casos retornados: {len(resultado['casos'])}")
    
    if resultado['casos']:
        print("\nPrimeros 3 casos:")
        for i, caso in enumerate(resultado['casos'][:3], 1):
            print(f"  {i}. {caso['case_id']}")
            print(f"     Rol: {caso['role']}")
            print(f"     Riesgo: {caso['overall_level']} ({caso['overall_score']})")


def ejemplo_3_metricas():
    """Ejemplo 3: Obtener métricas institucionales."""
    print("\n" + "="*70)
    print("EJEMPLO 3: Métricas Institucionales")
    print("="*70)
    
    client = CentinelaClient()
    
    metricas = client.metricas_institucionales()
    
    print(f"\nResumen General:")
    general = metricas.get('resumen_general', {})
    print(f"  Total de casos: {general.get('total_casos_analizados')}")
    
    tasas = metricas.get('tasas_por_nivel', {})
    print(f"\nTasas por Nivel:")
    print(f"  ALTO: {tasas.get('ALTO')}%")
    print(f"  MEDIO: {tasas.get('MEDIO')}%")
    print(f"  BAJO: {tasas.get('BAJO')}%")
    
    roles = general.get('distribucion_roles', {})
    print(f"\nDistribución por Rol:")
    for rol, count in roles.items():
        print(f"  {rol}: {count}")


def ejemplo_4_temporal():
    """Ejemplo 4: Análisis temporal."""
    print("\n" + "="*70)
    print("EJEMPLO 4: Análisis Temporal")
    print("="*70)
    
    client = CentinelaClient()
    
    temporal = client.metricas_temporales(periodo="daily")
    
    print(f"\nPeriodos disponibles: {len(temporal)}")
    
    if temporal:
        print("\nÚltimos 3 períodos:")
        for periodo in temporal[-3:]:
            print(f"  {periodo['periodo']}")
            print(f"    Casos totales: {periodo['total_casos']}")
            print(f"    Score promedio: {periodo['score_promedio']}")
            print(f"    Confianza promedio: {periodo['confianza_promedio']}")


def ejemplo_5_flujo_completo():
    """Ejemplo 5: Flujo completo de trabajo."""
    print("\n" + "="*70)
    print("EJEMPLO 5: Flujo Completo")
    print("="*70)
    
    client = CentinelaClient()
    
    # Paso 1: Verificar disponibilidad
    print("\n1️⃣  Verificando disponibilidad...")
    if not client.health_check():
        print("   ❌ API no disponible")
        return
    print("   ✓ API disponible")
    
    # Paso 2: Obtener información
    print("\n2️⃣  Obteniendo información de la API...")
    info = client.obtener_info()
    print(f"   ✓ API: {info['name']} v{info['version']}")
    
    # Paso 3: Analizar documento
    print("\n3️⃣  Analizando documento...")
    resultado = client.analizar_documento(
        rol="Estudiante",
        tipo_producto="Tesis",
        evidencias={
            "estilo_diferente": 0,
            "tiempo_sospechoso": 1,
            "referencias_raras": 0,
            "datos_inconsistentes": 1,
            "imagenes_sospechosas": 0,
            "sin_borradores": 0,
            "defensa_debil": 0,
        }
    )
    print(f"   ✓ Análisis completo: {resultado['overall_level']}")
    
    # Paso 4: Listar casos
    print("\n4️⃣  Listando casos...")
    casos = client.listar_casos(limit=5)
    print(f"   ✓ Total de casos: {casos['total']}")
    
    # Paso 5: Ver métricas
    print("\n5️⃣  Consultando métricas...")
    metricas = client.metricas_institucionales()
    general = metricas.get('resumen_general', {})
    print(f"   ✓ Casos analizados: {general.get('total_casos_analizados')}")
    
    print("\n✅ Flujo completo ejecutado exitosamente")


def main():
    """Función principal."""
    print("\n╔" + "="*68 + "╗")
    print("║" + " " * 10 + "📚 EJEMPLOS DE USO - CENTINELA DIGITAL API 📚" + " " * 12 + "║")
    print("╚" + "="*68 + "╝")
    
    print("\nEjemplos disponibles:")
    print("  1. Análisis simple de un documento")
    print("  2. Listar casos con filtros")
    print("  3. Obtener métricas institucionales")
    print("  4. Análisis temporal")
    print("  5. Flujo completo de trabajo")
    print("  6. Ejecutar todos")
    
    opcion = input("\nSelecciona ejemplo (1-6): ").strip()
    
    try:
        if opcion == "1":
            ejemplo_1_analisis_simple()
        elif opcion == "2":
            ejemplo_2_listar_casos()
        elif opcion == "3":
            ejemplo_3_metricas()
        elif opcion == "4":
            ejemplo_4_temporal()
        elif opcion == "5":
            ejemplo_5_flujo_completo()
        elif opcion == "6":
            ejemplo_1_analisis_simple()
            ejemplo_2_listar_casos()
            ejemplo_3_metricas()
            ejemplo_4_temporal()
            ejemplo_5_flujo_completo()
        else:
            print("Opción no válida")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n⚠️  Asegúrate de que la API esté corriendo:")
        print("   python3 run_api.sh")


if __name__ == "__main__":
    main()
