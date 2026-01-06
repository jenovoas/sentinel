#!/usr/bin/env python3
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import json
import sys
import shutil
from pathlib import Path

# Fix PYTHONPATH
root = Path(__file__).parent.parent
sys.path.append(str(root))
from sem_shell import SemSH

# Estilos de consola
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

class SemSHBenchmarkV2:
    def __init__(self):
        self.root = root
        self.corpus_path = self.root / "tests" / "semantic_corpus.json"
        self.state_file = Path("/etc/sentinel/state.json")
        self.profiles_dir = self.root / "config" / "profiles"
        self.shell = SemSH()
        
    def set_profile(self, profile_name):
        src = self.profiles_dir / f"{profile_name}.json"
        shutil.copy(src, self.state_file)
        print(f"\n{BOLD}🔄 Perfil Activo: {profile_name.upper()} (Umbral: {self.shell.load_profile()['risk_threshold']}){RESET}")

    def run_tests(self, profile_name):
        self.set_profile(profile_name)
        with open(self.corpus_path) as f:
            corpus = json.load(f)
            
        passed = 0
        total = len(corpus)
        
        print(f"{BOLD}{'ID':<6} | {'INPUT':<40} | {'RISK':<6} | {'RESULT':<10}{RESET}")
        print("-" * 75)
        
        for case in corpus:
            # 1. Obtener intención e IA Risk Score
            # Pass original input to SemSH (either NL or raw command)
            intent_data = self.shell.contextual_intent(case['input'])
            
            risk = intent_data.get('risk_score', S60(1, 0, 0))
            reasoning = intent_data.get('reasoning', '')
            
            # 2. Determinar Acción Realizada según Umbral de Perfil
            threshold = self.shell.load_profile()['risk_threshold']
            action = "ALLOW" if risk <= threshold else "BLOCK"
            
            # 3. Validar contra expectativa del corpus
            expected_action = case['expected_action'][profile_name]
            is_action_ok = action == expected_action
            
            # Validar si el riesgo cae en el rango esperado (Opcional, pero útil para calibración)
            risk_in_range = case['expected_risk_range'][0] <= risk <= case['expected_risk_range'][1]
            
            status = f"{GREEN}PASS{RESET}" if is_action_ok else f"{RED}FAIL{RESET}"
            if is_action_ok: passed += 1
            
            input_preview = (case['input'][:37] + '..') if len(case['input']) > 37 else case['input']
            print(f"{case['id']:<6} | {input_preview:<40} | {risk:.2f} | {status}")
            if not is_action_ok:
                print(f"   {YELLOW}↳ Reasoning: {reasoning}{RESET}")
                print(f"   {YELLOW}↳ Expected {expected_action}, got {action}{RESET}")
            
        print("-" * 75)
        success_rate = (passed / total) * 100
        color = GREEN if success_rate >= 90 else (YELLOW if success_rate >= 70 else RED)
        print(f"Resultado {profile_name.upper()}: {color}{success_rate:.1f}% ({passed}/{total}){RESET}")
        return passed, total

if __name__ == "__main__":
    bench = SemSHBenchmarkV2()
    overall_passed = 0
    overall_total = 0
    
    # We only test PROD and LOCKDOWN as LAB allows everything by design (uninteresting for AI logic test)
    for p in ['prod', 'lockdown']:
        p_passed, p_total = bench.run_tests(p)
        overall_passed += p_passed
        overall_total += p_total
        
    print(f"\n{BOLD}📊 RESUMEN GLOBAL AI CALIBRATION: {(overall_passed/overall_total)*100:.1f}% PASSED{RESET}\n")
