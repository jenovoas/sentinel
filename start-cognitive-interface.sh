#!/bin/bash

# Sentinel Cognitive Interface - Development Server
# This script starts the Next.js development server for the Cognitive Interface

echo "🧬 Starting Sentinel Cognitive Interface..."
echo "================================================"
echo ""
echo "📍 Access Points:"
echo "   - Main Interface: http://localhost:3000"
echo "   - Cognitive Interface: http://localhost:3000/cognitive"
echo "   - Merkabah Core: Integrated in /cognitive"
echo "   - Dimensional Navigation: Integrated in /cognitive"
echo ""
echo "🌌 Features:"
echo "   ✓ Sacred Geometry Visualization (Merkabah)"
echo "   ✓ Dimensional Layer Navigation"
echo "   ✓ Resonance-Based Interaction"
echo "   ✓ Real-time Coherence Metrics"
echo "   ✓ Oracle Console Integration"
echo ""
echo "⚡ Starting development server..."
echo ""

cd "$(dirname "$0")/frontend"
npm run dev
