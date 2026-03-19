# Sentinel - Plan de Trabajo Pendiente

**Fecha**: 2025-12-21  
**Estado**: Roadmap actualizado después de 9+ horas de trabajo

---

## ✅ LO QUE YA FUNCIONA (Validado Hoy)

- [x] Detección de precursors (100% accuracy)
- [x] Predicción se activa correctamente
- [x] Buffer se pre-expande (0.5 → 8.28 MB)
- [x] Drops reducidos 67% (30K → 9.7K)
- [x] Patrón de control descubierto
- [x] Teoría hidrodinámica validada (81.4%)
- [x] Número de Reynolds medido (Re_c = 182)
- [x] Viscosidad del sistema (α = 0.96)

---

## 🔴 PRIORIDAD ALTA (Hacer Primero)

### 1. Validar con Más Datos
**Por qué**: 70 muestras no son suficientes para conclusiones robustas

**Tareas**:
- [ ] Ejecutar benchmark 10 veces
- [ ] Recolectar 700+ muestras
- [ ] Verificar consistencia de Re_c
- [ ] Verificar consistencia de α

**Tiempo estimado**: 1 hora  
**Dificultad**: Baja  
**Comando**:
```bash
for i in {1..10}; do
  python tests/benchmark_levitation.py
  mv /tmp/levitation_benchmark_data.json /tmp/benchmark_$i.json
done
```

---

### 2. Probar con Diferentes Configuraciones
**Por qué**: Validar que el patrón se mantiene en diferentes condiciones

**Tareas**:
- [ ] Packet size: 512, 1500, 9000 bytes
- [ ] Burst rate: 10K, 50K, 100K pps
- [ ] Burst duration: 1s, 2s, 5s
- [ ] Buffer max: 5MB, 10MB, 20MB

**Tiempo estimado**: 2 horas  
**Dificultad**: Media

---

### 3. Implementar Controlador Refinado
**Por qué**: Usar α = 0.96 (medido) en lugar de 0.90 (estimado)

**Tareas**:
- [ ] Actualizar `PredictiveBufferManager` con α = 0.96
- [ ] Implementar predictor de turbulencia (Re)
- [ ] Agregar logging de Re en tiempo real
- [ ] Re-ejecutar benchmark

**Tiempo estimado**: 1 hora  
**Dificultad**: Baja

**Archivo**: `src/buffer/predictive_manager.py`

---

## 🟡 PRIORIDAD MEDIA (Hacer Después)

### 4. Entrenar LSTM
**Por qué**: Mejorar predicción de throughput futuro

**Tareas**:
- [ ] Generar dataset de 1000+ bursts
- [ ] Entrenar LSTM con secuencias de 10 timesteps
- [ ] Validar accuracy > 80%
- [ ] Integrar con controlador

**Tiempo estimado**: 4 horas  
**Dificultad**: Alta

**Archivos**:
- `src/ml/lstm_trainer.py` (crear)
- `src/ml/burst_predictor.py` (crear)

---

### 5. Implementar eBPF Prototype
**Por qué**: Mover control al kernel para latencia < 10 µs

**Tareas**:
- [ ] Escribir programa eBPF básico
- [ ] Hook en `tc` (traffic control)
- [ ] Ajustar buffer desde eBPF
- [ ] Medir latencia real

**Tiempo estimado**: 8 horas  
**Dificultad**: Muy Alta

**Archivos**:
- `src/ebpf/buffer_control.c` (crear)
- `src/ebpf/loader.py` (crear)

**Requisitos**:
- Kernel 5.x+
- libbpf
- clang/llvm

---

### 6. Visualización en Tiempo Real
**Por qué**: Ver el sistema funcionando (dashboard)

**Tareas**:
- [ ] Crear dashboard web simple
- [ ] Mostrar throughput en tiempo real
- [ ] Mostrar buffer size
- [ ] Mostrar Re y predicción de turbulencia
- [ ] Alertas cuando Re > Re_c

**Tiempo estimado**: 3 horas  
**Dificultad**: Media

**Stack sugerido**:
- Backend: FastAPI + WebSockets
- Frontend: HTML + Chart.js

---

## 🟢 PRIORIDAD BAJA (Futuro)

### 7. Hardware Real
**Por qué**: Validar con tráfico real, no simulado

**Tareas**:
- [ ] Conseguir NIC 10 GbE
- [ ] Configurar servidor de pruebas
- [ ] Generar tráfico real (iperf3)
- [ ] Medir drops reales (no simulados)

**Tiempo estimado**: 16 horas  
**Dificultad**: Muy Alta  
**Costo**: ~$500 USD (NIC + servidor)

---

### 8. Cluster Distribuido
**Por qué**: Escalar a múltiples nodos

**Tareas**:
- [ ] Implementar comunicación entre nodos
- [ ] Balanceo de carga inteligente
- [ ] Predicción distribuida
- [ ] Failover automático

**Tiempo estimado**: 40 horas  
**Dificultad**: Muy Alta

---

### 9. Publicación Científica
**Por qué**: Compartir descubrimientos con la comunidad

