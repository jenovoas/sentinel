# 🏗️ Arquitectura de Sentinel (Ring 0)

## 3. Ecosistema PinguinoSeguro

El nodo Fenix no solo aloja el monitoreo, sino que sirve como hub para los servicios productivos:

### 3.1 Portal PinguinoSeguro
Portal corporativo y portfolio personal. Implementado en Next.js con diseño Glassmorphism y cumplimiento ISO 27001.

### 3.2 La Espiguita
Sistema ERP e IoT para panaderías industriales.
- **Backend:** Axum (Rust) + PostgreSQL.
- **Frontend:** React + Vite.
- **IoT:** Broker MQTT (Mosquito) para telemetría de planta.

### 4. Capas de Seguridad (Ring 0-3)

**Versión**: 1.2.0 (S60-Unified / Fenix Native)  
**Última Actualización**: 18 de marzo de 2026  
**Entorno de Ejecución**: Podman Rootless (Rocky Linux 9)
**Estilo Arquitectónico**: Microservicios de bajo nivel con Orquestación en Rust (Cortex™)

---

## 🎯 Resumen General

Sentinel es una infraestructura de observabilidad y seguridad **pure-Rust** que combina:
- **Núcleo Cortex™** - Motor de orquestación asíncrono en Rust (Axum + Tokio).
- **Aritmética Base-60** - Cálculos de alta precisión mediante `me60os_core`.
- **eBPF Guardian** - Defensa a nivel de Kernel (LSM) en Ring 0.
- **Stack de Observabilidad** - Prometheus, Loki y Grafana integrados.
- **Automatización n8n** - Flujos de trabajo para respuesta ante incidentes.

---

## 🏛️ Diagrama de Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CAPA DE CLIENTE                            │
│                     (Navegador Web / Dashboard)                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS (Traefik)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         TRAEFIK PROXY                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Enrutamiento  │  │ TLS 1.3      │  │ Middlewares  │              │
│  │ Dinámico     │  │ Termination  │  │ de Seguridad │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   FRONTEND DEV  │ │ **SENTINEL CORTEX** │ │   MONITOREO     │
│  (dev.pinguino) │ │   **(RUST)**      │ │   (Grafana)     │
│   Puerto 80     │ │   Puerto 8000     │ │   Puerto 3000     │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         │                   │                   │
         │         ┌─────────┼─────────┐         │
         │         │         │         │         │
         ▼         ▼         ▼         ▼         ▼
┌─────────────────────────────────────────────────────────┐
│                   CAPA DE DATOS                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  PostgreSQL  │  │    Redis     │  │  Motor S60   │  │
│  │  (Persistencia)│  │   (Cache)    │  │ (Matemática) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                CAPA DE OBSERVABILIDAD                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Prometheus  │  │     Loki     │  │   Grafana    │  │
│  │  (Métricas)   │  │    (Logs)    │  │ (Dashboards) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                  CAPA DE SEGURIDAD (RING 0)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  eBPF LSM    │  │   Guardian   │  │  Resonancia  │  │
│  │  (Kernel)    │  │   Watcher    │  │   Harmónica  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🧩 Detalles de los Componentes

### 1. Núcleo Cortex™ (Rust)
Es el corazón del sistema, sustituyendo por completo al antiguo backend legado en Python.
- **Tecnología**: Rust 1.75+, Axum, Tokio Runtime.
- **Funciones**:
  - API de alta concurrencia para el dashboard.
  - Orquestación de tareas en segundo plano (Resonancia).
  - Integración nativa con `me60os_core` (Base-60).
- **Rendimiento**: < 10ms de latencia en endpoints críticos.

### 2. Capa de Datos y Matemática
- **PostgreSQL**: Almacenamiento persistente de configuraciones y eventos.
- **Redis**: Caché de alta velocidad para estados efímeros del sistema.
- **Motor S60**: Aritmética sexagesimal pura. Sin errores de redondeo IEEE-754.

### 3. Observabilidad
- **Prometheus**: Recolección de métricas del sistema y del Cortex.
- **Loki**: Agregación de logs para un seguimiento forense completo.
- **Grafana**: Visualización en tiempo real con dashboards específicos para Base-60.

### 4. Seguridad (eBPF)
- **Guardian LSM**: Políticas de seguridad aplicadas directamente en el Kernel de Linux mediante eBPF.
- **Monitor de Resonancia**: Verificación de integridad basada en pulsos de 17 segundos.

---

## 📈 Especificaciones Técnicas

| Métrica | Objetivo |
|---------|----------|
| Latencia de API | < 50ms (P95) |
| Errores de Flotantes | 0 (Exactitud Base-60) |
| Latencia de Red eBPF | < 100µs |
| Ciclo de Sincronización | 17 segundos (Fase Harmónica) |

---

## 🌐 Topología de Red (Fenix Sovereign Node)

| Nodo | IP Interna | Función |
| :--- | :--- | :--- |
| **Fenix** | `10.10.10.8` | Orquestador Ring 0 / DNS Master / Proxy / App Host |

**Notas de Conectividad:**
- **VPN (Wireguard)**: Gateway en `10.100.0.1`.
- **SSH**: Puerto **4222** (Acceso root prohibido).
- **PowerDNS API**: Accesible solo vía VPN en `http://10.100.0.1:8081`.

---

**YATRA. Truth Resonates.**
