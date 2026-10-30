# Guardian-Alpha eBPF LSM Build System

CLANG ?= clang
LLVM_STRIP ?= $(shell command -v llvm-strip-19 || command -v llvm-strip)
BPFTOOL ?= bpftool

ARCH := $(shell uname -m | sed 's/x86_64/x86/' | sed 's/aarch64/arm64/')
INCLUDES := -I/usr/include/$(ARCH)-linux-gnu

TARGET := guardian_cognitive
OBJECT := $(TARGET).o
# Sensores adicionales (auditoria por defecto, carga separada tras whitelist).
# Ver docs/AUDITORIA_EBPF_MARTE_2026-10-30.md y T-tareas eBPF.
SENSORS := ai_guardian float_detector guardian_gamma
SENSOR_OBJS := $(SENSORS:%=%.o)

.PHONY: all clean load unload test sensors

all: $(OBJECT)

sensors: $(SENSOR_OBJS)

%.o: %.c
	$(CLANG) -g -O2 -target bpf -D__TARGET_ARCH_$(ARCH) \
		$(INCLUDES) -c $< -o $@
	$(LLVM_STRIP) -g $@

$(OBJECT): $(TARGET).c
	$(CLANG) -g -O2 -target bpf -D__TARGET_ARCH_$(ARCH) \
		$(INCLUDES) -c $< -o $@
	$(LLVM_STRIP) -g $@

clean:
	rm -f $(OBJECT) $(SENSOR_OBJS)
