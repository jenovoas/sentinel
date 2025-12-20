# Guardian-Alpha eBPF LSM Build System

CLANG ?= clang
LLVM_STRIP ?= llvm-strip
BPFTOOL ?= bpftool

ARCH := $(shell uname -m | sed 's/x86_64/x86/' | sed 's/aarch64/arm64/')
INCLUDES := -I/usr/include/$(ARCH)-linux-gnu

TARGET := guardian_alpha_lsm
OBJECT := $(TARGET).o

.PHONY: all clean load unload test

all: $(OBJECT)

$(OBJECT): $(TARGET).c
	$(CLANG) -g -O2 -target bpf -D__TARGET_ARCH_$(ARCH) \
		$(INCLUDES) -c $< -o $@
	$(LLVM_STRIP) -g $@

clean:
	rm -f $(OBJECT)

load: $(OBJECT)
	sudo $(BPFTOOL) prog load $(OBJECT) /sys/fs/bpf/$(TARGET) \
		type lsm

unload:
	sudo rm -f /sys/fs/bpf/$(TARGET)

test:
	./test_intercept.sh
