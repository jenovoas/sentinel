# Sentinel eBPF Build System
# Covers all kernel programs (LSM/XDP/TC/kprobe) and userspace utilities

CLANG     ?= clang
CC        ?= gcc
LLVM_STRIP ?= llvm-strip
BPFTOOL   ?= bpftool

ARCH := $(shell uname -m | sed 's/x86_64/x86/' | sed 's/aarch64/arm64/')

CFLAGS_BPF  := -g -O2 -target bpf -D__TARGET_ARCH_$(ARCH) \
               -I/usr/include/$(ARCH)-linux-gnu -I.
CFLAGS_USER := -g -O2 -Wall -I/usr/include/$(ARCH)-linux-gnu -I.
LIBS_BPF    := -lbpf -lelf -lz

# ─── Kernel programs ──────────────────────────────────────────────────────────
LSM_OBJS := guardian_alpha_lsm.o lsm_ai_guardian.o ai_guardian.o guardian_cognitive.o float_detector.o
XDP_OBJS := burst_sensor.o xdp_firewall.o
TC_OBJS  := tc_firewall.o
KPROBE_OBJS := init_kprobe.o

ALL_BPF_OBJS := $(LSM_OBJS) $(XDP_OBJS) $(TC_OBJS) $(KPROBE_OBJS)

# ─── Userspace binaries ───────────────────────────────────────────────────────
BPF_BINS  := event_monitor loader lsm_loader lsm_attach attacher
MISC_BINS := benchmark_exec

ALL_BINS := $(BPF_BINS) $(MISC_BINS)

# ─── Targets ──────────────────────────────────────────────────────────────────
.PHONY: all clean load-all unload-all load-lsm load-xdp test

all: $(ALL_BPF_OBJS) $(ALL_BINS)

# Kernel BPF objects (generic rule)
%.o: %.c
	$(CLANG) $(CFLAGS_BPF) -c $< -o $@
	$(LLVM_STRIP) -g $@

# Userspace binaries with libbpf
$(BPF_BINS): %: %.c
	$(CC) $(CFLAGS_USER) $< -o $@ $(LIBS_BPF)

# Userspace binary without libbpf
benchmark_exec: benchmark_exec.c
	$(CC) $(CFLAGS_USER) $< -o $@

# ─── Load / Unload ────────────────────────────────────────────────────────────
load-lsm: $(LSM_OBJS)
	sudo $(BPFTOOL) prog load guardian_alpha_lsm.o  /sys/fs/bpf/guardian_alpha_lsm  type lsm
	sudo $(BPFTOOL) prog load lsm_ai_guardian.o     /sys/fs/bpf/lsm_ai_guardian     type lsm
	sudo $(BPFTOOL) prog load ai_guardian.o         /sys/fs/bpf/ai_guardian         type lsm
	sudo $(BPFTOOL) prog load guardian_cognitive.o  /sys/fs/bpf/guardian_cognitive  type lsm
	sudo $(BPFTOOL) prog load float_detector.o      /sys/fs/bpf/float_detector      type lsm

load-xdp: $(XDP_OBJS)
	sudo ip link set dev eth0 xdp obj burst_sensor.o  sec xdp
	sudo ip link set dev eth0 xdp obj xdp_firewall.o  sec xdp

load-tc: $(TC_OBJS)
	sudo tc qdisc add dev eth0 clsact 2>/dev/null || true
	sudo tc filter add dev eth0 ingress bpf da obj tc_firewall.o sec tc

load-all: load-lsm load-xdp load-tc

unload-lsm:
	sudo rm -f /sys/fs/bpf/guardian_alpha_lsm \
	           /sys/fs/bpf/lsm_ai_guardian    \
	           /sys/fs/bpf/ai_guardian         \
	           /sys/fs/bpf/guardian_cognitive  \
	           /sys/fs/bpf/float_detector

unload-xdp:
	sudo ip link set dev eth0 xdp off 2>/dev/null || true

unload-tc:
	sudo tc qdisc del dev eth0 clsact 2>/dev/null || true

unload-all: unload-lsm unload-xdp unload-tc

# ─── Misc ─────────────────────────────────────────────────────────────────────
clean:
	rm -f $(ALL_BPF_OBJS) $(ALL_BINS)

test:
	./test_intercept.sh
