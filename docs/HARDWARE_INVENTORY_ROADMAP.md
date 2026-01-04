# Sentinel Hardware Inventory & Capabilities

**Fecha**: 2025-12-20  
**Propósito**: Documentar hardware disponible y definir roadmap realista

---

## 🖥 Hardware Actual

### CPU
- **Modelo**: Intel Core i5-10300H @ 2.50GHz
- **Cores**: 4 físicos, 8 threads (HyperThreading)
- **Frecuencia**: 800 MHz - 4.5 GHz (Turbo Boost)
- **Arquitectura**: x86_64, 10th Gen Intel

### Memoria
- **RAM Total**: 11 GB
- **RAM Disponible**: 3.6 GB
- **RAM Usada**: 7.7 GB
- **Swap**: 4.0 GB (2.0 GB usado)

### Almacenamiento
- **Disco**: ~450 GB total (verificar con df -h)
- **Tipo**: SSD (asumido por velocidad del sistema)

### Sistema Operativo
- **Kernel**: Linux 6.12.63-1-lts
- **Python**: 3.13.11
- **Distribución**: Arch Linux (basado en kernel LTS)

### Software Instalado
- ✅ Python 3.13
- ❌ PyTorch (NO instalado)
- ❌ NumPy (NO instalado)
- ❌ Matplotlib (NO instalado)

---

##  Capacidades con Este Hardware

### ✅ Lo que PODEMOS hacer:

#### 1. Benchmark de Tráfico (AHORA)
- **CPU suficiente**: 8 threads para simular tráfico concurrente
- **RAM suficiente**: 3.6 GB disponibles para buffers de 10 MB
- **Latencia**: Simulación de nanosegundos en Python (no real, pero demostrativo)

**Limitación**: No es hardware real de red (100 GbE), pero podemos simular el comportamiento.

---

#### 2. LSTM Básico (MAÑANA)
- **CPU**: i5-10300H puede entrenar modelo pequeño
- **RAM**: 3.6 GB suficiente para dataset de 100-1000 bursts
- **Tiempo estimado**: 
  - 100 bursts: ~5 minutos
  - 1000 bursts: ~30 minutos

**Requisito**: Instalar PyTorch (CPU version)
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**Limitación**: Sin GPU, entrenamiento será lento pero funcional.

---

#### 3. Visualización (MAÑANA)
- **CPU**: Suficiente para matplotlib
- **RAM**: Suficiente para gráficas

**Requisito**: Instalar matplotlib
```bash
pip3 install matplotlib numpy
```

---

#### 4. eBPF Básico (POSIBLE)
- **Kernel**: 6.12.63 tiene soporte completo de eBPF
- **Herramientas**: Necesita bpftool, clang, llvm

**Requisito**: Instalar toolchain
```bash
sudo pacman -S bpf clang llvm
```

**Limitación**: No tenemos tarjeta de red 100 GbE, pero podemos usar loopback (lo) para demos.

---

### ❌ Lo que NO podemos hacer (sin hardware adicional):

#### 1. Line-Rate 100 Gbps
- **Razón**: No tenemos tarjeta de red 100 GbE
- **Alternativa**: Simular con loopback, demostrar concepto

#### 2. NPU/DPU Real
- **Razón**: i5-10300H no tiene NPU dedicado
- **Alternativa**: Usar CPU para inferencia (más lento pero funcional)

#### 3. Field Generation (Levitación Física)
- **Razón**: No tenemos hardware ultrasónico/electromagnético
- **Alternativa**: Solo documentar especificación

#### 4. Multi-Node Real
- **Razón**: Solo tenemos 1 máquina
- **Alternativa**: Simular múltiples nodos en procesos separados

---

## 🛤 Roadmap Basado en Hardware Actual

### Fase 1: Software Proof-of-Concept (HOY + MAÑANA)

**Objetivo**: Demostrar concepto con simulación

#### Hoy (30 min):
- [x] Benchmark de tráfico simulado
- [ ] Generar datos de drops (reactive vs predictive)

