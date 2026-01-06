#!/usr/bin/env python3

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

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import os
import sys
import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple

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
        with open(file_path, 'r', encoding='utf-8') as f:
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
        with open(file_path, 'r', encoding='utf-8') as f:
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
        with open(file_path, 'r', encoding='utf-8') as f:
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
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)
            
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                # Buscar assert True sin condición
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Assert):
                        if isinstance(stmt.test, ast.Constant) and stmt.test.value is True:
                            issues.append((node.lineno, f"Test '{node.name}' tiene 'assert True' (no prueba nada)"))
    except Exception:
        pass
    
    return issues

def audit_file(file_path: str) -> Dict:
    """Audita un archivo Python completo"""
    results = {
        "fake_returns": check_fake_returns(file_path),
        "fake_comments": check_fake_comments(file_path),
        "silent_imports": check_silent_import_failures(file_path),
        "fake_tests": check_fake_tests(file_path)
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