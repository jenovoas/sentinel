// SPDX-License-Identifier: GPL-2.0
/* Sentinel Float Detector — Ring 0 YATRA Lock Enforcement
 *
 * Hook LSM bprm_check_security: antes de ejecutar un binario,
 * verifica si está declarado "S60-safe" en la whitelist.
 *
 * Semántica (modo conservador por defecto):
 *   - Binario en float_safe_map (value=1)  → allow silencioso
 *   - Binario en float_block_map (value=1) → block + evento
 *   - Binario desconocido                  → allow + evento (log-only)
 *
 * El modo de auditoría permite recopilar señales sin interrumpir el sistema.
 *
 * Emite cortex_event (32 bytes) compatible con ebpf_cortex_bridge.rs.
 * event_type = EVENT_FLOAT_CONTAMINATION (10).
 *
 * Copyright (c) 2026 Sentinel Cortex™
 */

#include "vmlinux.h"
#include <bpf/bpf_core_read.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include "cortex_events.h"

#ifndef EACCES
#define EACCES 13
#endif

/* Los bloqueos requieren activar explícitamente float_detector_mode. */
#define FLOAT_ENFORCE_UNKNOWN 0

/* 0 = auditoría (valor inicial seguro); 1 = aplicar blacklist explícita. */
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, __u32);
    __type(value, __u32);
} float_detector_mode SEC(".maps");

/* Whitelist de binarios S60-safe (auditados, sin uso de FPU problemático). */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 4096);
    __type(key, char[256]);
    __type(value, __u8);
} float_safe_map SEC(".maps");

/* Blacklist explícita: binarios conocidos por contaminar con floats. */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 4096);
    __type(key, char[256]);
    __type(value, __u8);
} float_block_map SEC(".maps");

/* Map de desvío PAI: binarios cuyos cálculos decimales son redirigidos a Ring 0 / S60 */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 4096);
    __type(key, char[256]);
    __type(value, __u8);
} float_redirect_map SEC(".maps");

/* Ring buffer compartido con el bridge Rust. */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

static __always_inline void
emit_event(__u32 pid, __u8 severity)
{
    struct cortex_event *e;
    e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e)
        return;

    __builtin_memset(e, 0, sizeof(*e));

    e->timestamp_ns   = bpf_ktime_get_ns();
    e->event_type     = EVENT_FLOAT_CONTAMINATION;
    e->pid            = pid;
    e->entropy_signal = (__u64)severity * S60_SCALE_0;
    e->severity       = severity;
    e->reserved[0]    = GUARDIAN_CODE_FLOAT;

    bpf_ringbuf_submit(e, 0);
}

static __always_inline __u32 float_detector_enforcing(void)
{
    __u32 key = 0;
    __u32 *mode = bpf_map_lookup_elem(&float_detector_mode, &key);
    return mode && *mode == 1;
}

static __always_inline void
emit_math_diversion(__u32 pid, __u64 payload_signal, __u8 severity)
{
    struct cortex_event *e;
    e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e)
        return;

    __builtin_memset(e, 0, sizeof(*e));

    e->timestamp_ns   = bpf_ktime_get_ns();
    e->event_type     = EVENT_MATH_DIVERSION;
    e->pid            = pid;
    e->entropy_signal = payload_signal > 0 ? payload_signal : S60_SCALE_0;
    e->severity       = severity;
    e->reserved[0]    = GUARDIAN_CODE_FLOAT;

    bpf_ringbuf_submit(e, 0);
}

SEC("lsm.s/bprm_check_security")
int BPF_PROG(float_detector, struct linux_binprm *bprm, int ret)
{
    if (ret != 0)
        return ret;

    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u32 enforcing = float_detector_enforcing();
    const char *filename = BPF_CORE_READ(bprm, filename);

    char key[256] = {0};
    bpf_probe_read_kernel_str(key, sizeof(key), filename);

    /* 1. Blacklist explícita — bloqueo inmediato */
    __u8 *blocked = bpf_map_lookup_elem(&float_block_map, key);
    if (blocked && *blocked) {
        if (!enforcing) {
            struct cortex_event *e;
            e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
            if (e) {
                __builtin_memset(e, 0, sizeof(*e));
                e->timestamp_ns = bpf_ktime_get_ns();
                e->event_type = EVENT_FLOAT_WOULD_BLOCK;
                e->pid = pid;
                e->entropy_signal = (__u64)SEVERITY_CRITICAL * S60_SCALE_0;
                e->severity = SEVERITY_CRITICAL;
                e->reserved[0] = GUARDIAN_CODE_FLOAT;
                bpf_ringbuf_submit(e, 0);
            }
            return 0;
        }
        emit_event(pid, SEVERITY_CRITICAL);
        bpf_printk("FloatDetector [BLOCK]: contaminated %s", filename);
        return -EACCES;
    }

    /* 2. Redirección PAI-60 explícita — desvío de cálculos decimales a Ring 0 */
    __u8 *redirect = bpf_map_lookup_elem(&float_redirect_map, key);
    if (redirect && *redirect) {
        emit_math_diversion(pid, S60_SCALE_0, SEVERITY_HIGH);
        bpf_printk("FloatDetector [REDIRECT->PAI]: diverting math for %s (pid=%d)", filename, pid);
        return 0;
    }

    /* 3. Whitelist — allow silencioso */
    __u8 *safe = bpf_map_lookup_elem(&float_safe_map, key);
    if (safe && *safe) {
        return 0;
    }

    /* 4. Desconocido — política configurable.
     * Sin bpf_printk: el trace pipe cuesta ~µs por exec y este path corre
     * en TODA ejecución no listada. El evento ringbuf conserva la señal. */
    emit_event(pid, SEVERITY_MEDIUM);

#if FLOAT_ENFORCE_UNKNOWN
    return -EACCES;
#else
    return 0;
#endif
}

char LICENSE[] SEC("license") = "GPL";

