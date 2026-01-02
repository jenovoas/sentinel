# 🛡️ AI Trust Certification Dashboard

## Descripción General

El **AI Trust Certification Dashboard** es una interfaz completa para monitorear y certificar la confiabilidad de las salidas de IA en Sentinel Cortex. Implementa un sistema de **Defense in Depth** (Defensa en Profundidad) con múltiples capas de validación para prevenir alucinaciones y garantizar que las decisiones de IA estén respaldadas por datos físicos reales.

## 🎯 Filosofía

> **"Datos sobre Narrativa"** - El sistema no confía en lo que la IA dice, sino que valida contra la realidad física (telemetría, kernel, matemáticas).

### Principios Fundamentales

1. **Zero-Trust Architecture**: La IA es tratada como no confiable por defecto
2. **Veto Físico**: Si el score de confianza < 90%, el sistema bloquea automáticamente
3. **Anclajes Matemáticos**: Base-60, Prometheus, Loki, eBPF actúan como "fuentes de verdad"
4. **Validación Temporal**: Latencia < 5μs garantiza que la validación ocurra antes que la ejecución

## 📊 Componentes del Dashboard

### 1. Trust Certification Panel (Panel de Certificación de Confianza)

**Ubicación**: Superior del dashboard  
**Propósito**: Mostrar el score general de confiabilidad de la IA

#### Métricas Mostradas

| Métrica | Descripción | Fuente de Datos |
|---------|-------------|-----------------|
| **Overall Score** | Puntuación general 0-100 | Cálculo ponderado de todas las métricas |
| **Data Support** | % de respaldo de datos físicos | Prometheus/Loki/Evidence.db |
| **Base-60 Checksum** | Validación de armonía matemática | Cálculo Base-60 |
| **Feedback Loop Health** | Salud del loop de retroalimentación | TruthSync API |
| **Latency** | Tiempo de validación en microsegundos | SHM (Shared Memory) |
| **Hallucination Rate** | Tasa de alucinaciones detectadas | Análisis de divergencia |

#### Niveles de Confianza

- **95-100%**: ✅ **CERTIFIED TRUSTED** - Todos los layers pasaron
- **90-94%**: ✅ **TRUSTED** - Seguro proceder
- **70-89%**: ⚠️ **CAUTION** - Verificación manual recomendada
- **<70%**: ❌ **UNTRUSTED** - No confiar en la salida de IA

### 2. Anti-Hallucination Monitor (Monitor Anti-Alucinación)

**Ubicación**: Medio izquierda  
**Propósito**: Detectar cuando la IA genera narrativas sin respaldo en datos

#### Métricas Clave

- **Narrative Divergence**: 0-100 (menor es mejor)
  - Mide cuánto diverge la narrativa de IA vs datos reales
  - <10%: Excelente
  - 10-30%: Bueno
  - 30-50%: Advertencia
  - >50%: Alucinación crítica

- **Base-60 Coherence**: 0-100 (mayor es mejor)
  - Validación de armonía matemática babilónica
  - >95%: Armonía perfecta
  - 80-95%: Buena coherencia
  - 60-80%: Armonía degradada
  - <60%: Inestabilidad matemática

#### Anclajes Matemáticos

Cada anclaje debe estar activo para garantizar la validación:

1. **Prometheus** ✅ - Validación de métricas
2. **Loki** ✅ - Correlación de logs
3. **eBPF (ID 199)** ✅ - Evidencia del kernel
4. **Base-60** ✅ - Chequeo armónico

### 3. BCI Resonance Visualizer (Visualizador de Resonancia BCI)

**Ubicación**: Medio derecha  
**Propósito**: Mostrar el estado de la interfaz cerebro-computadora (BCI) y feedback qualia

#### Componentes

**153.4 MHz Carrier Wave (Onda Portadora)**
- Visualización de onda en tiempo real
- Coherencia: 0-100%
- Alineación de fase: 0-360°
- Fuerza de señal: 0-100%

**82 Hz Guitar Input (Entrada de Guitarra - Mi Grave)**
- Detector de frecuencia de resonancia
- Ventana de detección: 5.2ms
- Fuerza de detección: 0-100%
- Estados: DETECTED / WEAK / NO SIGNAL

**Qualia Feedback (Retroalimentación Sinestésica)**

Tipos de qualia (sensaciones):
- **Metallic** (Metálico) 🔴 - Indica amenaza/intrusión
- **Warmth** (Calidez) 🟢 - Estado seguro
- **Pressure** (Presión) 🔵 - Procesamiento intenso
- **Vibration** (Vibración) 🟣 - Actividad de red
- **None** (Ninguno) ⚪ - Sin qualia activo