#### Mañana (8 horas):
- [ ] Instalar PyTorch + Matplotlib
- [ ] Entrenar LSTM básico (100 bursts)
- [ ] Generar visualización profesional
- [ ] Integrar LSTM → Benchmark
- [ ] Script de demo ejecutable

**Entregable**: Demo funcional que muestra zero drops con predicción

---

### Fase 2: eBPF Prototype (Semana 1)

**Objetivo**: Control a nivel kernel (simulado)

- [ ] Instalar toolchain eBPF
- [ ] Escribir programa XDP básico
- [ ] Probar en loopback (lo)
- [ ] Medir latencia real (µs)

**Entregable**: eBPF funcionando en kernel, aunque sin hardware de red real

---

### Fase 3: Hardware Upgrade (Futuro)

**Para hacer REAL**:

#### Opción A: Raspberry Pi Cluster (~$500)
- 5x Raspberry Pi 5 (8GB RAM cada uno)
- Red Gigabit entre nodos
- Simular mesh network

#### Opción B: Tarjeta de Red 10 GbE (~$200)
- Mellanox ConnectX-3 (10 GbE)
- Probar line-rate real
- Validar latencia nanosegundo

#### Opción C: NPU/DPU (~$1000)
- Intel Movidius Neural Compute Stick
- O Google Coral TPU
- Inferencia acelerada

---

## 📊 Estimación de Performance con Hardware Actual

### Benchmark de Tráfico
- **Throughput simulado**: 50,000 pps (limitado por Python)
- **Latencia simulada**: ~1 ms (no nanosegundos reales)
- **Drops detectables**: ✅ SÍ (simulación válida)

### LSTM Training
- **Dataset**: 100-1000 bursts
- **Tiempo**: 5-30 minutos (CPU)
- **Accuracy esperada**: 80-90%

### eBPF
- **Latencia real**: ~1-10 µs (en loopback)
- **Throughput**: ~1 Gbps (limitado por loopback)

---

## ✅ Conclusión: Qué Hacer con Este Hardware

### LO QUE SÍ PODEMOS DEMOSTRAR:

1. **Concepto de predicción** ✅
   - LSTM detecta precursores
   - Buffer se pre-expande
   - Zero drops vs reactive

2. **Visualización profesional** ✅
   - Gráficas que muestran levitación
   - Datos exportables

3. **eBPF básico** ✅
   - Código funcionando en kernel
   - Latencia medible (aunque no nanosegundos)

4. **Demo ejecutable** ✅
   - Script de 1 minuto
   - Reproducible por otros

### LO QUE NECESITAMOS DOCUMENTAR (sin implementar):

1. **Hardware real** (SBN-1)
   - Especificación completa ✅ (ya hecho)
   - Costo estimado ✅ (ya hecho)
   - PCB design ⏳ (futuro)

2. **Line-rate 100 Gbps**
   - Arquitectura ✅ (ya documentado)
   - Pruebas reales ⏳ (requiere hardware)

3. **Multi-node mesh**
   - Protocolo ✅ (ya documentado)
   - Implementación real ⏳ (requiere múltiples nodos)

---

##  Plan de Acción INMEDIATO

### Paso 1: Instalar Dependencias (5 min)
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip3 install matplotlib numpy
```

### Paso 2: Ejecutar Benchmark Corregido (2 min)
```bash
python3 tests/benchmark_levitation.py
```

### Paso 3: Generar Visualización (1 min)
```bash
python3 tests/visualize_levitation.py
```

### Paso 4: Entrenar LSTM (30 min mañana)
```bash
python3 tests/train_lstm_basic.py
```

---

**Hardware actual es SUFICIENTE para demostrar el concepto.**

**No necesitamos SBN-1 físico para probar que la idea funciona.** 

---

**Autor**: Sentinel Cortex™ Team  
**Hardware**: Intel i5-10300H, 11GB RAM, Linux 6.12  
**Status**: ✅ READY TO EXECUTE
