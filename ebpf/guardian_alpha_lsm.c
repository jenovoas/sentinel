// SPDX-License-Identifier: GPL-2.0
/* Guardian-Alpha™ LSM - Kernel-Level AI Safety Enforcement
 *
 * Claim 3: Kernel-level protection via eBPF LSM hooks with
 * path-based whitelist and pre-execution veto.
 *
 * Semántica:
 *   - Solo intercepta execve si el PID está marcado como AI agent
 *     en alpha_ai_agents. Procesos normales pasan libremente.
 *   - Clave del whitelist = path del binario (char[256], null-padded),
 *     consistente con populate_whitelist.sh.
 *
 * Copyright (c) 2024-2026 Sentinel Cortex™
 */

#include "vmlinux.h"
#include <bpf/bpf_core_read.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#ifndef EACCES
#define EACCES 13
#endif
#ifndef PATH_MAX
#define PATH_MAX 256
#endif

/* Whitelist map: path (char[256]) -> allowed (1) o blocked (0)
 * Pre-poblado por populate_whitelist.sh y pineado en
 * /sys/fs/bpf/sentinel/whitelist_map. El loader lo ata con:
 *   bpftool prog load ... map name whitelist_map pinned <pin>
 */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10000);
    __type(key, char[PATH_MAX]);
    __type(value, __u8);
} whitelist_map SEC(".maps");

/* AI agents marcados desde userspace. Sin entrada = proceso normal
 * = Alpha no interviene. */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, __u32);
    __type(value, __u8);
} alpha_ai_agents SEC(".maps");

/* Ring buffer para audit trail */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

struct event {
    __u32 pid;
    __u32 uid;
    char path[PATH_MAX];
    __u8 action;      /* 0 = blocked, 1 = allowed */
    __u64 timestamp;
};

static __always_inline void log_event(__u32 pid, __u32 uid,
                                      const char *path, __u8 action)
{
    struct event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e)
        return;

    e->pid = pid;
    e->uid = uid;
    e->action = action;
    e->timestamp = bpf_ktime_get_ns();
    __builtin_memcpy(e->path, path, PATH_MAX);

    bpf_ringbuf_submit(e, 0);
}

SEC("lsm/bprm_check_security")
int BPF_PROG(guardian_execve, struct linux_binprm *bprm)
{
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
    __u8 *is_ai;
    __u8 *allowed;
    char path[PATH_MAX] = {};

    /* 1. Passthrough para procesos no-AI — YATRA: no contaminamos el resto */
    is_ai = bpf_map_lookup_elem(&alpha_ai_agents, &pid);
    if (!is_ai || *is_ai == 0)
        return 0;

    /* 2. Extraer path real del binario desde bprm->file->f_path */
    bpf_d_path(&bprm->file->f_path, path, sizeof(path));

    /* 3. Consultar whitelist */
    allowed = bpf_map_lookup_elem(&whitelist_map, path);
    if (!allowed || *allowed != 1) {
        log_event(pid, uid, path, 0);
        bpf_printk("Guardian-Alpha: BLOCKED execve pid=%d path=%s", pid, path);
        return -EACCES;
    }

    log_event(pid, uid, path, 1);
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
