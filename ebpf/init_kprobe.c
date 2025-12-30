#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

SEC("kprobe/do_execve")
int sentinel_init(struct pt_regs *ctx) {
    // No-op: placeholder for init PID1 supervision
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
