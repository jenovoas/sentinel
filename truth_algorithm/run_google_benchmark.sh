#!/bin/bash
# Script para ejecutar benchmark de Google Search con credenciales seguras
# ========================================================================
#
# Uso:
#   1. Edita este archivo y pon tus credenciales
#   2. chmod +x run_google_benchmark.sh
#   3. ./run_google_benchmark.sh
#   4. IMPORTANTE: NO commitear este archivo con credenciales reales
#
# Este archivo está en .gitignore para tu seguridad

# Configura tus credenciales aquí (SOLO para uso local)
export GOOGLE_SEARCH_API_KEY="tu_api_key_aqui"
export GOOGLE_SEARCH_CX="tu_cx_id_aqui"

# Ejecutar benchmark
python benchmark_google_speed.py
