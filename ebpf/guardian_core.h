/* Guardian Core Definitions - Minimal Kernel Headers for BPF CO-RE */
#ifndef __GUARDIAN_CORE_H__
#define __GUARDIAN_CORE_H__

/* 1. Basic Types */
typedef unsigned char __u8;
typedef unsigned short __u16;
typedef unsigned int __u32;
typedef unsigned long long __u64;
typedef signed char __s8;
typedef signed short __s16;
typedef signed int __s32;
typedef signed long long __s64;

typedef __u8 u8;
typedef __u16 u16;
typedef __u32 u32;
typedef __u64 u64;

typedef __u16 __be16;
typedef __u32 __be32;
typedef __u32 __wsum;

/* 2. Kernel Structures (Minimal Stub) */

/* struct linux_binprm: Binary parameter structure used in execve */
struct linux_binprm {
    char buf[128];
    void *vma;
    unsigned long vma_pages;
    void *mm;
    unsigned long p;
    unsigned long argmin;
    unsigned int
        cred_prepared: 1,
        cap_effective: 1;
    void *file;     /* struct file *file */
    void *cred;     /* struct cred *cred */
    int unsafe;
    unsigned int per_clear;
    int argc;
    int envc;
    const char *filename; /* Point of interest */
};

/* 3. BPF Constants */
enum bpf_map_type {
    BPF_MAP_TYPE_UNSPEC,
    BPF_MAP_TYPE_HASH,
    BPF_MAP_TYPE_ARRAY,
    BPF_MAP_TYPE_PROG_ARRAY,
    BPF_MAP_TYPE_PERF_EVENT_ARRAY,
    BPF_MAP_TYPE_PERCPU_HASH,
    BPF_MAP_TYPE_PERCPU_ARRAY,
    BPF_MAP_TYPE_STACK_TRACE,
    BPF_MAP_TYPE_CGROUP_ARRAY,
    BPF_MAP_TYPE_LRU_HASH,
    BPF_MAP_TYPE_LRU_PERCPU_HASH,
    BPF_MAP_TYPE_LPM_TRIE,
    BPF_MAP_TYPE_ARRAY_OF_MAPS,
    BPF_MAP_TYPE_HASH_OF_MAPS,
    BPF_MAP_TYPE_DEVMAP,
    BPF_MAP_TYPE_SOCKMAP,
    BPF_MAP_TYPE_CPUMAP,
    BPF_MAP_TYPE_XSKMAP,
    BPF_MAP_TYPE_SOCKHASH,
    BPF_MAP_TYPE_CGROUP_STORAGE,
    BPF_MAP_TYPE_REUSEPORT_SOCKARRAY,
    BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE,
    BPF_MAP_TYPE_QUEUE,
    BPF_MAP_TYPE_STACK,
    BPF_MAP_TYPE_SK_STORAGE,
    BPF_MAP_TYPE_DEVMAP_HASH,
    BPF_MAP_TYPE_STRUCT_OPS,
    BPF_MAP_TYPE_RINGBUF,
    BPF_MAP_TYPE_INODE_STORAGE,
};

#ifndef EACCES
#define EACCES 13
#endif

#endif /* __GUARDIAN_CORE_H__ */