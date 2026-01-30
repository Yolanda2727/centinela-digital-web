"""
Sistema de Auditoría y Logging de Actividades
Registra todos los análisis realizados con detalles completos
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sqlite3


class SistemaAuditoria:
    """Sistema completo de auditoría de actividades"""
    
    DB_PATH = Path(".centinela_data/auditoria.db")
    LOGS_DIR = Path(".centinela_data/logs")
    
    def __init__(self):
        """Inicializa sistema de auditoría"""
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self._crear_tablas()
    
    def _crear_tablas(self):
        """Crea tablas de auditoría si no existen"""
        conn = sqlite3.connect(str(self.DB_PATH))
        cursor = conn.cursor()
        
        # Tabla principal de actividades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actividades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                usuario TEXT NOT NULL,
                tipo_actividad TEXT NOT NULL,
                endpoint TEXT,
                metodo_http TEXT,
                ip_origen TEXT,
                estado TEXT,
                detalles TEXT,
                resultado TEXT,
                duracion_ms INTEGER
            )
        """)
        
        # Tabla de análisis realizados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS análisis_realizados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                usuario TEXT NOT NULL,
                tipo_documento TEXT,
                rol_autor TEXT,
                version_modelo TEXT,
                temperatura REAL,
                score_general REAL,
                nivel_riesgo TEXT,
                recomendaciones TEXT,
                documento_hash TEXT UNIQUE,
                duracion_ms INTEGER
            )
        """)
        
        # Tabla de cambios sensibles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cambios_sensibles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                usuario TEXT NOT NULL,
                tipo_cambio TEXT,
                descripcion TEXT,
                antes TEXT,
                despues TEXT,
                razon TEXT
            )
        """)
        
        # Tabla de alertas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                nivel TEXT,
                tipo_alerta TEXT,
                descripcion TEXT,
                usuario_afectado TEXT,
                resuelta INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def registrar_analisis(
        self,
        usuario: str,
        tipo_documento: str,
        rol_autor: str,
        version_modelo: str,
        temperatura: float,
        score_general: float,
        nivel_riesgo: str,
        recomendaciones: List[str],
        documento_hash: str,
        duracion_ms: int = 0
    ) -> int:
        """Registra un análisis realizado"""
        
        conn = sqlite3.connect(str(self.DB_PATH))
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        recomendaciones_str = json.dumps(recomendaciones)
        
        cursor.execute("""
            INSERT INTO análisis_realizados (
                timestamp, usuario, tipo_documento, rol_autor,
                version_modelo, temperatura, score_general, nivel_riesgo,
                recomendaciones, documento_hash, duracion_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, usuario, tipo_documento, rol_autor,
            version_modelo, temperatura, score_general, nivel_riesgo,
            recomendaciones_str, documento_hash, duracion_ms
        ))
        
        conn.commit()
        analisis_id = cursor.lastrowid
        conn.close()
        
        # Registrar en archivo de log también
        self._registrar_en_archivo(
            f"análisis_{usuario}",
            {
                "id": analisis_id,
                "timestamp": timestamp,
                "usuario": usuario,
                "tipo_documento": tipo_documento,
                "rol_autor": rol_autor,
                "version_modelo": version_modelo,
                "temperatura": temperatura,
                "score_general": score_general,
                "nivel_riesgo": nivel_riesgo,
                "recomendaciones": recomendaciones
            }
        )
        
        return analisis_id
    
    def registrar_actividad(
        self,
        usuario: str,
        tipo_actividad: str,
        endpoint: Optional[str] = None,
        metodo_http: Optional[str] = None,
        ip_origen: Optional[str] = None,
        estado: str = "exitosa",
        detalles: Optional[Dict] = None,
        resultado: Optional[str] = None,
        duracion_ms: int = 0
    ) -> int:
        """Registra una actividad en el sistema"""
        
        conn = sqlite3.connect(str(self.DB_PATH))
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        detalles_str = json.dumps(detalles) if detalles else None
        
        cursor.execute("""
            INSERT INTO actividades (
                timestamp, usuario, tipo_actividad, endpoint,
                metodo_http, ip_origen, estado, detalles,
                resultado, duracion_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, usuario, tipo_actividad, endpoint,
            metodo_http, ip_origen, estado, detalles_str,
            resultado, duracion_ms
        ))
        
        conn.commit()
        actividad_id = cursor.lastrowid
        conn.close()
        
        return actividad_id
    
    def registrar_cambio_sensible(
        self,
        usuario: str,
        tipo_cambio: str,
        descripcion: str,
        antes: Optional[str] = None,
        despues: Optional[str] = None,
        razon: Optional[str] = None
    ) -> int:
        """Registra cambios sensibles en el sistema"""
        
        conn = sqlite3.connect(str(self.DB_PATH))
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO cambios_sensibles (
                timestamp, usuario, tipo_cambio, descripcion,
                antes, despues, razon
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, usuario, tipo_cambio, descripcion,
            antes, despues, razon
        ))
        
        conn.commit()
        cambio_id = cursor.lastrowid
        conn.close()
        
        # Crear alerta si es crítico
        if tipo_cambio in ["eliminación_datos", "modificación_resultados", "cambio_configuración"]:
            self.crear_alerta(
                "CRÍTICO",
                tipo_cambio,
                f"Cambio sensible por {usuario}: {descripcion}",
                usuario
            )
        
        return cambio_id
    
    def crear_alerta(
        self,
        nivel: str,
        tipo_alerta: str,
        descripcion: str,
        usuario_afectado: Optional[str] = None
    ) -> int:
        """Crea una alerta en el sistema"""
        
        conn = sqlite3.connect(str(self.DB_PATH))
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO alertas (
                timestamp, nivel, tipo_alerta, descripcion, usuario_afectado
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            timestamp, nivel, tipo_alerta, descripcion, usuario_afectado
        ))
        
        conn.commit()
        alerta_id = cursor.lastrowid
        conn.close()
        
        return alerta_id
    
    def obtener_log_actividad(
        self,
        usuario: Optional[str] = None,
        tipo_actividad: Optional[str] = None,
        dias: int = 30,
        limite: int = 100
    ) -> List[Dict]:
        """Obtiene historial de actividades"""
        
        conn = sqlite3.connect(str(self.DB_PATH))
        cursor = conn.cursor()
        
        query = "SELECT * FROM actividades WHERE 1=1"
        params = []
        
        # Filtro de fecha
        query += f" AND timestamp > datetime('now', '-{dias} days')"
        
        if usuario:
            query += " AND usuario = ?"
            params.append(usuario)
        
        if tipo_actividad:
            query += " AND tipo_actividad = ?"
            params.append(tipo_actividad)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limite)
        
        cursor.execute(query, params)
        columnas = [descripcion[0] for descripcion in cursor.description]
        resultados = cursor.fetchall()
        
        conn.close()
        
        return [dict(zip(columnas, fila)) for fila in resultados]
    
    def obtener_análisis_usuario(
        self,
        usuario: str,
        dias: int = 30,
        limite: int = 50
    ) -> List[Dict]:
        """Obtiene análisis realizados por un usuario"""
        
        conn = sqlite3.connect(str(self.DB_PATH))
        cursor = conn.cursor()
        
        query = f"""
            SELECT * FROM análisis_realizados
            WHERE usuario = ?
            AND timestamp > datetime('now', '-{dias} days')
            ORDER BY timestamp DESC
            LIMIT ?
        """
        
        cursor.execute(query, (usuario, limite))
        columnas = [descripcion[0] for descripcion in cursor.description]
        resultados = cursor.fetchall()
        
        conn.close()
        
        datos = []
        for fila in resultados:
            fila_dict = dict(zip(columnas, fila))
            # Parsear JSON de recomendaciones
            fila_dict["recomendaciones"] = json.loads(fila_dict.get("recomendaciones", "[]"))
            datos.append(fila_dict)
        
        return datos
    
    def obtener_alertas(
        self,
        resuelta: bool = False,
        nivel: Optional[str] = None,
        limite: int = 50
    ) -> List[Dict]:
        """Obtiene alertas del sistema"""
        
        conn = sqlite3.connect(str(self.DB_PATH))
        cursor = conn.cursor()
        
        query = "SELECT * FROM alertas WHERE resuelta = ?"
        params = [1 if resuelta else 0]
        
        if nivel:
            query += " AND nivel = ?"
            params.append(nivel)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limite)
        
        cursor.execute(query, params)
        columnas = [descripcion[0] for descripcion in cursor.description]
        resultados = cursor.fetchall()
        
        conn.close()
        
        return [dict(zip(columnas, fila)) for fila in resultados]
    
    def obtener_cambios_sensibles(
        self,
        usuario: Optional[str] = None,
        tipo_cambio: Optional[str] = None,
        dias: int = 30,
        limite: int = 50
    ) -> List[Dict]:
        """Obtiene historial de cambios sensibles"""
        
        conn = sqlite3.connect(str(self.DB_PATH))
        cursor = conn.cursor()
        
        query = f"""
            SELECT * FROM cambios_sensibles
            WHERE timestamp > datetime('now', '-{dias} days')
        """
        params = []
        
        if usuario:
            query += " AND usuario = ?"
            params.append(usuario)
        
        if tipo_cambio:
            query += " AND tipo_cambio = ?"
            params.append(tipo_cambio)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limite)
        
        cursor.execute(query, params)
        columnas = [descripcion[0] for descripcion in cursor.description]
        resultados = cursor.fetchall()
        
        conn.close()
        
        return [dict(zip(columnas, fila)) for fila in resultados]
    
    def generar_reporte_auditoria(
        self,
        usuario: str,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None
    ) -> Dict:
        """Genera reporte de auditoría completo"""
        
        conn = sqlite3.connect(str(self.DB_PATH))
        cursor = conn.cursor()
        
        # Actividades
        query_actividades = "SELECT COUNT(*) FROM actividades WHERE usuario = ?"
        cursor.execute(query_actividades, (usuario,))
        total_actividades = cursor.fetchone()[0]
        
        # Análisis
        query_análisis = "SELECT COUNT(*) FROM análisis_realizados WHERE usuario = ?"
        cursor.execute(query_análisis, (usuario,))
        total_análisis = cursor.fetchone()[0]
        
        # Cambios sensibles
        query_cambios = "SELECT COUNT(*) FROM cambios_sensibles WHERE usuario = ?"
        cursor.execute(query_cambios, (usuario,))
        total_cambios = cursor.fetchone()[0]
        
        # Score promedio
        query_score = """
            SELECT AVG(score_general), 
                   COUNT(CASE WHEN nivel_riesgo='CRÍTICO' THEN 1 END),
                   COUNT(CASE WHEN nivel_riesgo='ALTO' THEN 1 END),
                   COUNT(CASE WHEN nivel_riesgo='MEDIO' THEN 1 END),
                   COUNT(CASE WHEN nivel_riesgo='BAJO' THEN 1 END)
            FROM análisis_realizados WHERE usuario = ?
        """
        cursor.execute(query_score, (usuario,))
        score_data = cursor.fetchone()
        
        conn.close()
        
        reporte = {
            "usuario": usuario,
            "fecha_generación": datetime.now().isoformat(),
            "resumen": {
                "total_actividades": total_actividades,
                "total_análisis": total_análisis,
                "cambios_sensibles": total_cambios
            },
            "análisis": {
                "score_promedio": score_data[0] or 0,
                "documentos_críticos": score_data[1] or 0,
                "documentos_alto_riesgo": score_data[2] or 0,
                "documentos_medio_riesgo": score_data[3] or 0,
                "documentos_bajo_riesgo": score_data[4] or 0
            },
            "actividades_recientes": self.obtener_log_actividad(usuario, limite=10),
            "análisis_recientes": self.obtener_análisis_usuario(usuario, limite=10),
            "cambios_recientes": self.obtener_cambios_sensibles(usuario, limite=10)
        }
        
        return reporte
    
    def _registrar_en_archivo(self, nombre_log: str, datos: Dict):
        """Registra en archivo JSON para backup"""
        
        log_file = self.LOGS_DIR / f"{nombre_log}.jsonl"
        
        with open(log_file, "a") as f:
            f.write(json.dumps(datos, ensure_ascii=False) + "\n")


# Instancia global de auditoría
auditoria = SistemaAuditoria()
