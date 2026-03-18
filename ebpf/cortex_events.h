/* SPDX-License-Identifier: GPL-2.0 */
/*
 * ME-60OS Cortex Events — Contrato de Verdad Compartida (Unified)
 *
 * Defin estructuras de eventos compartidas entre:
 *   - Programas eBPF en kernel (Ring 0)
 *   - Rust bridge en userspace (ebpf_cortex_bridge.rs)
 *   - Agentes ME-60OS (quantum bus / Redis)
 *
 * AXIOMA: Sin floats. Todo en S60 raw (SCALE_0 = 12,960,000 = 60^4).
 * AXIOMA: Salto-17 para distribución de fase: Phase(n) = (n * 17) % 60
 * AXIOMA: T=68s (17*4) es el ciclo de reset QHC del sistema.
 *
 * Copyright (c) 2026 ME-60OS Development Team
 */

#ifndef __CORTEX_EVENTS_H__
#define __CORTEX_EVENTS_H__

/* Note: Do NOT include linux/types.h here — conflicts with vmlinux.h.
 * Los tipos (__u64, __u32, __u8) son provistos por vmlinux.h */

/* ─────────────────────────────── TIPOS DE EVENTO ─────────────────────── */

#define EVENT_FILE_BLOCKED      1   /* Archivo bloqueado por LSM */
#define EVENT_EXEC_BLOCKED      2   /* Ejecución bloqueada por Guardian */
#define EVENT_FILE_ALLOWED      3   /* Acceso a archivo permitido */
#define EVENT_EXEC_ALLOWED      4   /* Ejecución permitida (en whitelist) */
#define EVENT_NETWORK_BURST     5   /* Anomalía de red detectada */
#define EVENT_NETWORK_NORMAL    6   /* Tráfico de red normal */
#define EVENT_SYSTEM_METRIC     7   /* Métrica del sistema (bio-resonancia) */
#define EVENT_BIO_PULSE         8   /* Señal de pulso biológico (17s) */
#define EVENT_QHC_RESET         9   /* Reset cuántico T=68s */

/* ─────────────────────────────── NIVELES DE SEVERIDAD (S60) ───────────── */

/* Mapeados a valores SPA raw (SCALE_0 = 12,960,000):
 * LOW      → S60(0, 9,  0, 0, 0) = "Disonancia baja"
 * MEDIUM   → S60(0, 30, 0, 0, 0) = "Umbral de alerta"
 * HIGH     → S60(0, 45, 0, 0, 0) = "Disonancia alta"
 * CRITICAL → S60(0, 51, 0, 0, 0) = "Incoherencia crítica"
 */
#define SEVERITY_LOW       0
#define SEVERITY_MEDIUM    1
#define SEVERITY_HIGH      2
#define SEVERITY_CRITICAL  3

/* ─────────────────────────────── CONSTANTES MAESTRAS ─────────────────── */

/* S60 SCALE_0 = 60^4 = 12,960,000 (debe coincidir con Rust SPA::SCALE_0) */
#define S60_SCALE_0     12960000ULL

/* Pulso humano maestro (17 segundos en nanosegundos) */
#define BIO_PULSE_NS    (17ULL * 1000000000ULL)

/* Ciclo mayor QHC: T=68s (17*4) en nanosegundos */
#define QHC_CYCLE_NS    (68ULL * 1000000000ULL)

/* ─────────────────────────────── ESTRUCTURA SPA EN KERNEL ─────────────── */

/*
 * s60_entropy_t — Representación S60 de entropía en kernel
 * Permite cálculo de componentes individuales sin floats.
 * Nota: En el ring buffer principal se usa la representación raw (u64)
 * para mantener el struct en 32 bytes. Esta estructura se usa en
 * programas eBPF que necesitan acceso a los componentes individuales.
 */
struct s60_entropy_t {
    __u64 raw_value;    /* Valor crudo: entropy_raw / S60_SCALE_0 = grados */
    __u8  degree;       /* Grados (0-59) */
    __u8  minute;       /* Minutos (0-59) */
    __u8  second;       /* Segundos (0-59) */
    __u8  tertia;       /* Tercias (0-59) */
    __u8  stability;    /* 0 = Caos, 59 = Coherencia Soberana */
    __u8  _pad[3];      /* Alineación */
};

/* ─────────────────────────────── EVENTO PRINCIPAL (32 bytes) ──────────── */

/*
 * cortex_event — Evento enviado desde Ring 0 al bridge Rust
 *
 * Escrito por eBPF en kernel, leído por ebpf_cortex_bridge.rs via ring buffer.
 * Tamaño: 32 bytes (cache-line friendly, sin gaps).
 * DEBE coincidir con RawCortexEvent en ebpf_cortex_bridge.rs:
 *   pub struct RawCortexEvent {
 *       timestamp_ns: u64,   event_type: u32, pid: u32,
 *       entropy_signal: u64, severity: u8,    _reserved: [u8; 7]
 *   }
 */
struct cortex_event {
    __u64 timestamp_ns;      /* bpf_ktime_get_ns() — nanosegundos exactos */
    __u32 event_type;        /* EVENT_* constante */
    __u32 pid;               /* Process ID que disparó el evento */
    __u64 entropy_signal;    /* S60 raw value (escalado por S60_SCALE_0) */
    __u8  severity;          /* SEVERITY_* level */
    __u8  reserved[7];       /* Padding a 32 bytes */
} __attribute__((packed));

/* ─────────────────────────────── EVENTO DE RED (32 bytes) ─────────────── */

/*
 * network_burst_event — Evento extendido para anomalías de red
 * Usado por burst_sensor.c
 */
struct network_burst_event {
    __u64 timestamp_ns;
    __u32 event_type;        /* EVENT_NETWORK_BURST o EVENT_NETWORK_NORMAL */
    __u32 packets_per_sec;   /* Tasa de paquetes actual */
    __u64 entropy_signal;    /* S60 raw value */
    __u8  severity;          /* Nivel de severidad del burst */
    __u8  reserved[7];
} __attribute__((packed));

/* ─────────────────────────────── STATIC ASSERTIONS ────────────────────── */

/* Verificar tamaños en tiempo de compilación (solo C11+) */
#ifndef __BPF__
_Static_assert(sizeof(struct cortex_event) == 32,
    "cortex_event debe ser exactamente 32 bytes");
_Static_assert(sizeof(struct network_burst_event) == 32,
    "network_burst_event debe ser exactamente 32 bytes");
#endif

#endif /* __CORTEX_EVENTS_H__ */