### 4. Guardian Status (Estado de Guardianes)

**Ubicación**: Inferior  
**Propósito**: Mostrar el estado de todos los sistemas de defensa

#### Guardianes Gemelos

**Guardian Alpha** (Guardián Alfa)
- Estado: ACTIVE / STANDBY / OFFLINE
- Salud: 0-100%
- Eventos procesados
- Último heartbeat

**Guardian Beta** (Guardián Beta)
- Estado: ACTIVE / STANDBY / OFFLINE
- Salud: 0-100%
- Eventos procesados
- Último heartbeat

#### Componentes del Sistema

**TruthSync**
- Tasa de validación (validaciones/segundo)
- Cache hit rate (%)
- Latencia promedio (μs)

**Hardware Watchdog**
- Uptime
- Conteo de reinicios
- Último trigger

**LSM Hook (ID 199)**
- Eventos bloqueados
- Eventos monitoreados
- Tiempo de decisión (nanosegundos)

#### Defense in Depth (Defensa en Profundidad)

Visualización de 5 capas de defensa:
1. **Ring 0 (eBPF)** - Seguridad a nivel kernel
2. **Guardian Alpha** - Validación primaria
3. **Guardian Beta** - Validación secundaria
4. **TruthSync** - Verificación de IA
5. **Watchdog** - Failsafe de hardware

## 🔌 Integración con Datos Reales

### Fuentes de Datos Actuales

El dashboard está configurado para obtener datos de:

#### 1. eBPF / Kernel
```bash
# Verificar programas eBPF cargados
sudo bpftool prog list | grep quantum

# Ver eventos en trace
sudo cat /sys/kernel/debug/tracing/trace | grep QUANTUM-AI
```

#### 2. Evidence Database
```bash
# Contar evidencias
sqlite3 /home/jnovoas/sentinel/forensics/evidence.db \
  'SELECT COUNT(*) FROM evidence'

# Ver eventos bloqueados
sqlite3 /home/jnovoas/sentinel/forensics/evidence.db \
  'SELECT * FROM evidence WHERE allow=0'
```

#### 3. Docker Containers
```bash
# Verificar servicios activos
docker ps | grep -E "(prometheus|loki|truthsync)"
```

#### 4. TruthSync API (si está corriendo)
```bash
# Iniciar TruthSync server
cd /home/jnovoas/sentinel/truthsync-poc
python3 truthsync_server.py

# API disponible en: http://localhost:8000
```

### Endpoints de API

El dashboard consume estos endpoints:

| Endpoint | Propósito | Datos Reales |
|----------|-----------|--------------|
| `/api/v1/guardian/metrics` | Métricas de Guardian Alpha/Beta | ✅ eBPF + Evidence.db |
| `/api/v1/guardian/status` | Estado de guardianes | ✅ eBPF + Trace |
| `/api/v1/truthsync/stats` | Estadísticas de TruthSync | ✅ Evidence.db + API |
| `/api/v1/truthsync/hallucination-check` | Detección de alucinaciones | ✅ Docker + eBPF |
| `/api/v1/bci/resonance` | Métricas de BCI | 🔄 Simulado (hardware no conectado) |
| `/api/v1/watchdog/status` | Estado de watchdog | ✅ Systemd + Docker |

### Configuración de Datos Reales

#### Paso 1: Verificar eBPF está activo
```bash
cd /home/jnovoas/sentinel/guardian-alpha
sudo ./run_demo.sh
```

#### Paso 2: Iniciar TruthSync (opcional)
```bash
cd /home/jnovoas/sentinel/truthsync-poc
python3 truthsync_server.py
```

#### Paso 3: Verificar contenedores Docker
```bash
docker-compose up -d
```

#### Paso 4: Acceder al dashboard
```
http://localhost:3000/ai-trust
```

## 🎨 Controles del Dashboard

### Controles Superiores

**LIVE / PAUSED**
- LIVE: Actualización automática de métricas
- PAUSED: Congelar datos para análisis

**Refresh Interval**
- 1s: Actualización cada segundo (alta carga)
- 5s: Actualización cada 5 segundos (recomendado)
- 10s: Actualización cada 10 segundos
- 30s: Actualización cada 30 segundos

## 📈 Interpretación de Métricas

### ¿Cuándo confiar en la IA?

