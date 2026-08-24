#!/usr/bin/env python3
# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# -------------------------------------------------------------------------------------

"""
🐚 SEMANTIC SHELL v2.0
======================
Interfaz de lenguaje natural para el Sistema Sentinel.
Reconstruida bajo Protocolo Yatra.

Permite al operador hablar con el sistema y que este ejecute acciones
o enseñe conceptos (Modo Maestro).
"""

import sys
import os
import subprocess
import asyncio
import time

# Ensure imports work
sys.path.append(os.path.join(os.getcwd(), "quantum"))
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    from semantic_router import SemanticRouter
except ImportError:
    # Fallback if running from root
    sys.path.append(os.getcwd())
    from quantum.semantic_router import SemanticRouter

class SemanticShell:
    def __init__(self):
        print("🔌 Iniciando enlace neuronal (Cargando Router)...")
        self.router = SemanticRouter()
        self.running = True
        
    def clear(self):
        subprocess.run(['clear'], check=False)
        
    def print_banner(self):
        print("\033[1;35m" + "="*60)
        print("  🧠  SENTINEL SEMANTIC SHELL v2.0  🧠")
        print("  [MODO MAESTRO / LENGUAJE NATURAL ACTIVADO]")
        print("="*60 + "\033[0m")
        print("Escribe 'exit' o 'q' para volver al CLI Modular.")
        print("-" * 60)

    async def process_command(self, user_input):
        print(f"\033[1;30mThinking...\033[0m", end="\r")
        
        # 1. Routing
        category, reason = await self.router.classify_intent(user_input)
        
        print(f"🤖 ENTENDIDO: \033[1;36m{category}\033[0m")
        # print(f"   Razón: {reason}")
        
        # 2. Execution Dispatch
        if category == "QUERY_ORACLE":
            print("\n🔮 Invocando al Oráculo (Modo Maestro)...")
            time.sleep(0.5)
            # Pass arguments as a list to subprocess.run to prevent command injection
            subprocess.run([sys.executable, "quantum/quantum_oracle_cli.py", user_input], check=False)
            
        elif category == "SYSTEM_ACTION":
            print("\n⚙️ Ejecutando Acción de Sistema...")
            self.execute_system_action(user_input, reason)
            
        elif category == "SAFETY_CHECK":
            print("\n🛡️ Verificación de Seguridad...")
            # For now, we lean on the explanation provided by Gemini in 'reason'
            # In future v2.1, we can call yatra_guard directly
            print(f"   DICTAMEN DEL GUARDIÁN: {reason}")
            
        elif category == "UNKNOWN":
            print("\n❓ No estoy seguro de cómo proceder con eso en este plano de realidad.")
            print(f"   Contexto AI: {reason}")
            
        else:
            print("⚠️ Error de categorización.")
            
    def execute_system_action(self, user_input, reason):
        # Heuristic mapping for v2.0 (To be enhanced with dedicated tool calling)
        u = user_input.lower()
        if "dashboard" in u or "monitor" in u:
            subprocess.run([sys.executable, "quantum/sentinel_dashboard.py"], check=False)
        elif "scan" in u or "resonan" in u:
            subprocess.run([sys.executable, "quantum/quantum_scanner.py", "quantum/RESONANT_ARCH_SPECS.md"], check=False)
        elif "lattice" in u or "red" in u:
            subprocess.run([sys.executable, "quantum/quantum_lattice.py"], check=False)
        elif "audit" in u or "truth" in u:
            subprocess.run([sys.executable, "quantum/TRUTHSYNC_FULL_SYSTEM_AUDIT.py"], check=False)
        else:
            print("⚠️ Acción reconocida pero sin enlace directo en el Shell v2.0.")
            print("   Por favor usa el menú numérico del CLI para esta función específica.")

    async def repl_loop(self):
        self.clear()
        self.print_banner()
        
        while self.running:
            try:
                user_input = input("\n\033[1;32mOperador > \033[0m").strip()
                
                if not user_input: continue
                if user_input.lower() in ['exit', 'q', 'quit', 'salir']:
                    self.running = False
                    print("\n🔌 Desconectando enlace neural...")
                    break
                    
                await self.process_command(user_input)
                
            except KeyboardInterrupt:
                self.running = False
                print("\n\n🔌 Interrupción detectada.")
                break
            except Exception as e:
                print(f"\n❌ Error Crítico en Shell: {e}")

def run_shell():
    shell = SemanticShell()
    asyncio.run(shell.repl_loop())

if __name__ == "__main__":
    run_shell()