**Tareas**:
- [ ] Refinar paper (HYDRODYNAMIC_VALIDATION_PAPER.md)
- [ ] Agregar más experimentos
- [ ] Revisar literatura adicional
- [ ] Enviar a conferencia (IEEE INFOCOM, ACM SIGCOMM)

**Tiempo estimado**: 20 horas  
**Dificultad**: Alta

---

## 📋 TESTS PENDIENTES

### Tests Unitarios
- [ ] Test de `TrafficMonitor`
- [ ] Test de `PredictiveBufferManager`
- [ ] Test de `TrafficGenerator`
- [ ] Test de cálculo de Re

### Tests de Integración
- [ ] Test end-to-end con tráfico real
- [ ] Test de failover
- [ ] Test de performance bajo carga

### Tests de Validación
- [ ] Validar ecuación de continuidad refinada
- [ ] Validar modelo PID completo
- [ ] Validar con diferentes topologías

---

## 🔬 INVESTIGACIÓN PENDIENTE

### Preguntas Sin Responder
1. ¿Por qué α = 0.96 y no 0.90?
2. ¿Qué términos faltan en la ecuación de continuidad?
3. ¿El Re_c es constante o depende de configuración?
4. ¿Hay otros números adimensionales relevantes (Froude, Mach)?

### Experimentos Propuestos
- [ ] Variar viscosidad artificialmente
- [ ] Probar con tráfico caótico (no periódico)
- [ ] Aplicar CFD a topología de red
- [ ] Comparar con TCP BBR, Cubic, Reno

---

## 📊 MÉTRICAS A MEDIR

### Performance
- [ ] Latencia de predicción (target: < 10 ms)
- [ ] Latencia de control (target: < 1 µs con eBPF)
- [ ] Throughput máximo soportado
- [ ] CPU usage

### Accuracy
- [ ] Precisión de predicción de throughput
- [ ] Precisión de predicción de drops (Re)
- [ ] False positive rate
- [ ] False negative rate

### Robustness
- [ ] Comportamiento bajo carga extrema
- [ ] Recuperación después de falla
- [ ] Estabilidad a largo plazo (24h+)

---

##  OBJETIVOS POR FASE

### Fase 1: Validación Robusta (1 semana)
- [x] Benchmark inicial
- [ ] 10+ benchmarks adicionales
- [ ] Validación estadística
- [ ] Paper refinado

### Fase 2: Implementación Completa (1 mes)
- [ ] LSTM entrenado
- [ ] eBPF prototype
- [ ] Dashboard en tiempo real
- [ ] Tests automatizados

### Fase 3: Producción (3 meses)
- [ ] Hardware real
- [ ] Cluster distribuido
- [ ] Certificación de seguridad
- [ ] Documentación completa

### Fase 4: Publicación (6 meses)
- [ ] Paper publicado
- [ ] Patente solicitada
- [ ] Producto comercial
- [ ] Comunidad open source

---

##  QUICK WINS (Hacer Mañana)

### 1. Ejecutar 10 Benchmarks (30 min)
```bash
cd /home/jnovoas/sentinel
source venv/bin/activate
for i in {1..10}; do
  echo "Benchmark $i/10"
  python tests/benchmark_levitation.py
done
```

### 2. Actualizar α a 0.96 (15 min)
```python
# En src/buffer/predictive_manager.py
self.decay_factor = 0.96  # Cambiar de 0.90 a 0.96
```

### 3. Agregar Predictor de Turbulencia (30 min)
```python
def predict_turbulence(self, throughput):
    Re = throughput / 0.04  # viscosity = 1 - 0.96
    if Re > 182:
        logger.warning(f"Turbulence predicted! Re={Re:.1f}")
        return True
    return False
```

---

## 📝 DOCUMENTACIÓN PENDIENTE

- [ ] README actualizado con resultados
- [ ] Tutorial de uso
- [ ] API documentation
- [ ] Deployment guide
- [ ] Troubleshooting guide

---

## 🤝 COLABORACIÓN

### Buscar Ayuda En:
- **LSTM**: Alguien con experiencia en ML/time series
- **eBPF**: Alguien con experiencia en kernel programming
- **Hardware**: Alguien con acceso a servidores 10 GbE
- **Paper**: Alguien con experiencia en publicaciones científicas

### Comunidades:
- Reddit: r/networking, r/MachineLearning
- Stack Overflow: networking, ebpf tags
- GitHub: Buscar colaboradores
- LinkedIn: Networking researchers

---

## ⏱ ESTIMACIÓN TOTAL

**Prioridad Alta**: ~4 horas  
**Prioridad Media**: ~15 horas  
**Prioridad Baja**: ~76 horas  

**Total**: ~95 horas (~12 días de trabajo full-time)

---

## 🎓 APRENDIZAJE NECESARIO

- [ ] eBPF programming (tutorial: https://ebpf.io)
- [ ] LSTM/RNN (curso: Fast.ai)
- [ ] Fluid dynamics (libro: White, Fluid Mechanics)
- [ ] Network calculus (libro: Le Boudec)
- [ ] Control theory (libro: Åström, Feedback Systems)

---

**Última actualización**: 2025-12-21 01:41  
**Próxima revisión**: Mañana (con cabeza fría)  
**Status**:  **ROADMAP COMPLETO - LISTO PARA EJECUTAR**
