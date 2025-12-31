CLANG ?= clang
LLVM_STRIP ?= llvm-strip-19
BPFTOOL ?= bpftool

ARCH := $(shell uname -m | sed 's/x86_64/x86/' | sed 's/aarch64/arm64/')
INCLUDES := -I. -I/usr/include/$(ARCH)-linux-gnu -I../../ebpf

TARGET := trace.bpf
OBJECT := $(TARGET).o

all: $(OBJECT)

$(OBJECT): $(TARGET).c
	$(CLANG) -g -O2 -target bpf -D__TARGET_ARCH_$(ARCH) \
		$(INCLUDES) -c $< -o $@
	$(LLVM_STRIP) -g $@

clean:
	rm -f $(OBJECT)