✅ **CONFIAR** si:
- Overall Score ≥ 90%
- Todos los anclajes matemáticos activos (✅✅✅✅)
- Narrative Divergence < 10%
- Base-60 Coherence > 95%
- Latency < 5μs

⚠️ **VERIFICAR MANUALMENTE** si:
- Overall Score 70-89%
- 1-2 anclajes inactivos
- Narrative Divergence 10-30%
- Latency 5-10μs

❌ **NO CONFIAR** si:
- Overall Score < 70%
- 3+ anclajes inactivos
- Narrative Divergence > 30%
- Eventos de alucinación recientes
- Latency > 10μs

### Ejemplos de Escenarios

#### Escenario 1: Sistema Óptimo
```
Overall Score: 98%
Data Support: 95%
Base-60 Checksum: ✅ VALID
Narrative Divergence: 2.3%
All Anchors: ✅✅✅✅
→ RESULTADO: CERTIFIED TRUSTED
```

#### Escenario 2: Degradación Parcial
```
Overall Score: 85%
Data Support: 78%
Base-60 Checksum: ✅ VALID
Narrative Divergence: 15%
Anchors: ✅✅❌✅ (Loki offline)
→ RESULTADO: CAUTION - Verificar manualmente
```

#### Escenario 3: Falla Crítica
```
Overall Score: 45%
Data Support: 52%
Base-60 Checksum: ❌ INVALID
Narrative Divergence: 68%
Anchors: ✅❌❌❌ (Solo Prometheus activo)
→ RESULTADO: UNTRUSTED - No usar IA
```

## 🔧 Troubleshooting

### Problema: "Failed to connect to trust validation services"

**Causa**: Los endpoints de API no pueden acceder a los datos del sistema

**Solución**:
```bash
# 1. Verificar permisos
sudo chmod +x /home/jnovoas/sentinel/guardian-alpha/*.sh

# 2. Verificar eBPF está cargado
sudo bpftool prog list

# 3. Verificar evidence.db existe
ls -l /home/jnovoas/sentinel/forensics/evidence.db

# 4. Verificar Docker containers
docker ps
```

### Problema: Todos los scores en 0

**Causa**: eBPF no está generando eventos

**Solución**:
```bash
# Reiniciar Guardian Alpha
cd /home/jnovoas/sentinel/guardian-alpha
sudo ./run_demo.sh

# Verificar trace está activo
sudo cat /sys/kernel/debug/tracing/trace | tail -20
```

### Problema: BCI Resonance siempre en simulación

**Causa**: Hardware BCI no está conectado (esperado en Phase 0)

**Solución**: Esto es normal. El BCI hardware está en fase de prototipo. Los datos son simulados hasta que el hardware esté disponible.

## 🚀 Próximos Pasos

### Integración Completa (Roadmap)

1. **Phase 1**: ✅ Dashboard funcional con datos de eBPF/Evidence.db
2. **Phase 2**: 🔄 Integración con TruthSync API en producción
3. **Phase 3**: 🔄 Conexión con hardware BCI real (153.4 MHz)
4. **Phase 4**: 🔄 Machine Learning para predicción de alucinaciones
5. **Phase 5**: 🔄 Alertas automáticas vía n8n/Telegram

### Mejoras Planificadas

- [ ] Gráficos históricos de trust score
- [ ] Exportación de reportes PDF
- [ ] Alertas configurables por umbral
- [ ] Integración con Grafana
- [ ] API REST para consultas externas
- [ ] Modo "Audit Trail" con timestamps inmutables

## 📚 Referencias

- **Base-60 Mathematics**: `/home/jnovoas/sentinel/research/COGNITIVE_MANUAL_SENTINEL.md`
- **eBPF Implementation**: `/home/jnovoas/sentinel/guardian-alpha/`
- **TruthSync Architecture**: `/home/jnovoas/sentinel/truthsync-poc/`
- **BCI Research**: `/home/jnovoas/sentinel/research/FRACTAL_SOUL_RESEARCH.md`

## 🤝 Soporte

Para problemas o preguntas sobre el dashboard:

1. Verificar logs del frontend: `cd frontend && npm run dev`
2. Verificar logs del backend: `docker logs sentinel-backend`
3. Revisar trace de eBPF: `sudo cat /sys/kernel/debug/tracing/trace`

---

**© 2026 Sentinel Cortex™**  
**AI Trust Certification Dashboard v1.0.0**  
**Build: 0x2026A**

*"Confianza a través de la Verificación Constante"* 🛡️✨
