#!/usr/bin/env python3
import os
import subprocess
import json
import requests
import time
from pathlib import Path

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"
TRUTHSYNC_BIN = "/home/jnovoas/sentinel/truthsync-poc/target/release/truthsync_core"
SENTINEL_ROOT = "/home/jnovoas/sentinel"

def scan_files():
    """Escanea código/docs para certificación"""
    print("📂 Escaneando archivos del proyecto...")
    files = {
        'code': [],
        'docs': [],
        'logs': []
    }
    # Exclude directories
    exclude = {'.git', '.venv', 'node_modules', 'target', '.pytest_cache'}
    
    for root, dirs, fs in os.walk(SENTINEL_ROOT):
        # Filter directories in place
        dirs[:] = [d for d in dirs if d not in exclude]
        
        for f in fs:
            path = Path(root) / f
            # Skip binary files and large logs
            if path.suffix in ('.py', '.c', '.rs', '.h'):
                files['code'].append(str(path))
            elif path.suffix == '.md':
                files['docs'].append(str(path))
            elif path.suffix == '.log' and path.stat().st_size > 0:
                files['logs'].append(str(path))
    return files

def truthsync_certify(claims):
    """Envía a TruthSync CLI para scoring"""
    if not claims:
        return {"status": "NO_CLAIMS", "score": 0.0}
    try:
        proc = subprocess.run([
            TRUTHSYNC_BIN,
            "--mode", "certify",
            "--claims", json.dumps(claims)
        ], capture_output=True, text=True, timeout=30)
        return json.loads(proc.stdout)
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "score": 0.0}

def query_ollama(prompt):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_ctx": 4096}
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        return response.json().get('response', 'ERROR')
    except:
        return "AI_OFFLINE"

def generate_report():
    print(f"🔍 Iniciando Pipeline de Auto-Certificación (TruthSync CLI + {MODEL})...")
    files = scan_files()
    
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'summary': {
            'total_code': len(files['code']),
            'total_docs': len(files['docs']),
            'total_logs': len(files['logs'])
        },
        'certifications': []
    }

    # Seleccionamos archivos críticos para no saturar el reporte inicial
    critical_files = [
        "guardian-alpha/quantum_ai_integration.c",
        "guardian-alpha/sentinel_relay.c",
        "truthsync-poc/src/main.rs",
        "REQUIREMENTS_TRACEABILITY_MATRIX.md",
        "SYSTEM_AUDIT_SUMMARY_2026_01_01.md"
    ]

    for f_path in critical_files:
        full_path = os.path.join(SENTINEL_ROOT, f_path)
        if not os.path.exists(full_path):
            continue
            
        print(f"📝 Certificando {f_path}...")
        with open(full_path, 'r') as f:
            content = f.read()

        # Phase 1: AI Analysis
        ai_prompt = f"[AUDITOR_PIPELINE] Analiza {f_path}. Extrae 'truth claims' técnicos y genera una certificación breve.\nContent:\n{content[:2000]}"
        ai_response = query_ollama(ai_prompt)
        
        # Phase 2: TruthSync Scoring (Simplified for POSIX output)
        # We extract lines that look like claims
        claims = [line for line in ai_response.split('\n') if len(line) > 20 and '-' in line[:5]]
        ts_score = truthsync_certify(claims)

        report['certifications'].append({
            'file': f_path,
            'ai_certification': ai_response,
            'truthsync_status': ts_score.get('status'),
            'truthsync_score': ts_score.get('score'),
            'claims_verified': ts_score.get('claims_count', 0)
        })

    # Save Markdown Report
    md_report = f"# 📜 SENTINEL SELF-CERTIFICATION PIPELINE REPORT\n"
    md_report += f"**Timestamp:** {report['timestamp']}\n\n"
    md_report += f"## 📊 System Overview\n"
    md_report += f"- Code Artifacts: {report['summary']['total_code']}\n"
    md_report += f"- Documentation: {report['summary']['total_docs']}\n"
    md_report += f"- Active Logs: {report['summary']['total_logs']}\n\n"
    
    for cert in report['certifications']:
        md_report += f"### 📄 {cert['file']}\n"
        md_report += f"**TruthSync Score:** {cert['truthsync_score']} ({cert['truthsync_status']})\n"
        md_report += f"**AI Audit:**\n{cert['ai_certification']}\n\n---\n\n"

    with open(os.path.join(SENTINEL_ROOT, "SENTINEL_CERTIFICATION_PIPELINE.md"), "w") as f:
        f.write(md_report)
    
    print(f"\n✅ Pipeline completo. Informe generado en SENTINEL_CERTIFICATION_PIPELINE.md")

if __name__ == "__main__":
    generate_report()
