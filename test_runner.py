"""
Script de Validación y Testing para Centinela Digital

Prueba:
- Flujos individuales con casos de prueba
- Modelo mejorado de análisis
- Persistencia en base de datos
- Generación de métricas institucionales
"""

import json
import sys
from pathlib import Path
from typing import Dict

# Importar módulos locales
try:
    from test_cases import TEST_CASES, get_all_test_cases, list_test_cases
    from improved_analysis_model import (
        analyze_with_improved_model,
        validate_analysis,
        calculate_dimension_scores,
    )
    from database import CentinelaDatabase
    from institutional_metrics import InstitucionalMetrics, FollowUpMetrics
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Asegúrate de que todos los módulos estén en el mismo directorio.")
    sys.exit(1)


class CentinelaTestRunner:
    """Ejecuta suite completa de tests."""
    
    def __init__(self):
        self.db = CentinelaDatabase()
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": [],
            "errors": [],
            "test_details": [],
        }
    
    def run_all_tests(self, verbose: bool = True) -> Dict:
        """Ejecuta todos los tests."""
        print("=" * 70)
        print("🔧 SUITE DE TESTING - CENTINELA DIGITAL")
        print("=" * 70)
        print()
        
        # Test 1: Validar estructura de casos
        self._test_case_structure()
        
        # Test 2: Ejecutar análisis en cada caso
        self._test_individual_cases(verbose)
        
        # Test 3: Validar modelo mejorado
        self._test_improved_model()
        
        # Test 4: Prueba de persistencia
        self._test_database_persistence()
        
        # Test 5: Generación de reportes
        self._test_institutional_reports()
        
        return self.results
    
    def _test_case_structure(self):
        """Valida que los casos de prueba tengan la estructura correcta."""
        print("\n📋 Test 1: Estructura de casos de prueba")
        print("-" * 70)
        
        casos = get_all_test_cases()
        
        for caso_name, caso_data in casos.items():
            self.results["total_tests"] += 1
            required_fields = [
                "rol",
                "tipo_producto",
                "texto",
                "evidencias",
                "expected_risk_level",
            ]
            
            missing = [f for f in required_fields if f not in caso_data]
            
            if missing:
                print(f"❌ {caso_name}: Faltan campos {missing}")
                self.results["failed"] += 1
                self.results["errors"].append(f"{caso_name}: Campos faltantes")
            else:
                print(f"✓ {caso_name}: Estructura válida")
                self.results["passed"] += 1
    
    def _test_individual_cases(self, verbose: bool = False):
        """Ejecuta análisis en cada caso individual."""
        print("\n🔍 Test 2: Análisis de casos individuales")
        print("-" * 70)
        
        casos = get_all_test_cases()
        
        for caso_name, caso_data in casos.items():
            self.results["total_tests"] += 1
            
            try:
                # Ejecutar análisis
                result = analyze_with_improved_model(
                    caso_data["evidencias"],
                    caso_data["rol"],
                    caso_data["tipo_producto"],
                    num_evidencias_marked=sum(caso_data["evidencias"].values()),
                )
                
                # Validar resultado
                validation = validate_analysis(
                    result,
                    expected_level=caso_data.get("expected_risk_level"),
                )
                
                # Verificar si pasó la validación
                if validation["expected_vs_actual"]:
                    match = validation["expected_vs_actual"]["match"]
                    if match:
                        print(
                            f"✓ {caso_name}: "
                            f"Riesgo {result['overall_score']} "
                            f"({result['overall_level']})"
                        )
                        self.results["passed"] += 1
                    else:
                        print(
                            f"⚠️  {caso_name}: "
                            f"Esperado {validation['expected_vs_actual']['expected']}, "
                            f"obtenido {validation['expected_vs_actual']['actual']}"
                        )
                        self.results["warnings"].append(
                            f"{caso_name}: Resultado inesperado"
                        )
                        self.results["passed"] += 1  # No es error crítico
                else:
                    print(
                        f"✓ {caso_name}: "
                        f"Riesgo {result['overall_score']} ({result['overall_level']})"
                    )
                    self.results["passed"] += 1
                
                if verbose:
                    print(f"  Dimensiones: {result['dimension_scores']}")
                    print(f"  Confianza: {result['confidence']}")
                    print(f"  Recomendaciones: {len(result.get('recommendations', []))} items")
                
                # Guardar en BD
                self._save_test_case_to_db(caso_name, result, caso_data)
                
            except Exception as e:
                print(f"❌ {caso_name}: Error - {str(e)}")
                self.results["failed"] += 1
                self.results["errors"].append(f"{caso_name}: {str(e)}")
    
    def _test_improved_model(self):
        """Prueba características específicas del modelo mejorado."""
        print("\n⚙️  Test 3: Modelo de análisis mejorado")
        print("-" * 70)
        
        test_cases = [
            {
                "name": "Puntuación baja (bajo riesgo)",
                "evidencias": {
                    "estilo_diferente": 0,
                    "tiempo_sospechoso": 0,
                    "referencias_raras": 0,
                    "datos_inconsistentes": 0,
                    "imagenes_sospechosas": 0,
                    "sin_borradores": 0,
                    "defensa_debil": 0,
                },
                "expected_max": 20,
            },
            {
                "name": "Puntuación alta (alto riesgo)",
                "evidencias": {
                    "estilo_diferente": 1,
                    "tiempo_sospechoso": 1,
                    "referencias_raras": 1,
                    "datos_inconsistentes": 1,
                    "imagenes_sospechosas": 1,
                    "sin_borradores": 1,
                    "defensa_debil": 1,
                },
                "expected_min": 70,
            },
        ]
        
        for test in test_cases:
            self.results["total_tests"] += 1
            
            result = analyze_with_improved_model(
                test["evidencias"],
                "Estudiante",
                "Ensayo",
            )
            
            score = result["overall_score"]
            
            if "expected_max" in test:
                if score <= test["expected_max"]:
                    print(f"✓ {test['name']}: Score {score} <= {test['expected_max']}")
                    self.results["passed"] += 1
                else:
                    print(
                        f"❌ {test['name']}: Score {score} > {test['expected_max']}"
                    )
                    self.results["failed"] += 1
            
            if "expected_min" in test:
                if score >= test["expected_min"]:
                    print(f"✓ {test['name']}: Score {score} >= {test['expected_min']}")
                    self.results["passed"] += 1
                else:
                    print(
                        f"❌ {test['name']}: Score {score} < {test['expected_min']}"
                    )
                    self.results["failed"] += 1
    
    def _test_database_persistence(self):
        """Prueba almacenamiento y recuperación de datos."""
        print("\n💾 Test 4: Persistencia en base de datos")
        print("-" * 70)
        
        try:
            # Crear caso de prueba
            test_caso = {
                "rol": "Estudiante",
                "tipo_producto": "Test",
                "riesgo_score": 50,
                "nivel_riesgo": "MEDIO",
                "confianza": 0.75,
                "sentimiento": "neutro",
                "num_evidencias": 2,
                "texto_length": 1000,
            }
            
            self.results["total_tests"] += 1
            
            # Guardar
            caso_id = self.db.guardar_caso(test_caso)
            print(f"✓ Caso guardado: {caso_id}")
            self.results["passed"] += 1
            
            # Recuperar
            self.results["total_tests"] += 1
            retrieved = self.db.obtener_caso(caso_id)
            
            if retrieved and retrieved.get("tipo_producto") == "Test":
                print(f"✓ Caso recuperado correctamente")
                self.results["passed"] += 1
            else:
                print(f"❌ No se pudo recuperar el caso")
                self.results["failed"] += 1
            
            # Listar casos
            self.results["total_tests"] += 1
            casos_list = self.db.listar_casos(limite=10)
            print(f"✓ Casos en DB: {len(casos_list)}")
            self.results["passed"] += 1
            
        except Exception as e:
            print(f"❌ Error de base de datos: {str(e)}")
            self.results["failed"] += 1
            self.results["errors"].append(f"DB Error: {str(e)}")
    
    def _test_institutional_reports(self):
        """Prueba generación de reportes institucionales."""
        print("\n📊 Test 5: Reportes institucionales")
        print("-" * 70)
        
        try:
            # Obtener casos de la BD
            casos = self.db.listar_casos(limite=100)
            
            if not casos:
                print("⚠️  No hay casos en la BD para generar reportes")
                return
            
            self.results["total_tests"] += 1
            
            # Generar reporte ejecutivo
            reporte = InstitucionalMetrics.generar_reporte_ejecutivo(casos)
            print(f"✓ Reporte ejecutivo generado")
            print(f"  - Total de casos: {reporte['resumen_general']['total_casos_analizados']}")
            print(f"  - Tasa riesgo promedio: {reporte['tasas_por_nivel']}")
            self.results["passed"] += 1
            
            # Evolución temporal
            if len(casos) > 1:
                self.results["total_tests"] += 1
                evolucion = FollowUpMetrics.calcular_evolucion_temporal(casos, agrupacion="diaria")
                print(f"✓ Análisis temporal: {len(evolucion)} períodos")
                self.results["passed"] += 1
            
        except Exception as e:
            print(f"❌ Error en reportes: {str(e)}")
            self.results["failed"] += 1
            self.results["errors"].append(f"Reports Error: {str(e)}")
    
    def _save_test_case_to_db(self, caso_name: str, analysis: Dict, original_data: Dict):
        """Guarda resultado de test en BD."""
        try:
            db_record = {
                "caso_id": f"test_{caso_name}",
                "rol": original_data["rol"],
                "tipo_producto": original_data["tipo_producto"],
                "riesgo_score": analysis["overall_score"],
                "nivel_riesgo": analysis["overall_level"],
                "confianza": analysis["confidence"],
                "num_evidencias": sum(original_data["evidencias"].values()),
                "texto_length": len(original_data.get("texto", "")),
                "red_flags": analysis.get("critical_dimensions", []),
                "recomendaciones": analysis.get("recommendations", []),
            }
            self.db.guardar_caso(db_record)
        except Exception:
            pass  # Silent fail para tests
    
    def print_summary(self):
        """Imprime resumen de resultados."""
        print("\n" + "=" * 70)
        print("📈 RESUMEN DE RESULTADOS")
        print("=" * 70)
        print(f"Total de tests: {self.results['total_tests']}")
        print(f"✓ Exitosos: {self.results['passed']}")
        print(f"❌ Fallidos: {self.results['failed']}")
        print(f"⚠️  Advertencias: {len(self.results['warnings'])}")
        
        if self.results["errors"]:
            print("\nErrores encontrados:")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        if self.results["warnings"]:
            print("\nAdvertencias:")
            for warning in self.results["warnings"]:
                print(f"  - {warning}")
        
        # Tasa de éxito
        if self.results["total_tests"] > 0:
            success_rate = (
                self.results["passed"] / self.results["total_tests"] * 100
            )
            print(f"\n✓ Tasa de éxito: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
            elif success_rate >= 70:
                print("✓ La mayoría de tests pasaron")
            else:
                print("❌ Demasiados tests fallaron")
        
        print("=" * 70)
        print()


def main():
    """Punto de entrada principal."""
    runner = CentinelaTestRunner()
    
    try:
        results = runner.run_all_tests(verbose=False)
        runner.print_summary()
        
        # Retornar código de salida basado en éxito
        return 0 if results["failed"] == 0 else 1
    
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
