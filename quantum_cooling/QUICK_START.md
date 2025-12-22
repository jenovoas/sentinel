# Quantum Cooling - Quick Start Guide

## 🚀 Cómo Probarlo

### Opción 1: Demo Local (Sin Prometheus)

```bash
cd /home/jnovoas/sentinel/research/cosmic_patterns

# V2: Física validada
python quantum_cooling_v2.py

# V3: Algoritmos avanzados
python quantum_cooling_v3.py

# Benchmark completo
python benchmark_comprehensive.py
```

**Resultado**: Verás la simulación en tiempo real.

---

### Opción 2: Con Prometheus Real

```bash
cd /home/jnovoas/sentinel/quantum_cooling

# 1. Verificar que Prometheus esté corriendo
curl http://localhost:9090/-/healthy

# 2. Ejecutar servicio (modo monitoring, sin auto-resize)
python service.py

# 3. Ver métricas en tiempo real
```

**Config**: Edita `config.yaml` para ajustar parámetros.

---

### Opción 3: Producción (Cuando Estés Listo)

```bash
# 1. Editar config
nano /home/jnovoas/sentinel/quantum_cooling/config.yaml

# Cambiar:
enable_auto_resize: true  # ⚠️ Requiere sudo

# 2. Ejecutar como servicio
sudo python service.py

# 3. Monitorear logs
tail -f quantum_cooling.log
```

---

## 📊 Qué Esperar

### V2 Benchmark
- 5 patrones de tráfico
- ~13 segundos de ejecución
- Resultado: 9.9% mejora promedio

### V3 Demo
- Detección de runaway
- Aprendizaje de patrones
- Damping adaptativo
- ~15 segundos

### Servicio Real
- Poll cada 1 segundo
- Logs en tiempo real
- Stats al final (Ctrl+C para detener)

---

## ⚠️ Safety First

**Antes de `enable_auto_resize: true`**:
1. Verificar que tienes permisos sudo
2. Conocer el comando de rollback
3. Tener backup de configuración actual

**Rollback**:
```bash
sudo sysctl -w net.core.rmem_default=<valor_original>
```

---

## 🎯 Próximos Pasos

1. **Hoy**: Ejecutar demos locales
2. **Mañana**: Conectar a Prometheus real
3. **Próxima semana**: Habilitar auto-resize en staging

---

**Todo está listo. Cuando quieras, ejecutamos.** 🧊⚛️
