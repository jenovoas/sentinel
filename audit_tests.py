#!/usr/bin/env python3
"""
🔍 AUDITOR MASIVO DE TESTS
==========================
Analiza todos los archivos de test para identificar:
- Tests vacíos o sin assertions
- Tests con assert True (falseados)
- Tests con TODO/FAKE/MOCK sin implementar
- Archivos de test obsoletos
"""

import os
import re
import ast

def analyze_test_file(filepath):
    """Analiza un archivo de test y retorna problemas encontrados."""
    problems = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Detectar assert True
        if re.search(r'assert\s+True\b', content):
            problems.append("❌ Contiene 'assert True' (test falseado)")
        
        # 2. Detectar TODO/FAKE/MOCK sin implementar
        if re.search(r'pass\s*#\s*(TODO|FAKE|MOCK)', content, re.IGNORECASE):
            problems.append("⚠️  Contiene TODO/FAKE/MOCK sin implementar")
        
        # 3. Detectar si tiene funciones de test
        has_test_functions = bool(re.search(r'def\s+test_\w+', content))
        
        if not has_test_functions:
            problems.append("⚠️  No tiene funciones de test (def test_*)")
        
        # 4. Contar assertions
        assertion_count = len(re.findall(r'\bassert\b', content))
        
        if has_test_functions and assertion_count == 0:
            problems.append("❌ Tiene funciones test_ pero sin assertions")
        
        # 5. Detectar archivos muy pequeños (< 50 líneas)
        line_count = len(content.split('\n'))
        if line_count < 50 and has_test_functions:
            problems.append(f"⚠️  Archivo pequeño ({line_count} líneas) - posible stub")
        
        return problems
    
    except Exception as e:
        return [f"❌ Error leyendo archivo: {e}"]

def main():
    """Escanea todos los archivos de test."""
    print("\n🔍 AUDITOR MASIVO DE TESTS")
    print("=" * 60)
    
    # Buscar todos los archivos de test
    test_files = []
    for root, dirs, files in os.walk('.'):
        # Ignorar directorios
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', '.backup']]
        
        for file in files:
            if 'test' in file.lower() and file.endswith('.py'):
                filepath = os.path.join(root, file)
                test_files.append(filepath)
    
    print(f"\n📋 Encontrados {len(test_files)} archivos de test\n")
    
    # Analizar cada archivo
    problematic_files = {}
    clean_files = []
    
    for filepath in sorted(test_files):
        problems = analyze_test_file(filepath)
        
        if problems:
            problematic_files[filepath] = problems
        else:
            clean_files.append(filepath)
    
    # Reporte
    print("\n" + "=" * 60)
    print("📊 RESULTADOS")
    print("=" * 60)
    
    if problematic_files:
        print(f"\n❌ ARCHIVOS PROBLEMÁTICOS ({len(problematic_files)}):\n")
        for filepath, problems in problematic_files.items():
            print(f"\n{filepath}:")
            for problem in problems:
                print(f"  {problem}")
    
    if clean_files:
        print(f"\n✅ ARCHIVOS LIMPIOS ({len(clean_files)}):\n")
        for filepath in clean_files[:10]:  # Mostrar solo primeros 10
            print(f"  {filepath}")
        if len(clean_files) > 10:
            print(f"  ... y {len(clean_files) - 10} más")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📈 RESUMEN:")
    print(f"   Total: {len(test_files)} archivos")
    print(f"   ✅ Limpios: {len(clean_files)}")
    print(f"   ❌ Problemáticos: {len(problematic_files)}")
    print("=" * 60)
    
    # Recomendaciones
    if problematic_files:
        print("\n💡 RECOMENDACIONES:")
        print("   1. Revisar archivos problemáticos manualmente")
        print("   2. Eliminar tests vacíos o falseados")
        print("   3. Implementar TODOs o eliminar stubs")
        print("   4. Consolidar tests pequeños")

if __name__ == "__main__":
    main()
