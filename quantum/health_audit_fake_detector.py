#!/usr/bin/env python3
# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.

# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
🔍 SENTINEL HEALTH AUDIT - DETECTOR DE CÓDIGO FAKE
===================================================
Verifica la salud del sistema y detecta código simulado o fake.

Criterios de detección:
1. Funciones que siempre retornan True/éxito sin lógica real
2. Simulaciones que no conectan con servicios reales
3. Tests que no prueban nada (assert True)
4. Código con comentarios "TODO", "FAKE", "MOCK", "SIMULATE"
5. Imports que fallan pero son ignorados silenciosamente
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# Colores para output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_issue(severity: str, file: str, line: int, message: str):
    color = Colors.RED if severity == "CRITICAL" else Colors.YELLOW if severity == "WARNING" else Colors.BLUE
    icon = "🚨" if severity == "CRITICAL" else "⚠️" if severity == "WARNING" else "ℹ️"
    print(f"{icon} {color}[{severity}]{Colors.RESET} {file}:{line}")
    print(f"   {message}\n")

def check_fake_returns(file_path: str) -> List[Tuple[int, str]]:
    """Detecta funciones que siempre retornan True o valores fake"""
    issues = []
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Buscar funciones que solo retornan True/False sin lógica
                if len(node.body) == 1 and isinstance(node.body[0], ast.Return):
                    return_value = node.body[0].value
                    if isinstance(return_value, ast.Constant):
                        if return_value.value is True:
                            issues.append((node.lineno, f"Función '{node.name}' siempre retorna True sin lógica"))
                        elif isinstance(return_value.value, dict) and return_value.value.get("verified") is True:
                            issues.append((node.lineno, f"Función '{node.name}' retorna dict fake con verified=True"))
    except SyntaxError:
        pass
    except Exception as e:
        pass

    return issues

def check_fake_comments(file_path: str) -> List[Tuple[int, str]]:
    """Detecta comentarios que indican código fake o simulado"""
    issues = []
    fake_keywords = [
        r'\bFAKE\b', r'\bMOCK\b', r'\bSIMULATE\b', r'\bSIMULATED\b',
        r'\bTODO.*implement\b', r'\bFIXME\b', r'\bHACK\b',
        r'simular.*result', r'inventar.*dato', r'fake.*data'
    ]

    try:
        with open(file_path, encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                line_lower = line.lower()
                for keyword in fake_keywords:
                    if re.search(keyword, line, re.IGNORECASE):
                        issues.append((i, f"Comentario sospechoso: {line.strip()[:80]}"))
                        break
    except Exception:
        pass

    return issues

def check_silent_import_failures(file_path: str) -> List[Tuple[int, str]]:
    """Detecta imports que fallan pero son ignorados con try/except"""
    issues = []
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # Verificar si el try contiene imports
                has_import = any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in node.body)
                # Verificar si el except hace pass o asigna None
                if has_import and node.handlers:
                    for handler in node.handlers:
                        if len(handler.body) == 1:
                            if isinstance(handler.body[0], ast.Pass):
                                issues.append((node.lineno, "Import fallido ignorado silenciosamente con 'pass'"))
                            elif isinstance(handler.body[0], ast.Assign):
                                # Verificar si asigna None
                                if isinstance(handler.body[0].value, ast.Constant) and handler.body[0].value.value is None:
                                    issues.append((node.lineno, "Import fallido asigna None (posible código fake)"))
    except Exception:
        pass

    return issues

def check_fake_tests(file_path: str) -> List[Tuple[int, str]]:
    """Detecta tests que no prueban nada real"""
    issues = []
    if 'test' not in file_path.lower():
        return issues

    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                # Buscar assert True sin condición
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Assert):
                        if isinstance(stmt.test, ast.Constant) and stmt.test.value is True:
                            issues.append((node.lineno, f"Test '{node.name}' tiene 'assert True' (no prueba nada)"))
    except Exception as e:
        print(f"   ⚠️  Error parseando tests en {file_path}: {e}")

    return issues

