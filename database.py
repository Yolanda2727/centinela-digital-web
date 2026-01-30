"""
Persistencia de Datos para Centinela Digital

Proporciona almacenamiento local de casos analizados
para construir históricos institucionales.
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class CentinelaDatabase:
    """Gestiona la base de datos SQLite para Centinela Digital."""
    
    DB_DIR = Path(".centinela_data")
    DB_FILE = DB_DIR / "centinela.db"
    
    def __init__(self):
        """Inicializa la conexión a la base de datos."""
        self.db_file = self.DB_FILE
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Crea la base de datos y tablas si no existen."""
        self.DB_DIR.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        # Tabla de casos analizados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS casos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caso_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                rol TEXT NOT NULL,
                tipo_producto TEXT NOT NULL,
                riesgo_score INTEGER NOT NULL,
                nivel_riesgo TEXT NOT NULL,
                confianza REAL,
                sentimiento TEXT,
                num_evidencias INTEGER,
                texto_length INTEGER,
                json_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de red flags por caso
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS red_flags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caso_id TEXT NOT NULL,
                flag_text TEXT NOT NULL,
                severidad TEXT,
                categoria TEXT,
                FOREIGN KEY (caso_id) REFERENCES casos(caso_id)
            )
        """)
        
        # Tabla de recomendaciones por caso
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recomendaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caso_id TEXT NOT NULL,
                recomendacion TEXT NOT NULL,
                prioridad INTEGER,
                categoria TEXT,
                FOREIGN KEY (caso_id) REFERENCES casos(caso_id)
            )
        """)
        
        # Tabla de KPIs por caso
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kpis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caso_id TEXT NOT NULL,
                kpi_name TEXT NOT NULL,
                kpi_value TEXT,
                tipo_kpi TEXT,
                FOREIGN KEY (caso_id) REFERENCES casos(caso_id)
            )
        """)
        
        # Tabla de estadísticas agregadas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estadisticas_globales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE UNIQUE,
                total_casos INTEGER,
                casos_alto_riesgo INTEGER,
                casos_medio_riesgo INTEGER,
                casos_bajo_riesgo INTEGER,
                promedio_riesgo REAL,
                producto_mas_frecuente TEXT,
                rol_mas_frecuente TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def guardar_caso(self, caso_data: Dict) -> str:
        """
        Guarda un caso análizado en la base de datos.
        
        Args:
            caso_data: diccionario con datos del caso
        
        Returns:
            ID del caso guardado
        """
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        caso_id = caso_data.get("caso_id") or f"caso_{datetime.now().timestamp()}"
        
        try:
            cursor.execute("""
                INSERT INTO casos (
                    caso_id, timestamp, rol, tipo_producto, riesgo_score,
                    nivel_riesgo, confianza, sentimiento, num_evidencias,
                    texto_length, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                caso_id,
                caso_data.get("timestamp", datetime.now().isoformat()),
                caso_data.get("rol"),
                caso_data.get("tipo_producto"),
                caso_data.get("riesgo_score", 0),
                caso_data.get("nivel_riesgo", "DESCONOCIDO"),
                caso_data.get("confianza", 0.0),
                caso_data.get("sentimiento"),
                caso_data.get("num_evidencias", 0),
                caso_data.get("texto_length", 0),
                json.dumps(caso_data, ensure_ascii=False),
            ))
            
            # Guardar red flags si existen
            for flag in caso_data.get("red_flags", []):
                cursor.execute("""
                    INSERT INTO red_flags (caso_id, flag_text, severidad, categoria)
                    VALUES (?, ?, ?, ?)
                """, (
                    caso_id,
                    flag.get("text") if isinstance(flag, dict) else flag,
                    flag.get("severidad") if isinstance(flag, dict) else "media",
                    flag.get("categoria") if isinstance(flag, dict) else "general",
                ))
            
            # Guardar recomendaciones si existen
            for idx, rec in enumerate(caso_data.get("recomendaciones", []), 1):
                cursor.execute("""
                    INSERT INTO recomendaciones (caso_id, recomendacion, prioridad, categoria)
                    VALUES (?, ?, ?, ?)
                """, (
                    caso_id,
                    rec.get("text") if isinstance(rec, dict) else rec,
                    idx,
                    rec.get("categoria") if isinstance(rec, dict) else "accion",
                ))
            
            # Guardar KPIs si existen
            for kpi in caso_data.get("kpis", []):
                cursor.execute("""
                    INSERT INTO kpis (caso_id, kpi_name, kpi_value, tipo_kpi)
                    VALUES (?, ?, ?, ?)
                """, (
                    caso_id,
                    kpi.get("name") if isinstance(kpi, dict) else kpi,
                    kpi.get("value") if isinstance(kpi, dict) else "",
                    kpi.get("tipo") if isinstance(kpi, dict) else "general",
                ))
            
            conn.commit()
            return caso_id
        except sqlite3.IntegrityError:
            # Caso ya existe, actualizar
            cursor.execute("""
                UPDATE casos SET timestamp = ?, riesgo_score = ?, nivel_riesgo = ?,
                                confianza = ?, json_data = ?
                WHERE caso_id = ?
            """, (
                caso_data.get("timestamp", datetime.now().isoformat()),
                caso_data.get("riesgo_score", 0),
                caso_data.get("nivel_riesgo", "DESCONOCIDO"),
                caso_data.get("confianza", 0.0),
                json.dumps(caso_data, ensure_ascii=False),
                caso_id,
            ))
            conn.commit()
            return caso_id
        finally:
            conn.close()
    
    def obtener_caso(self, caso_id: str) -> Optional[Dict]:
        """Obtiene un caso específico de la base de datos."""
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        cursor.execute("SELECT json_data FROM casos WHERE caso_id = ?", (caso_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def listar_casos(
        self,
        filtro_nivel: Optional[str] = None,
        filtro_rol: Optional[str] = None,
        limite: int = 100
    ) -> List[Dict]:
        """
        Lista casos con filtros opcionales.
        
        Args:
            filtro_nivel: filtrar por nivel de riesgo (ALTO, MEDIO, BAJO)
            filtro_rol: filtrar por rol
            limite: número máximo de resultados
        
        Returns:
            lista de casos
        """
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        query = "SELECT json_data FROM casos WHERE 1=1"
        params = []
        
        if filtro_nivel:
            query += " AND nivel_riesgo = ?"
            params.append(filtro_nivel)
        
        if filtro_rol:
            query += " AND rol = ?"
            params.append(filtro_rol)
        
        query += f" ORDER BY created_at DESC LIMIT {limite}"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [json.loads(row[0]) for row in results]
    
    def obtener_estadisticas(self, fecha: Optional[str] = None) -> Dict:
        """Obtiene estadísticas agregadas."""
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        fecha_param = fecha or datetime.now().date().isoformat()
        
        # Estadísticas del día
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN nivel_riesgo = 'ALTO' THEN 1 ELSE 0 END) as alto,
                SUM(CASE WHEN nivel_riesgo = 'MEDIO' THEN 1 ELSE 0 END) as medio,
                SUM(CASE WHEN nivel_riesgo = 'BAJO' THEN 1 ELSE 0 END) as bajo,
                AVG(riesgo_score) as promedio
            FROM casos
            WHERE DATE(created_at) = ?
        """, (fecha_param,))
        
        stats = cursor.fetchone()
        conn.close()
        
        return {
            "total_casos": stats[0] or 0,
            "casos_alto_riesgo": stats[1] or 0,
            "casos_medio_riesgo": stats[2] or 0,
            "casos_bajo_riesgo": stats[3] or 0,
            "promedio_riesgo": round(stats[4], 2) if stats[4] else 0,
            "fecha": fecha_param,
        }
    
    def obtener_resumen_institucion(self) -> Dict:
        """Obtiene resumen general de todos los casos."""
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        # Total de casos
        cursor.execute("SELECT COUNT(*) FROM casos")
        total = cursor.fetchone()[0]
        
        # Distribución por nivel
        cursor.execute("""
            SELECT nivel_riesgo, COUNT(*) FROM casos
            GROUP BY nivel_riesgo
        """)
        dist_nivel = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Distribución por producto
        cursor.execute("""
            SELECT tipo_producto, COUNT(*) FROM casos
            GROUP BY tipo_producto
        """)
        dist_producto = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Promedio de riesgo
        cursor.execute("SELECT AVG(riesgo_score) FROM casos")
        promedio = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_casos": total,
            "distribucion_nivel": dist_nivel,
            "distribucion_producto": dist_producto,
            "promedio_riesgo": round(promedio, 2) if promedio else 0,
            "fecha_reporte": datetime.now().isoformat(),
        }


# Instancia global
db = CentinelaDatabase()


if __name__ == "__main__":
    # Prueba rápida
    print("Inicializando base de datos de Centinela Digital...")
    test_caso = {
        "rol": "Estudiante",
        "tipo_producto": "Ensayo",
        "riesgo_score": 45,
        "nivel_riesgo": "MEDIO",
        "confianza": 0.85,
        "sentimiento": "neutro",
        "num_evidencias": 2,
        "texto_length": 2500,
        "red_flags": ["Estilo inconsistente", "Tiempo sospechoso"],
        "recomendaciones": ["Realizar entrevista", "Verificar referencias"],
        "kpis": ["Tasa de plagio", "Consistencia de estilo"],
    }
    
    caso_id = db.guardar_caso(test_caso)
    print(f"Caso guardado con ID: {caso_id}")
    
    stats = db.obtener_estadisticas()
    print(f"Estadísticas: {stats}")
