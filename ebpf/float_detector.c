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
 * El modo log-only permite poblar la whitelist en producción sin
 * interrumpir el sistema. Una vez estabilizado, se puede endurecer
 * cambiando FLOAT_ENFORCE_UNKNOWN a 1.
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

/* Endurecer política: si está en 1, binarios desconocidos son bloqueados.
 * Por defecto 0 = log-only (recomendado hasta que la whitelist esté poblada).
 */
#define FLOAT_ENFORCE_UNKNOWN 0

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

    bpf_ringbuf_submit(e, 0);
}

SEC("lsm/bprm_check_security")
int BPF_PROG(float_detector, struct linux_binprm *bprm, int ret)
{
    if (ret != 0)
        return ret;

    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    const char *filename = BPF_CORE_READ(bprm, filename);

    char key[256] = {0};
    bpf_probe_read_kernel_str(key, sizeof(key), filename);

    /* 1. Blacklist explícita — bloqueo inmediato */
    __u8 *blocked = bpf_map_lookup_elem(&float_block_map, key);
    if (blocked && *blocked) {
        emit_event(pid, SEVERITY_CRITICAL);
        bpf_printk("FloatDetector [BLOCK]: contaminated %s", filename);
        return -EACCES;
    }

    /* 2. Whitelist — allow silencioso */
    __u8 *safe = bpf_map_lookup_elem(&float_safe_map, key);
    if (safe && *safe) {
        return 0;
    }

    /* 3. Desconocido — política configurable */
    emit_event(pid, SEVERITY_MEDIUM);
    bpf_printk("FloatDetector [UNKNOWN]: %s (pid=%d)", filename, pid);

#if FLOAT_ENFORCE_UNKNOWN
    return -EACCES;
#else
    return 0;
#endif
}

char LICENSE[] SEC("license") = "GPL";