def check_float_contamination(file_path: str) -> List[Tuple[int, str]]:
    """Detecta código no medible/comprobable: float, numpy/random en cálculo core.

    Regla del proyecto (Jaime, 2026-08-05): TODO lo que no sea medible y
    comprobable debe ser etiquetado para revisión y refactorización. En S60
    puro esto significa: presencia de float(), np.random, numpy para cálculo,
    normalizaciones arbitrarias (ej. / 500.0), .to_float() en core.
    """
    issues = []
    # Marcador estándar de etiqueta de revisión (ver coherence_mapping_calibration.py)
    ALREADY_TAGGED = "ETIQUETA DE REVISIÓN"
    already_tagged = False
    # Patrones de contaminación no-medible (core, no I/O de borde)
    patterns = [
        (r'\bfloat\s*\(', "Conversión explícita a float() — contaminación decimal en core"),
        (r'np\.random\.', "np.random — ruido no determinista (no medible/repetible)"),
        (r'\brandom\.(uniform|normal|randint|random)\s*\(', "random.* — fuente no determinista"),
        (r'numpy|import numpy', "import numpy — riesgo de cálculo core en float"),
        (r'\.to_float\s*\(', ".to_float() en core — salida de aritmética S60 a decimal"),
        (r'/\s*\d+\.\d+', "División por literal decimal (ej. /500.0) — normalización arbitraria no medible"),
        (r'np\.fft\.', "np.fft — PSD numérica; requiere justificación física medible"),
        (r'uniform\(0\.\d+', "uniform(0.x) — banda aleatoria hardcodeada"),
    ]
    try:
        with open(file_path, encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if not already_tagged and ALREADY_TAGGED in line:
                    already_tagged = True
                for pat, msg in patterns:
                    if re.search(pat, line):
                        suffix = " [YA ETIQUETADO]" if already_tagged else ""
                        issues.append((i, msg + suffix))
                        break
    except Exception as e:
        print(f"   ⚠️  Error leyendo {file_path}: {e}")

    return issues

def audit_file(file_path: str) -> Dict:
    """Audita un archivo Python completo"""
    results = {
        "fake_returns": check_fake_returns(file_path),
        "fake_comments": check_fake_comments(file_path),
        "silent_imports": check_silent_import_failures(file_path),
        "fake_tests": check_fake_tests(file_path),
        "float_contamination": check_float_contamination(file_path)
    }
    return results

def scan_directory(base_dir: str, exclude_dirs: List[str]) -> Dict[str, Dict]:
    """Escanea todo el directorio buscando código fake"""
    results = {}
    base_path = Path(base_dir)

    for py_file in base_path.rglob("*.py"):
        # Excluir directorios
        if any(excluded in str(py_file) for excluded in exclude_dirs):
            continue
        # No auditar al propio detector (contiene los patrones de búsqueda)
        if py_file.name == "health_audit_fake_detector.py":
            continue

        file_results = audit_file(str(py_file))

        # Solo guardar si hay issues
        if any(file_results.values()):
            results[str(py_file)] = file_results

    return results

def main():
    print_header("🔍 SENTINEL HEALTH AUDIT - DETECTOR DE CÓDIGO FAKE")

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Directorios a excluir
    exclude_dirs = [
        'node_modules', 'venv', '__pycache__', '.git',
        'target', 'build', 'dist', '.venv', 'venv_test'
    ]

    print(f"📂 Escaneando: {base_dir}")
    print(f"🚫 Excluyendo: {', '.join(exclude_dirs)}\n")

    results = scan_directory(base_dir, exclude_dirs)

    if not results:
        print(f"{Colors.GREEN}✅ No se detectó código fake o simulado.{Colors.RESET}")
        print(f"{Colors.GREEN}✅ El sistema parece estar limpio.{Colors.RESET}\n")
        return 0

    # Reportar issues
    total_issues = 0
    critical_files = []

    for file_path, issues in sorted(results.items()):
        rel_path = os.path.relpath(file_path, base_dir)
        has_critical = False

        for issue_type, issue_list in issues.items():
            for line, message in issue_list:
                severity = "CRITICAL" if issue_type in ["fake_returns", "fake_tests"] else "WARNING"
                if severity == "WARNING" and issue_type == "float_contamination":
                    # Etiquetado explícito: no-medible → revisión/refactorización
                    message = f"[NO-MEDIBLE] {message} — ETIQUETAR PARA REVISIÓN Y REFACTORIZACIÓN"
                if severity == "CRITICAL":
                    has_critical = True
                print_issue(severity, rel_path, line, message)
                total_issues += 1

        if has_critical:
            critical_files.append(rel_path)

    # Resumen
    print_header("📊 RESUMEN DE AUDITORÍA")
    print(f"Total de issues detectados: {Colors.BOLD}{total_issues}{Colors.RESET}")
    print(f"Archivos con issues críticos: {Colors.BOLD}{len(critical_files)}{Colors.RESET}\n")

    if critical_files:
        print(f"{Colors.RED}🚨 ARCHIVOS CRÍTICOS QUE REQUIEREN REVISIÓN:{Colors.RESET}")
        for f in critical_files:
            print(f"   - {f}")
        print()

    print(f"{Colors.YELLOW}⚠️  Revisa estos archivos manualmente para confirmar si son fake.{Colors.RESET}")
    print(f"{Colors.YELLOW}⚠️  No todos los issues son necesariamente código fake.{Colors.RESET}\n")

    return 1 if critical_files else 0

if __name__ == "__main__":
    sys.exit(main())
