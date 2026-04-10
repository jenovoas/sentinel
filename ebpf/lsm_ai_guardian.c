// SPDX-License-Identifier: GPL-2.0
// Sentinel AI Guardian - LSM Hook con Whitelist Dinámica
// Bloquea syscalls destructivas ANTES de ejecución (Ring 0)

#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#define PATH_MAX 256
#define ALLOW_AI 1
#define BLOCK_AI 0

// Mapa de PIDs de AI agents (actualizable desde userspace)
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, __u32);    // PID
    __type(value, __u8);   // 1 = AI agent, 0 = normal
} ai_agents SEC(".maps");

// Whitelist dinámica de paths (actualizable sin reboot)
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10000);
    __type(key, char[PATH_MAX]);  // Path completo
    __type(value, __u64);         // Policy ID (ALLOW_AI, BLOCK_AI)
} ai_whitelist SEC(".maps");

// Stats de bloqueos
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 3);
    __type(key, __u32);
    __type(value, __u64);
} stats SEC(".maps");

#define STAT_CHECKS 0
#define STAT_BLOCKS 1
#define STAT_ALLOWS 2

// LSM Hook: file_open
// Se ejecuta ANTES de que kernel abra archivo
SEC("lsm/file_open")
int BPF_PROG(ai_guardian_open, struct file *file)
{
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u8 *is_ai;
    char path[PATH_MAX];
    __u64 *policy;
    __u32 key;
    __u64 *count;
    
    // 1. Verificar si es AI agent
    is_ai = bpf_map_lookup_elem(&ai_agents, &pid);
    if (!is_ai || *is_ai == 0) {
        // No es AI, permitir
        return 0;
    }
    
    // 2. Obtener path del archivo
    bpf_d_path(&file->f_path, path, sizeof(path));
    
    // 3. Verificar whitelist DINÁMICA
    policy = bpf_map_lookup_elem(&ai_whitelist, path);
    
    // 4. Incrementar stats
    key = STAT_CHECKS;
    count = bpf_map_lookup_elem(&stats, &key);
    if (count) __sync_fetch_and_add(count, 1);
    
    // 5. Decisión determinista
    if (!policy || *policy != ALLOW_AI) {
        // Path NO en whitelist o explícitamente bloqueado
        key = STAT_BLOCKS;
        count = bpf_map_lookup_elem(&stats, &key);
        if (count) __sync_fetch_and_add(count, 1);
        
        // Log evento bloqueado (visible en /sys/kernel/debug/tracing/trace_pipe)
        bpf_printk("AI_GUARDIAN: BLOCKED file_open pid=%d path=%s", pid, path);
        
        return -EPERM;  // Operation not permitted
    }
    
    // Permitir (en whitelist)
    key = STAT_ALLOWS;
    count = bpf_map_lookup_elem(&stats, &key);
    if (count) __sync_fetch_and_add(count, 1);
    
    return 0;
}

// LSM Hook: bprm_check_security
// Se ejecuta ANTES de que kernel ejecute binario
SEC("lsm/bprm_check_security")
int BPF_PROG(ai_guardian_exec, struct linux_binprm *bprm)
{
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u8 *is_ai;
    char path[PATH_MAX];
    __u64 *policy;
    __u32 key;
    __u64 *count;
    
    // 1. Verificar si es AI agent
    is_ai = bpf_map_lookup_elem(&ai_agents, &pid);
    if (!is_ai || *is_ai == 0) {
        return 0;
    }
    
    // 2. Obtener path del binario
    bpf_probe_read_kernel_str(path, sizeof(path), bprm->filename);
    
    // 3. Verificar whitelist DINÁMICA
    policy = bpf_map_lookup_elem(&ai_whitelist, path);
    
    // 4. Stats
    key = STAT_CHECKS;
    count = bpf_map_lookup_elem(&stats, &key);
    if (count) __sync_fetch_and_add(count, 1);
    
    // 5. Decisión determinista
    if (!policy || *policy != ALLOW_AI) {
        key = STAT_BLOCKS;
        count = bpf_map_lookup_elem(&stats, &key);
        if (count) __sync_fetch_and_add(count, 1);
        
        bpf_printk("AI_GUARDIAN: BLOCKED exec pid=%d binary=%s", pid, path);
        
        return -EPERM;
    }
    
    key = STAT_ALLOWS;
    count = bpf_map_lookup_elem(&stats, &key);
    if (count) __sync_fetch_and_add(count, 1);
    
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
