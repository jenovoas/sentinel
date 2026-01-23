// SPDX-License-Identifier: GPL-2.0
// ME-60OS Cortex Events - Estructuras de Verdad Compartida
// Define el contrato de datos entre Ring 0 (Kernel) y Cortex (Userspace)

#ifndef __CORTEX_EVENTS_H__
#define __CORTEX_EVENTS_H__

typedef unsigned char __u8;
typedef unsigned int __u32;
typedef unsigned long long __u64;

// Tipos de Eventos Neuronales
#define EVENT_TYPE_EXEC  1
#define EVENT_TYPE_OPEN  2
#define EVENT_TYPE_NET   3
#define EVENT_TYPE_BIO   4  // Señal de Bio-Resonancia

// Estructura S60 para Entropía (Componentes Enteros)
struct s60_entropy_t {
    __u64 raw_value;    // Valor crudo para cálculo rápido
    __u8  degree;       // Grados (0-59)
    __u8  minute;       // Minutos (0-59)
    __u8  second;       // Segundos (0-59)
    __u8  tertia;       // Tercias (0-59)
    __u8  stability;    // 0 = Caos, 60 = Orden Perfecto
};

// Evento Principal enviado por Ring Buffer
struct cortex_event_t {
    __u64 timestamp;           // ktime_get_ns()
    __u32 pid;                 // Process ID
    __u32 type;                // EVENT_TYPE_*
    struct s60_entropy_t entropy; // Estado de entropía calculado en kernel
    char payload[64];          // Datos contextuales (filename, comm, etc)
    __u32 cpu_id;             // CPU Core donde ocurrió
};

#endif /* __CORTEX_EVENTS_H__ */
