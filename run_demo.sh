#!/bin/bash
# Sentinel Quick Start - Execute Benchmark and Visualization

echo "🚀 SENTINEL LEVITATION DEMO"
echo "================================"
echo ""

# Activate virtual environment
source venv/bin/activate

echo "1️⃣ Running benchmark (reactive vs predictive)..."
echo "   This will take ~60 seconds..."
echo ""
python3 tests/benchmark_levitation.py

echo ""
echo "2️⃣ Generating visualization..."
python3 tests/visualize_levitation.py

echo ""
echo "✅ DONE!"
echo ""
echo "📊 Results:"
echo "   - Benchmark data: /tmp/levitation_benchmark_data.json"
echo "   - Visualization: docs/levitation_proof.png"
echo ""
echo "🎯 Expected: ZERO drops in predictive mode"
