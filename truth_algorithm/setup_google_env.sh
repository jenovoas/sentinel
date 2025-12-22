#!/bin/bash
# Script automático para configurar entorno virtual y probar Google API
# ======================================================================

echo "🚀 Configurando entorno para Google Search API..."
echo ""

# 1. Crear entorno virtual
echo "📦 Creando entorno virtual..."
python -m venv venv_google

# 2. Activar entorno virtual
echo "✅ Activando entorno virtual..."
source venv_google/bin/activate

# 3. Instalar dependencias
echo "📥 Instalando google-api-python-client..."
pip install --quiet google-api-python-client python-dotenv

# 4. Verificar instalación
echo ""
echo "✅ Entorno configurado correctamente!"
echo ""
echo "================================================"
echo "INSTRUCCIONES PARA EJECUTAR EL BENCHMARK"
echo "================================================"
echo ""
echo "1. Activar el entorno virtual:"
echo "   source venv_google/bin/activate"
echo ""
echo "2. Ejecutar el test con tus credenciales:"
echo "   python test_google_simple.py TU_API_KEY 80b08c4835fa24341"
echo ""
echo "3. O ejecutar el benchmark completo:"
echo "   python benchmark_google_speed.py"
echo "   (requiere .env configurado)"
echo ""
echo "4. Para salir del entorno virtual:"
echo "   deactivate"
echo ""
echo "================================================"
