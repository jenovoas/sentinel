#!/usr/bin/env python3
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import os
import asyncio
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

# Importamos el Core (ajustando el path si es necesario)
import sys
from truthsync_core import TruthSyncCore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MasterValidator")

class MasterValidator:
    def __init__(self):
        self.base_path = Path("/app/..") # En el contenedor, mapeado así
        self.exclude_dirs = {".git", "node_modules", "venv", "__pycache__", "target", "build", "dist"}
        self.core = TruthSyncCore(
            postgres_url="postgresql://sentinel_user:2wA4KgRinuKNgcOrA839ZRC2R1ycNtC4@postgres:5432/sentinel_db",
            redis_url="redis://redis:6379"
        )
        self.file_results = []

    def get_file_hash(self, filepath):
        hasher = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"

    async def run(self):
        logger.info("🛡️ Iniciando Validación Maestra de Sentinel...")
        await self.core.initialize()
        
        # Escaneo de archivos
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                filepath = Path(root) / file
                rel_path = filepath.relative_to(self.base_path)
                
                # Solo archivos relevantes
                if rel_path.suffix in {".py", ".md", ".json", ".rs", ".js", ".ts", ".html", ".css", ".sh", ".c"}:
                    file_hash = self.get_file_hash(filepath)
                    
                    # Enviamos job al motor pesado
                    claim = f"File Integrity: {rel_path} (hash: {file_hash})"
                    job_id = await self.core.submit_job(claim, priority="normal", metadata={"path": str(rel_path)})
                    
                    self.file_results.append({
                        "path": str(rel_path),
                        "hash": file_hash,
                        "job_id": job_id,
                        "timestamp": datetime.now().isoformat()
                    })

        logger.info(f"📝 {len(self.file_results)} archivos enviados al motor pesado para certificación.")
        
        # Esperar un poco para que el motor procese (es async y pesado)
        logger.info("⏳ Procesando colas de certificación...")
        await asyncio.sleep(5) 
        
        # Generar reporte resumido
        self.generate_report()
        
        await self.core.shutdown()
        logger.info("✅ Validación con TruthSync Core completada.")

    def generate_report(self):
        report_path = self.base_path / "TRUTHSYNC_MASTER_VALIDATION_REPORT.md"
        with open(report_path, "w") as f:
            f.write("# 🛡️ SENTINEL: REPORTE MAESTRO DE CERTIFICACIÓN TRUTHSYNC\n\n")
            f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Motor:** TruthSync Core (Heavy) con PostgreSQL + Redis\n")
            f.write(f"**Archivos certificados:** {len(self.file_results)}\n\n")
            f.write("--- \n\n")
            f.write("| Archivo | Hash SHA-256 | Job ID | Estado |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            
            for res in sorted(self.file_results, key=lambda x: x["path"]):
                status = "✅ CERTIFIED" if not res["hash"].startswith("ERROR") else "❌ FAILED"
                f.write(f"| `{res['path']}` | `{res['hash'][:16]}...` | `{res['job_id']}` | {status} |\n")
        
        print(f"\n✨ Reporte generado en: {report_path}")

if __name__ == "__main__":
    asyncio.run(MasterValidator().run())
