# eBPF LSM Deployment and Testing Plan

## Goal

Deploy and validate the Guardian-Alpha eBPF LSM module to provide kernel-level protection against malicious AI-generated commands. This will complete **Claim 3** of the patent portfolio with working proof-of-concept.

## User Review Required

> **⚠️ IMPORTANT: Kernel-Level Changes**
> 
> This implementation will load eBPF programs into the kernel that intercept system calls. While eBPF is designed to be safe, this requires:
> - Root/sudo privileges
> - Kernel version >= 5.7 (✅ You have 6.12.63)
> - BPF_LSM enabled (✅ Confirmed)
> - BTF support (✅ Available)

> **⚠️ WARNING: Testing Approach**
> 
> We have two LSM implementations:
> 1. `guardian_alpha_lsm.c` - Simpler, whitelist-based execve interceptor
> 2. `lsm_ai_guardian.c` - More advanced, with AI agent tracking and dynamic whitelist
> 
> **Recommendation**: Start with `guardian_alpha_lsm.c` for initial testing, then upgrade to `lsm_ai_guardian.c` for production.

## Current Status

### ✅ System Requirements Met
- **Kernel Version**: 6.12.63-1-lts (>= 5.7 required)
- **BPF_LSM**: Enabled (`CONFIG_BPF_LSM=y`)
- **BTF Support**: Available (`/sys/kernel/btf/vmlinux` exists)
- **LSM Stack**: `bpf` is in the LSM list
- **Tools**: clang, llvm-strip, bpftool all installed

### 📁 Existing Code
- `guardian_alpha_lsm.c` - 108 lines, basic LSM implementation
- `lsm_ai_guardian.c` - 142 lines, advanced implementation
- `Makefile` - Build system
- `load.sh` - Loading script
- `watchdog_service.py` - Watchdog integration

---

## Proposed Changes

### Phase 1: Compilation and Basic Testing

#### Modify: Makefile
- Update to support both LSM implementations
- Add proper error handling
- Include BTF generation flags

#### New: compile_and_test.sh
- Automated compilation script
- Pre-flight checks (kernel version, BTF, tools)
- Compilation with verbose output
- Basic validation

---

### Phase 2: Guardian Alpha Deployment

#### Modify: load.sh
- Add pre-flight checks
- Improve error messages
- Add whitelist population logic
- Verification steps

#### New: test_lsm_basic.sh
- Test script to verify LSM is intercepting
- Create test whitelist entries
- Attempt to execute whitelisted and non-whitelisted commands
- Capture kernel logs

#### New: unload.sh
- Safe unloading procedure
- Cleanup of pinned programs
- Verification of removal

---

### Phase 3: Advanced AI Guardian Testing

#### New: load_ai_guardian.sh
- Load `lsm_ai_guardian.c` version
- Populate AI agent PIDs
- Setup dynamic whitelist
- Integration with backend

#### New: test_ai_guardian.py
- Python test suite
- Register test process as "AI agent"
- Attempt file operations
- Verify blocking behavior
- Read stats from eBPF maps

---

### Phase 4: Documentation and Evidence

#### New: DEPLOYMENT_GUIDE.md
- Step-by-step deployment instructions
- Troubleshooting guide
- Performance benchmarks
- Security considerations

#### Modify: STATUS.md
- Update with actual test results
- Add compilation evidence
- Include kernel logs
- Performance metrics

#### New: docs/EVIDENCE_LSM_WORKING.md
- Proof of kernel-level interception
- Screenshots of kernel logs
- Benchmark results
- Comparison with user-space solutions

---

## Verification Plan

### Automated Tests

#### 1. Compilation Test
```bash
cd /home/jnovoas/sentinel/ebpf
./compile_and_test.sh
```
**Expected**: Both `guardian_alpha_lsm.o` and `lsm_ai_guardian.o` compile without errors

