# MATRIZ DE TRAZABILIDAD DE REQUISITOS - SENTINEL CORTEX

Esta matriz vincula los requisitos funcionales y de seguridad con su implementación técnica específica y las métricas de validación obtenidas en el entorno de producción estable.

| Requisito Técnico | Implementación Física | Validación Métrica | Estado |
| :--- | :--- | :--- | :--- |
| **Intercepción Pre-Ejecución** | Hook eBPF LSM `bprm_check_security` | TTE: 3.23 μs (Ruta crítica) | ✅ Verificado |
| **Aislamiento de Recursos** | Cgroups v2 (CPUQuota=10%, MemoryMax=100M) | Estabilidad bajo stress (5000 exec/s) | ✅ Verificado |
| **Plano de Datos de Baja Latencia** | BPF Ringbuffer + Nativo C Relay | Latencia Relay: 4.1 μs (Asíncrono) | ✅ Verificado |
| **Procesamiento de Eventos** | Rust Engine (`truthsync_core`) + SHM | Latencia de procesamiento: 5 μs | ✅ Verificado |
| **Resiliencia Operacional** | systemd Watchdog (Restart=always) | Uptime verificado / Reinicio automático | ✅ Verificado |
| **Inferencia Semántica** | Local LLM (Llama 3.2:3b via Ollama) | Integración asíncrona validada | ✅ Verificado |
| **Comunicación Inter-Proceso** | File-backed Memory Map (`/tmp/truthsync_shm`) | Consumo CPU Relay < 0.1% | ✅ Verificado |
| **Integridad de Reportes** | Firma mediante TPM 2.0 (Hardware Trust) | 100% Integrity Score en Battlefield Log | ✅ Verificado |

## 🛠️ Metodología de Validación
Las métricas han sido obtenidas mediante el suite de pruebas `sentinel_tte_certifier.py` y el script de stress `pressure_injector.sh`, operando sobre el kernel Linux con soporte LSM activo.

---
*Documento generado para la certificación técnica de Sentinel Cortex v1.1.0.*
