#!/usr/bin/env python3
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import sys
import argparse
from sentinel_core.ebpf.monitor import GuardianMonitor

def start_monitor():
    """Inicia el monitor de protección en tiempo real (Cognitive Loop)."""
    print("🛡️  [Sentinel ClLI] Iniciando Guardian Alpha Monitor...")
    monitor = GuardianMonitor()
    monitor.start()

def main():
    """Punto de entrada principal de la aplicación CLI."""
    parser = argparse.ArgumentParser(description="Sentinel Cortex - Cognitive Operating System Security")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: start
    start_parser = subparsers.add_parser("start", help="Inicia el monitor de protección")

    # Comando: status (Placeholder)
    status_parser = subparsers.add_parser("status", help="Muestra el estado del sistema")

    args = parser.parse_args()

    if args.command == "start":
        start_monitor()
    elif args.command == "status":
        print("ℹ️  [Status] Sistema Sentinel: ONLINE")
        print("ℹ️  [Status] Guardian Beta (eBPF): Cargado (Asumido)")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
