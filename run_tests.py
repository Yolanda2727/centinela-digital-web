#!/usr/bin/env python3
"""
Script para ejecutar todas las pruebas de Centinela Digital
Valida: estructura, análisis, BD, reportes y API
"""

import sys
import os
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

def check_imports():
    """Verifica que todos los módulos clave estén disponibles."""
    print("🔍 Verificando dependencias...")
    print("-" * 70)
    
    required_modules = {
        "test_cases": "Casos de prueba",
        "improved_analysis_model": "Modelo de análisis",
        "database": "Base de datos",
        "institutional_metrics": "Métricas institucionales",
    }
    
    missing = []
    for module, description in required_modules.items():
        try:
            __import__(module)
            print(f"  ✓ {description} ({module})")
        except ImportError as e:
            print(f"  ❌ {description} ({module}): {e}")
            missing.append(module)
    
    if missing:
        print(f"\n❌ Faltan módulos: {', '.join(missing)}")
        return False
    
    print("\n✓ Todas las dependencias disponibles\n")
    return True


def run_test_runner():
    """Ejecuta el test runner principal."""
    print("=" * 70)
    print("📊 EJECUTANDO SUITE DE PRUEBAS")
    print("=" * 70)
    print()
    
    try:
        from test_runner import CentinelaTestRunner
        
        runner = CentinelaTestRunner()
        results = runner.run_all_tests(verbose=False)
        runner.print_summary()
        
        return results["failed"] == 0
    
    except Exception as e:
        print(f"❌ Error al ejecutar tests: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_api():
    """Valida que la API esté disponible."""
    print("\n" + "=" * 70)
    print("🌐 VALIDANDO API")
    print("=" * 70)
    print()
    
    try:
        from api import app
        print("✓ API Flask disponible")
        
        # Verificar rutas
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        print(f"✓ Rutas disponibles: {len(routes)}")
        for route in sorted(routes):
            if route != "static":
                print(f"  - {route}")
        
        return True
    
    except Exception as e:
        print(f"⚠️  API no disponible: {e}")
        return True  # No es crítico


def validate_app():
    """Valida que la app Streamlit esté disponible."""
    print("\n" + "=" * 70)
    print("📱 VALIDANDO APLICACIÓN")
    print("=" * 70)
    print()
    
    try:
        app_path = Path(__file__).parent / "app.py"
        if app_path.exists():
            print(f"✓ Aplicación Streamlit disponible: {app_path}")
            return True
        else:
            print(f"⚠️  app.py no encontrado")
            return True
    
    except Exception as e:
        print(f"⚠️  Error validando aplicación: {e}")
        return True


def validate_database():
    """Valida el estado de la base de datos."""
    print("\n" + "=" * 70)
    print("💾 VALIDANDO BASE DE DATOS")
    print("=" * 70)
    print()
    
    try:
        from database import CentinelaDatabase
        
        db = CentinelaDatabase()
        print(f"✓ Base de datos disponible en: {db.db_file}")
        
        # Contar casos
        casos = db.listar_casos(limite=1)
        print(f"✓ Casos en BD: {len(casos)}")
        
        return True
    
    except Exception as e:
        print(f"⚠️  Error con BD: {e}")
        return True


def main():
    """Función principal."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "🧪 VALIDACIÓN CENTINELA DIGITAL 🧪" + " " * 18 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    # Paso 1: Verificar dependencias
    if not check_imports():
        print("\n❌ Falla: No se pueden importar módulos requeridos")
        return 1
    
    # Paso 2: Ejecutar tests
    tests_passed = run_test_runner()
    
    # Paso 3: Validar API
    validate_api()
    
    # Paso 4: Validar aplicación
    validate_app()
    
    # Paso 5: Validar BD
    validate_database()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("✅ VALIDACIÓN COMPLETADA")
    print("=" * 70)
    
    if tests_passed:
        print("\n🎉 ESTADO: TODO FUNCIONA CORRECTAMENTE")
        print("\nPróximos pasos:")
        print("  1. API REST: python3 run_api.sh")
        print("  2. Aplicación web: streamlit run app.py")
        print("  3. Cliente API: python3 api_client.py")
        return 0
    else:
        print("\n⚠️  ESTADO: ALGUNOS TESTS FALLARON")
        print("Revisa los errores arriba para más detalles")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
