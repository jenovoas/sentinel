#include <linux/bpf.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Uso: %s <prog_path> <link_path>\n", argv[0]);
        return 1;
    }
    const char *prog_path = argv[1];
    const char *link_path = argv[2];

    // Obtener FD del programa pineado via syscall
    union bpf_attr_get {
        __u32 pathname;
        __u32 bpf_fd;
    };
    
    int prog_fd = syscall(__NR_bpf, BPF_OBJ_GET, prog_path, strlen(prog_path) + 1);
    
    // Alternativa: bpf_obj_get via syscall directa
    // Primero intentamos con BPF_OBJ_GET
    {
        char path[256];
        strncpy(path, prog_path, 255);
        path[255] = 0;
        
        union {
            struct { __aligned_u64 pathname; __u32 bpf_fd; __u32 file_flags; } attr;
            char buf[256];
        } u;
        memset(&u, 0, sizeof(u));
        u.attr.pathname = (__aligned_u64)path;
        
        int fd = syscall(__NR_bpf, BPF_OBJ_GET, &u, sizeof(u.attr));
        if (fd < 0) {
            fprintf(stderr, "ERROR: BPF_OBJ_GET '%s': %d\n", prog_path, errno);
            return 1;
        }
        prog_fd = fd;
    }

    // Crear link via syscall
    {
        struct {
            struct bpf_link_create_opts {
                __aligned_u64 sz;
                __u32 flags;
                __u32 target_btf_id;
                __aligned_u64 iter_info;
                __u32 iter_info_len;
                __u32 target_btf_obj_id;
                __u32 target_btf_type_id;
                __u32 uprobe_offset;
                __u32 uprobe_pid;
                __u64 uprobe_flags;
                __u64 uprobe_abs_path;
            } opts;
            char reserved[256];
        } attr;
        memset(&attr, 0, sizeof(attr));
        attr.opts.sz = sizeof(attr.opts);

        int link_fd = syscall(__NR_bpf, BPF_LINK_CREATE, &attr,
            sizeof(attr.opts));
        // No funciona asi, mejor con bpf_link_create de libbpf pero con opts correctos
    }

    fprintf(stderr, "Usar bpf_link_create de libbpf con opts.size correcto\n");
    return 1;
}
