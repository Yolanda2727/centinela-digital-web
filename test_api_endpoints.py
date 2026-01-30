#!/usr/bin/env python3
"""
Script para probar todos los endpoints de la API REST
Ejecuta desde otra terminal mientras API está corriendo
"""

import requests
import json
import sys
import time
from typing import Dict, Any

# Configuración
API_BASE_URL = "http://localhost:5000"
TIMEOUT = 5

class APITester:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Realiza una petición HTTP."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, timeout=TIMEOUT)
            elif method == "POST":
                response = self.session.post(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=TIMEOUT
                )
            else:
                raise ValueError(f"Método no soportado: {method}")
            
            return {
                "status": response.status_code,
                "data": response.json() if response.text else {},
                "success": 200 <= response.status_code < 300
            }
        
        except requests.exceptions.ConnectionError:
            return {
                "status": 0,
                "data": {},
                "success": False,
                "error": "No se pudo conectar a la API"
            }
        except Exception as e:
            return {
                "status": 0,
                "data": {},
                "success": False,
                "error": str(e)
            }
    
    def test_health(self):
        """Prueba: Health Check."""
        print("\n📍 Test 1: Health Check")
        print("-" * 70)
        
        self.results["total"] += 1
        
        result = self._request("GET", "/health")
        
        if result["success"]:
            print(f"✓ Status: {result['status']}")
            print(f"✓ API está sana")
            print(f"  Timestamp: {result['data'].get('timestamp')}")
            self.results["passed"] += 1
            return True
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            self.results["failed"] += 1
            self.results["errors"].append("Health check falló")
            return False
    
    def test_info(self):
        """Prueba: Información de API."""
        print("\n📍 Test 2: Información de API")
        print("-" * 70)
        
        self.results["total"] += 1
        
        result = self._request("GET", "/api/info")
        
        if result["success"]:
            data = result["data"]
            print(f"✓ Status: {result['status']}")
            print(f"✓ Nombre: {data.get('nombre')}")
            print(f"✓ Versión: {data.get('version')}")
            print(f"✓ Endpoints: {len(data.get('endpoints', []))}")
            self.results["passed"] += 1
            return True
        else:
            print(f"❌ Error: {result.get('error')}")
            self.results["failed"] += 1
            self.results["errors"].append("Info endpoint falló")
            return False
    
    def test_analyze_low_risk(self):
        """Prueba: Análisis de caso bajo riesgo."""
        print("\n📍 Test 3: Analizar Caso Bajo Riesgo")
        print("-" * 70)
        
        self.results["total"] += 1
        
        payload = {
            "rol": "Estudiante",
            "tipo_producto": "Ensayo",
            "evidencias": {
                "estilo_diferente": 0,
                "tiempo_sospechoso": 0,
                "referencias_raras": 0,
                "datos_inconsistentes": 0,
                "imagenes_sospechosas": 0,
                "sin_borradores": 0,
                "defensa_debil": 0,
            }
        }
        
        result = self._request("POST", "/api/analyze", payload)
        
        if result["success"]:
            data = result["data"]
            print(f"✓ Status: {result['status']}")
            print(f"✓ Case ID: {data.get('case_id')}")
            print(f"✓ Score: {data.get('overall_score')}")
            print(f"✓ Nivel: {data.get('overall_level')}")
            print(f"✓ Confianza: {data.get('confidence')}")
            
            # Validar que el nivel sea BAJO
            if data.get('overall_level') == 'BAJO':
                print("✓ Nivel de riesgo correcto")
                self.results["passed"] += 1
                return True
            else:
                print(f"❌ Nivel esperado BAJO, obtenido {data.get('overall_level')}")
                self.results["failed"] += 1
                self.results["errors"].append("Nivel de riesgo incorrecto (caso bajo)")
                return False
        else:
            print(f"❌ Error: {result.get('error')}")
            self.results["failed"] += 1
            self.results["errors"].append("Análisis bajo riesgo falló")
            return False
    
    def test_analyze_high_risk(self):
        """Prueba: Análisis de caso alto riesgo."""
        print("\n📍 Test 4: Analizar Caso Alto Riesgo")
        print("-" * 70)
        
        self.results["total"] += 1
        
        payload = {
            "rol": "Estudiante",
            "tipo_producto": "Ensayo",
            "evidencias": {
                "estilo_diferente": 1,
                "tiempo_sospechoso": 1,
                "referencias_raras": 1,
                "datos_inconsistentes": 1,
                "imagenes_sospechosas": 1,
                "sin_borradores": 1,
                "defensa_debil": 1,
            }
        }
        
        result = self._request("POST", "/api/analyze", payload)
        
        if result["success"]:
            data = result["data"]
            print(f"✓ Status: {result['status']}")
            print(f"✓ Case ID: {data.get('case_id')}")
            print(f"✓ Score: {data.get('overall_score')}")
            print(f"✓ Nivel: {data.get('overall_level')}")
            print(f"✓ Recomendaciones: {len(data.get('recommendations', []))} items")
            
            # Validar que el nivel sea ALTO
            if data.get('overall_level') == 'ALTO':
                print("✓ Nivel de riesgo correcto")
                self.results["passed"] += 1
                self.case_id_high = data.get('case_id')
                return True
            else:
                print(f"❌ Nivel esperado ALTO, obtenido {data.get('overall_level')}")
                self.results["failed"] += 1
                self.results["errors"].append("Nivel de riesgo incorrecto (caso alto)")
                return False
        else:
            print(f"❌ Error: {result.get('error')}")
            self.results["failed"] += 1
            self.results["errors"].append("Análisis alto riesgo falló")
            return False
    
    def test_get_case(self):
        """Prueba: Obtener un caso específico."""
        print("\n📍 Test 5: Obtener Caso Específico")
        print("-" * 70)
        
        self.results["total"] += 1
        
        # Primero analizar para obtener un case_id
        payload = {
            "rol": "Investigador Externo",
            "tipo_producto": "Investigación",
            "evidencias": {
                "estilo_diferente": 0,
                "tiempo_sospechoso": 0,
                "referencias_raras": 0,
                "datos_inconsistentes": 0,
                "imagenes_sospechosas": 0,
                "sin_borradores": 0,
                "defensa_debil": 0,
            }
        }
        
        analyze_result = self._request("POST", "/api/analyze", payload)
        
        if not analyze_result["success"]:
            print(f"❌ No se pudo crear caso para prueba")
            self.results["failed"] += 1
            self.results["errors"].append("Get case test: crear caso falló")
            return False
        
        case_id = analyze_result["data"].get("case_id")
        
        # Ahora obtener el caso
        result = self._request("GET", f"/api/case/{case_id}")
        
        if result["success"]:
            data = result["data"]
            print(f"✓ Status: {result['status']}")
            print(f"✓ Case ID: {data.get('caso_id')}")
            print(f"✓ Rol: {data.get('rol')}")
            print(f"✓ Tipo: {data.get('tipo_producto')}")
            print(f"✓ Nivel Riesgo: {data.get('nivel_riesgo')}")
            self.results["passed"] += 1
            return True
        else:
            print(f"❌ Error: {result.get('error')}")
            self.results["failed"] += 1
            self.results["errors"].append("Get case falló")
            return False
    
    def test_list_cases(self):
        """Prueba: Listar casos."""
        print("\n📍 Test 6: Listar Casos")
        print("-" * 70)
        
        self.results["total"] += 1
        
        result = self._request("GET", "/api/cases?limite=5&offset=0")
        
        if result["success"]:
            data = result["data"]
            print(f"✓ Status: {result['status']}")
            print(f"✓ Total de casos: {data.get('total')}")
            print(f"✓ Casos en página: {len(data.get('casos', []))}")
            print(f"✓ Límite: {data.get('limite')}")
            self.results["passed"] += 1
            return True
        else:
            print(f"❌ Error: {result.get('error')}")
            self.results["failed"] += 1
            self.results["errors"].append("List cases falló")
            return False
    
    def test_institutional_metrics(self):
        """Prueba: Métricas institucionales."""
        print("\n📍 Test 7: Métricas Institucionales")
        print("-" * 70)
        
        self.results["total"] += 1
        
        result = self._request("GET", "/api/metrics/institutional")
        
        if result["success"]:
            data = result["data"]
            print(f"✓ Status: {result['status']}")
            general = data.get('resumen_general', {})
            print(f"✓ Total casos analizados: {general.get('total_casos_analizados')}")
            tasas = data.get('tasas_por_nivel', {})
            print(f"✓ Tasa Alto Riesgo: {tasas.get('ALTO')}%")
            print(f"✓ Tasa Medio Riesgo: {tasas.get('MEDIO')}%")
            print(f"✓ Tasa Bajo Riesgo: {tasas.get('BAJO')}%")
            self.results["passed"] += 1
            return True
        else:
            print(f"❌ Error: {result.get('error')}")
            self.results["failed"] += 1
            self.results["errors"].append("Institutional metrics falló")
            return False
    
    def test_temporal_metrics(self):
        """Prueba: Métricas temporales."""
        print("\n📍 Test 8: Métricas Temporales")
        print("-" * 70)
        
        self.results["total"] += 1
        
        result = self._request("GET", "/api/metrics/temporal?agrupacion=diaria")
        
        if result["success"]:
            data = result["data"]
            print(f"✓ Status: {result['status']}")
            print(f"✓ Agrupación: {data.get('agrupacion')}")
            print(f"✓ Períodos: {len(data.get('periodos', []))}")
            self.results["passed"] += 1
            return True
        else:
            print(f"❌ Error: {result.get('error')}")
            self.results["failed"] += 1
            self.results["errors"].append("Temporal metrics falló")
            return False
    
    def run_all_tests(self):
        """Ejecuta todos los tests."""
        print("\n")
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 12 + "🧪 PRUEBAS DE ENDPOINTS REST API 🧪" + " " * 15 + "║")
        print("╚" + "=" * 68 + "╝")
        print()
        
        # Verificar conexión
        print("⏳ Conectando a API...")
        if not self.test_health():
            print("\n❌ No se puede conectar a la API")
            print("   Asegúrate de ejecutar: python3 run_api.sh")
            return False
        
        # Ejecutar tests
        self.test_info()
        self.test_analyze_low_risk()
        self.test_analyze_high_risk()
        self.test_get_case()
        self.test_list_cases()
        self.test_institutional_metrics()
        self.test_temporal_metrics()
        
        # Resumen
        self.print_summary()
        return self.results["failed"] == 0
    
    def print_summary(self):
        """Imprime resumen de resultados."""
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 70)
        print(f"Total: {self.results['total']}")
        print(f"✓ Exitosos: {self.results['passed']}")
        print(f"❌ Fallidos: {self.results['failed']}")
        
        if self.results["errors"]:
            print("\nErrores encontrados:")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        if self.results["total"] > 0:
            success_rate = (self.results["passed"] / self.results["total"]) * 100
            print(f"\n✓ Tasa de éxito: {success_rate:.1f}%")
            
            if success_rate == 100:
                print("🎉 TODOS LOS TESTS PASARON")
            elif success_rate >= 80:
                print("✓ La mayoría de tests pasaron")
            else:
                print("❌ Muchos tests fallaron")
        
        print("=" * 70)


def main():
    """Punto de entrada."""
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    else:
        api_url = API_BASE_URL
    
    print(f"Objetivo: {api_url}")
    
    tester = APITester(api_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
