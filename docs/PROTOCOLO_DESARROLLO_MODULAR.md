# 🛰 PROTOCOLO DE DESARROLLO MODULAR (MODO FRÍO)

**Estado**: SOPORTE LOCAL OPTIMIZADO  
**Objetivo**: Programación de Sentinel sin carga térmica (Sin Front/Back en background).

---

## 🛠 FILOSOFÍA DE TRABAJO

Dado que el hardware local tiene límites térmicos, hemos pasado a una **Arquitectura de Verificación Modular**. No es necesario levantar el servidor FastAPI ni el frontend de Next.js para seguir construyendo la soberanía.

### Reglas de Oro:
1.  **Cero Background**: No dejar procesos `uvicorn`, `node` o loops infinitos de Python corriendo.
2.  **Validación CLI**: Usar los scripts de auditoría y el nuevo orquestador ligero.
3.  **TruthSync Offline**: Los módulos usan el motor de TruthSync directamente desde el sistema de archivos.

---

##  INTERFACES DISPONIBLES

### 1. El Orquestador Ligero (CLI)
Este es tu nuevo centro de comando. Consume recursos mínimos y permite interactuar con los 4 switches.
```bash
python3 /home/jnovoas/sentinel/quantum/SENTINEL_MODULAR_CLI.py
```

### 2. Auditoría Maestra TruthSync
Verifica la integridad de todo el sistema en segundos.
```bash
python3 /home/jnovoas/sentinel/quantum/TRUTHSYNC_FULL_SYSTEM_AUDIT.py
```

### 3. Simulador de Watchdog (Manual)
En lugar de dejarlo corriendo, puedes ejecutarlo una vez para generar el estado y luego cerrarlo.
```bash
python3 /home/jnovoas/sentinel/ebpf/quantum_watchdog_simulator.py
(Presiona Ctrl+C después de un ciclo)
```

---

## 📦 ESTRUCTURA DE MÓDULOS ACTIVOS

- **Switch 1**: `quantum/trinity_final_sovereign.py`
- **Switch 2**: `ebpf/quantum_watchdog_simulator.py`
- **Switch 3**: `backend/app/routers/infrastructure.py` (Lógica disponible para CLI)
- **Switch 4**: `backend/app/services/perpetual_engine.py` (Lógica disponible para CLI)

**Sentinel está ahora en modo "Silent Sovereignty". Construimos en frío, ejecutamos en caliente solo cuando sea necesario.**

📐⚛
