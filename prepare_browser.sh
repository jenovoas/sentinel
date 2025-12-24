#!/bin/bash

# Script para preparar el sistema antes de usar el navegador
# Reduce la carga del sistema para evitar sobrecalentamiento

echo "🔧 Preparando el sistema para usar el navegador..."
echo ""

# 1. Mostrar temperatura actual
echo "📊 Temperatura actual del CPU:"
sensors | grep "Package id 0" || sensors | grep "Core 0"
echo ""

# 2. Cerrar procesos innecesarios que consumen mucho
echo "🧹 Cerrando procesos innecesarios..."

# Cerrar GNOME Software si está abierto (consume mucho)
pkill -f gnome-software && echo "  ✓ Cerrado GNOME Software" || echo "  - GNOME Software no estaba corriendo"

# Cerrar Evolution si está abierto
pkill -f evolution && echo "  ✓ Cerrado Evolution" || echo "  - Evolution no estaba corriendo"

# Cerrar Tracker (indexador de archivos)
tracker3 reset -s && echo "  ✓ Detenido Tracker (indexador)" || echo "  - Tracker no disponible"

echo ""

# 3. Limpiar caché
echo "🗑️  Limpiando caché del sistema..."
sync
echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null 2>&1 && echo "  ✓ Caché limpiado" || echo "  ⚠️  No se pudo limpiar caché (requiere sudo)"

echo ""

# 4. Verificar memoria disponible
echo "💾 Memoria disponible:"
free -h | grep "Mem:"

echo ""

# 5. Sugerencias
echo "📋 RECOMENDACIONES:"
echo "  1. Usa Firefox en lugar de Chrome (consume menos RAM)"
echo "  2. Abre máximo 3-4 pestañas"
echo "  3. Cierra este IDE (Antigravity) temporalmente si es posible"
echo "  4. Asegúrate de que la laptop tenga buena ventilación"
echo ""

# 6. Esperar a que baje la temperatura
echo "⏳ Esperando 10 segundos para que baje la temperatura..."
sleep 10

echo ""
echo "📊 Temperatura después de la limpieza:"
sensors | grep "Package id 0" || sensors | grep "Core 0"

echo ""
echo "✅ Sistema preparado. Ahora puedes abrir el navegador."
echo ""
echo "💡 TIP: Ejecuta './monitor_system.sh' en otra terminal para monitorear en tiempo real"
