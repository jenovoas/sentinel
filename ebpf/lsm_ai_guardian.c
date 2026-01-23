// SPDX-License-Identifier: GPL-2.0
// ME-60OS AI Guardian v2.0 - Ring Buffer Integrated
// Ring 0 -> Cortex Telemetry Channel

#include <linux/bpf.h>
#include <linux/fs.h>
#include <linux/path.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include "cortex_events.h"

#define PATH_MAX 256
#define ALLOW_AI 1
#define BLOCK_AI 0

// Mapa de Ring Buffer para eventos de alta velocidad (256KB)
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} cortex_ringbuf SEC(".maps");

// Whitelist y Mapas de Control (Legacy v1.0 preservado)
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, __u32);
    __type(value, __u8);
} ai_agents SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10000);
    __type(key, char[PATH_MAX]);
    __type(value, __u64);
} ai_whitelist SEC(".maps");

// Función auxiliar: Cálculo de Entropía S60 (Determinista)
static __always_inline void calculate_s60_entropy(struct s60_entropy_t *e, __u64 seed) {
    // Usamos el timestamp/seed para generar componentes base-60
    // Lógica: seed % 60 para cada componente
    
    e->raw_value = seed;
    
    // División entera simulada para componentes
    // Nota: El verificador puede quejarse si usamos % con variables no const.
    // Usamos aritmética simple para "simular" extracción de dígitos S60
    
    unsigned long long val = seed;
    
    // Seconds
    e->second = val % 60;
    val /= 60;
    
    // Minutes
    e->minute = val % 60;
    val /= 60;
    
    // Degrees
    e->degree = val % 60;
    
    // Tertia (Sub-second precision)
    e->tertia = (seed >> 4) % 60; 
    
    // Stability calculation (arbitrary deterministic metric)
    e->stability = (e->degree + e->minute + e->second) % 60;
}

// Helper para enviar evento
static __always_inline void emit_cortex_event(void *ctx, __u32 type, char *data, __u32 pid) {
    struct cortex_event_t *event;
    
    // Reservar espacio en Ring Buffer
    event = bpf_ringbuf_reserve(&cortex_ringbuf, sizeof(*event), 0);
    if (!event) {
        return; // Ring buffer lleno o error
    }
    
    // Poblar datos
    event->timestamp = bpf_ktime_get_ns();
    event->pid = pid;
    event->type = type;
    event->cpu_id = bpf_get_smp_processor_id();
    
    // Copiar payload (seguro)
    __builtin_memcpy(event->payload, data, sizeof(event->payload));
    
    // Calcular Entropía Local
    calculate_s60_entropy(&event->entropy, event->timestamp);
    
    // Enviar a Cortex
    bpf_ringbuf_submit(event, 0);
}

// LSM Hook: file_open
SEC("lsm/file_open")
int BPF_PROG(ai_guardian_open, struct file *file)
{
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    char path[PATH_MAX];
    __u8 *is_ai = bpf_map_lookup_elem(&ai_agents, &pid);
    
    // Telemetría para TODOS los procesos si es crítico, 
    // pero por ahora filtramos solo lo interesante o AI
    
    // Obtener path
    long ret = bpf_d_path(&file->f_path, path, sizeof(path));
    if (ret < 0) return 0;
    
    // Si es AI agent, aplicar Whitelist (Lógica v1.0)
    if (is_ai && *is_ai == 1) {
         __u64 *policy = bpf_map_lookup_elem(&ai_whitelist, path);
         if (!policy || *policy != ALLOW_AI) {
             // Bloqueo y Evento de Seguridad
             emit_cortex_event(file, EVENT_TYPE_OPEN, path, pid);
             return -EPERM;
         }
    }
    
    // Si NO es bloqueo, enviamos evento muestreado (ej: cada N eventos) 
    // para alimentar la red neuronal del Cortex con "normalidad".
    // Por simplicidad, enviamos todo para AI agents.
    if (is_ai) {
        emit_cortex_event(file, EVENT_TYPE_OPEN, path, pid);
    }
    
    return 0;
}

// LSM Hook: bprm_check_security (Exec)
SEC("lsm/bprm_check_security")
int BPF_PROG(ai_guardian_exec, struct linux_binprm *bprm)
{
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    char path[PATH_MAX];
    
    long ret = bpf_probe_read_kernel_str(path, sizeof(path), bprm->filename);
    if (ret < 0) return 0;
    
    // Siempre reportar ejecuciones al Cortex (alta prioridad)
    emit_cortex_event(bprm, EVENT_TYPE_EXEC, path, pid);
    
    // Lógica de Bloqueo para AI Agents
    __u8 *is_ai = bpf_map_lookup_elem(&ai_agents, &pid);
    if (is_ai && *is_ai == 1) {
         __u64 *policy = bpf_map_lookup_elem(&ai_whitelist, path);
         if (!policy || *policy != ALLOW_AI) {
             return -EPERM;
         }
    }
    
    return 0;
}

char LICENSE[] SEC("license") = "GPL";