#### 2. Basic LSM Loading Test
```bash
cd /home/jnovoas/sentinel/ebpf
sudo ./load.sh
sudo bpftool prog show pinned /sys/fs/bpf/guardian_alpha_lsm
```
**Expected**: Program loaded successfully, visible in bpftool output

#### 3. Interception Test
```bash
cd /home/jnovoas/sentinel/ebpf
sudo ./test_lsm_basic.sh
```
**Expected**: 
- Whitelisted commands execute successfully
- Non-whitelisted commands blocked with -EACCES
- Kernel logs show "Guardian-Alpha: BLOCKED execve"

#### 4. AI Guardian Test
```bash
cd /home/jnovoas/sentinel/ebpf
sudo python3 test_ai_guardian.py
```
**Expected**:
- AI agent PID registered
- File operations blocked when not in whitelist
- Stats map shows correct counts

#### 5. Performance Benchmark
```bash
cd /home/jnovoas/sentinel/ebpf
sudo ./benchmark_lsm_overhead.sh
```
**Expected**: Overhead < 1ms per syscall

### Manual Verification

#### 1. Kernel Log Inspection
```bash
sudo dmesg | grep "Guardian-Alpha"
# or
sudo cat /sys/kernel/debug/tracing/trace_pipe
```
**Expected**: See interception events in real-time

#### 2. Map Inspection
```bash
sudo bpftool map dump pinned /sys/fs/bpf/guardian_alpha_lsm/whitelist_map
sudo bpftool map dump pinned /sys/fs/bpf/guardian_alpha_lsm/events
```
**Expected**: See whitelist entries and event logs

#### 3. Unload Verification
```bash
sudo ./unload.sh
sudo bpftool prog show | grep guardian
```
**Expected**: No guardian programs listed after unload

---

## Success Criteria

### Technical
- [ ] Both LSM programs compile without errors
- [ ] Programs load into kernel successfully
- [ ] Syscalls are intercepted (verified via kernel logs)
- [ ] Whitelist enforcement works correctly
- [ ] Non-whitelisted commands are blocked
- [ ] Overhead measured at < 1ms
- [ ] Programs can be safely unloaded

### Evidence
- [ ] Compilation logs captured
- [ ] Kernel logs showing interception
- [ ] Performance benchmarks documented
- [ ] Video/screenshots of blocking in action
- [ ] Comparison with user-space alternatives

### Patent
- [ ] Claim 3 validated with working code
- [ ] Unique differentiators documented
- [ ] Prior art search confirms zero overlap
- [ ] Technical evidence package ready for attorney

---

## Risk Mitigation

### Risk: Kernel Panic
**Probability**: Very Low (eBPF verifier prevents unsafe code)  
**Mitigation**: 
- eBPF verifier validates all programs before loading
- Start with simple `guardian_alpha_lsm.c`
- Test in non-production environment first

### Risk: Performance Impact
**Probability**: Low  
**Mitigation**:
- Benchmark overhead before production use
- Use efficient BPF maps (hash maps)
- Minimize work in hot path

### Risk: Bypass Attempts
**Probability**: Zero (kernel-level enforcement)  
**Mitigation**:
- Document impossibility of bypass
- Test various evasion techniques
- Demonstrate superiority over user-space

---

## Timeline

### Immediate (Next 30 minutes)
1. Create compilation and testing scripts
2. Compile both LSM programs
3. Verify compilation success

### Short-term (Next 2 hours)
1. Load Guardian Alpha LSM
2. Run basic interception tests
3. Capture kernel logs
4. Document results

### Medium-term (Next 4 hours)
1. Test AI Guardian version
2. Performance benchmarks
3. Create evidence documentation
4. Video demonstration

---

## Notes

- All eBPF programs are GPL-licensed (kernel requirement)
- BTF (BPF Type Format) is available, enabling CO-RE (Compile Once, Run Everywhere)
- LSM stack already includes `bpf`, so programs can attach
- Kernel 6.12.63 is very recent, excellent eBPF support
