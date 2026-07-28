// SPDX-License-Identifier: GPL-2.0
/* Guardian-Gamma™ — Meta-Vigilance at Ring 0
 *
 * Fase 1 (kernel-side): detecta ataques ACTIVOS contra los otros Guardians
 * observando la syscall bpf() y la liberación de programas BPF peer.
 *
 * Hooks implementados:
 *   - kprobe/__sys_bpf:    detecta BPF_PROG_DETACH / BPF_LINK_DETACH
 *                          (telemetría, no bloquea — rol de vigilante)
 *   - kprobe/bpf_prog_put: detecta liberación de un prog peer registrado
 *
 * Fase 2 (userspace) añadirá: inotify de pins, correlator de ringbuffer,
 * detección de silencio QHC, watchdog de heartbeat.
 *
 * AXIOMA YATRA: Cero floats. Todo en S60 raw (SCALE_0 = 12,960,000).
 *
 * Copyright (c) 2026 Sentinel Cortex™
 */

#include "vmlinux.h"
#include <bpf/bpf_core_read.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include "cortex_events.h"

/* Comandos bpf() sensibles — valores estables en UAPI */
#define BPF_PROG_DETACH_CMD 8
#define BPF_LINK_DETACH_CMD 34

/* ─── Maps ────────────────────────────────────────────────────────────────── */

/* Ringbuffer compartido con el bridge Rust (cortex_event, 32B) */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

/* Peers conocidos: prog_id del kernel → guardian_code (1..4).
 * Poblado desde userspace (gamma_watchdog) tras load.sh.
 * Pineado para permitir actualización en caliente.
 */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 16);
    __type(key, __u32);
    __type(value, __u8);
    __uint(pinning, LIBBPF_PIN_BY_NAME);
} known_peer_prog_ids SEC(".maps");

/* Rate limiting: (event_type << 8 | guardian_code) → last_ns
 * Evita inundación del ringbuffer durante ataques ruidosos o loops.
 */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 256);
    __type(key, __u64);
    __type(value, __u64);
} rate_limit SEC(".maps");

/* Heartbeat userspace → kernel. Slot 0 = último ts_ns escrito por gamma_watchdog.
 * La Fase 2 userspace escribe aquí cada BIO_PULSE (17s).
 */
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, __u32);
    __type(value, __u64);
    __uint(pinning, LIBBPF_PIN_BY_NAME);
} gamma_heartbeat SEC(".maps");

/* ─── Helpers ─────────────────────────────────────────────────────────────── */

/* Verifica y actualiza rate limit. Retorna 1 si el evento DEBE descartarse. */
static __always_inline int
is_rate_limited(__u32 event_type, __u8 guardian_code, __u64 window_ns)
{
    __u64 key = ((__u64)event_type << 8) | (__u64)guardian_code;
    __u64 now = bpf_ktime_get_ns();
    __u64 *last = bpf_map_lookup_elem(&rate_limit, &key);

    if (last && (*last + window_ns) > now)
        return 1;

    bpf_map_update_elem(&rate_limit, &key, &now, BPF_ANY);
    return 0;
}

/* Emite un cortex_event al ringbuffer común.
 * El byte 0 de reserved[] transporta guardian_code (convención Gamma).
 */
static __always_inline void
emit_gamma(__u32 event_type, __u32 pid, __u8 guardian_code, __u8 severity)
{
    struct cortex_event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e)
        return;

    __builtin_memset(e, 0, sizeof(*e));

    e->timestamp_ns   = bpf_ktime_get_ns();
    e->event_type     = event_type;
    e->pid            = pid;
    e->entropy_signal = (__u64)guardian_code * S60_SCALE_0;
    e->severity       = severity;
    e->reserved[0]    = guardian_code;

    bpf_ringbuf_submit(e, 0);
}

/* ─── Hook 1: kprobe sobre __sys_bpf ──────────────────────────────────────── */

/* Detecta intentos de DETACH contra CUALQUIER programa BPF.
 * Deduplicación por rate_limit (ventana 1s) para no inundar.
 * Userspace correlaciona con known_peer_prog_ids para filtrar ataques reales.
 */
SEC("kprobe/__sys_bpf")
int BPF_KPROBE(gamma_sys_bpf, int cmd)
{
    if (cmd != BPF_PROG_DETACH_CMD && cmd != BPF_LINK_DETACH_CMD)
        return 0;

    /* Rate limit por cmd type, sin guardian_code (no lo sabemos desde aquí) */
    if (is_rate_limited(EVENT_GAMMA_DETACH_ATTEMPT, (__u8)cmd, 1000000000ULL))
        return 0;

    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    emit_gamma(EVENT_GAMMA_DETACH_ATTEMPT, pid, 0 /* desconocido */, SEVERITY_HIGH);
    return 0;
}

/* ─── Hook 2: kprobe sobre bpf_prog_put ───────────────────────────────────── */

/* Se dispara cuando un programa BPF es liberado (refcount → 0).
 * Si el prog_id está en known_peer_prog_ids → PEER_VANISHED (CRITICAL).
 * No bloquea — solo reporta.
 */
SEC("kprobe/bpf_prog_put")
int BPF_KPROBE(gamma_prog_put, struct bpf_prog *prog)
{
    if (!prog)
        return 0;

    __u32 id = 0;
    struct bpf_prog_aux *aux = BPF_CORE_READ(prog, aux);
    if (!aux)
        return 0;
    id = BPF_CORE_READ(aux, id);

    __u8 *code = bpf_map_lookup_elem(&known_peer_prog_ids, &id);
    if (!code)
        return 0;  /* No es un peer registrado — ignorar */

    if (is_rate_limited(EVENT_GAMMA_PEER_VANISHED, *code, 500000000ULL))
        return 0;

    emit_gamma(EVENT_GAMMA_PEER_VANISHED, 0, *code, SEVERITY_CRITICAL);
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
