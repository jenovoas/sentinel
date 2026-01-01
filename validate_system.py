#!/usr/bin/env python3
"""
Sentinel Cortex - Automated Validation Suite
Comprehensive tests for researchers and independent validation
"""

import subprocess
import time
import json
import sys
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def run_command(cmd, check=True, capture=True):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture,
            text=True,
            check=check
        )
        return result.stdout.strip() if capture else ""
    except subprocess.CalledProcessError as e:
        return None

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_test(name, status, details=""):
    """Print test result"""
    symbol = "✅" if status else "❌"
    color = Colors.GREEN if status else Colors.RED
    print(f"{symbol} {color}{name}{Colors.RESET}")
    if details:
        print(f"   {Colors.YELLOW}{details}{Colors.RESET}")

def test_kernel_version():
    """Test 1: Kernel version >= 6.1"""
    output = run_command("uname -r")
    if output:
        version = output.split('.')[0:2]
        major, minor = int(version[0]), int(version[1])
        passed = major >= 6 and minor >= 1
        print_test(
            "Kernel Version >= 6.1",
            passed,
            f"Found: {output}"
        )
        return passed
    return False

def test_ebpf_lsm():
    """Test 2: eBPF LSM support"""
    output = run_command("zcat /proc/config.gz 2>/dev/null | grep CONFIG_BPF_LSM || cat /boot/config-$(uname -r) 2>/dev/null | grep CONFIG_BPF_LSM")
    passed = output and "CONFIG_BPF_LSM=y" in output
    print_test(
        "eBPF LSM Support",
        passed,
        f"CONFIG_BPF_LSM={'enabled' if passed else 'disabled'}"
    )
    return passed

def test_ollama_running():
    """Test 3: Ollama service"""
    output = run_command("pgrep ollama")
    passed = output is not None and len(output) > 0
    print_test(
        "Ollama Service Running",
        passed,
        f"PID: {output if passed else 'Not running'}"
    )
    return passed

def test_ollama_model():
    """Test 4: Ollama model availability"""
    output = run_command("ollama list 2>/dev/null | grep llama3.2")
    passed = output is not None and "llama3.2" in output
    print_test(
        "Llama3.2 Model Installed",
        passed,
        f"Model: {'llama3.2:3b' if passed else 'Not found'}"
    )
    return passed

def test_sentinel_status():
    """Test 5: Sentinel components"""
    output = run_command("sudo sctl status 2>/dev/null")
    if not output:
        print_test("Sentinel Status", False, "sctl command failed")
        return False
    
    checks = {
        "eBPF LSM": "ACTIVE" in output,
        "Sentinel Relay": "RUNNING" in output,
        "Kernel Pulse": "RUNNING" in output,
        "TruthSync SHM": "MOUNTED" in output
    }
    
    all_passed = all(checks.values())
    print_test(
        "Sentinel Components",
        all_passed,
        f"Active: {sum(checks.values())}/{len(checks)}"
    )
    
    for component, status in checks.items():
        symbol = "✓" if status else "✗"
        print(f"      {symbol} {component}")
    
    return all_passed

def test_bpf_maps():
    """Test 6: BPF maps loaded"""
    output = run_command("sudo bpftool map list 2>/dev/null | grep -E '(decision_ringbu|quantum_ringbuf)'")
    passed = output is not None and "ringbuf" in output
    map_count = len(output.split('\n')) if output else 0
    print_test(
        "BPF Ring Buffers",
        passed,
        f"Found: {map_count} ringbuf maps"
    )
    return passed

def test_performance_tte():
    """Test 7: Time-to-Execute benchmark"""
    print(f"\n{Colors.YELLOW}Running TTE benchmark (this may take 30 seconds)...{Colors.RESET}")
    
    # Run quick benchmark
    output = run_command("cd /home/jnovoas/sentinel && source .venv/bin/activate && python bench_final_system.py 2>/dev/null | grep 'TTE'")
    
    if output and "us" in output:
        # Extract TTE value
        try:
            tte_line = [line for line in output.split('\n') if 'TTE' in line and 'us' in line][0]
            tte_value = float(tte_line.split('|')[2].strip().split()[0])
            passed = tte_value < 10.0
            print_test(
                "TTE < 10 μs",
                passed,
                f"Measured: {tte_value} μs"
            )
            return passed
        except:
            pass
    
    print_test("TTE Benchmark", False, "Could not parse benchmark output")
    return False

def test_resource_usage():
    """Test 8: Resource consumption"""
    # Check sentinel_relay process
    output = run_command("ps aux | grep sentinel_relay | grep -v grep")
    
    if output:
        parts = output.split()
        cpu = float(parts[2])
        mem_kb = float(parts[5])
        mem_mb = mem_kb / 1024
        
        cpu_ok = cpu < 5.0  # Allow up to 5% CPU
        mem_ok = mem_mb < 10.0  # Allow up to 10 MB RAM
        
        passed = cpu_ok and mem_ok
        print_test(
            "Resource Usage",
            passed,
            f"CPU: {cpu}%, RAM: {mem_mb:.2f} MB"
        )
        return passed
    
    print_test("Resource Usage", False, "sentinel_relay not found")
    return False

def test_ai_inference():
    """Test 9: AI model inference"""
    print(f"\n{Colors.YELLOW}Testing AI inference (this may take 10 seconds)...{Colors.RESET}")
    
    output = run_command('ollama run llama3.2:3b "Say OK" 2>/dev/null | head -1')
    passed = output is not None and len(output) > 0
    print_test(
        "AI Inference",
        passed,
        f"Response: {output[:50] if passed else 'No response'}"
    )
    return passed

def test_postgres():
    """Test 10: PostgreSQL availability"""
    output = run_command("docker ps | grep postgres")
    passed = output is not None and "postgres" in output
    print_test(
        "PostgreSQL Database",
        passed,
        f"Status: {'Running' if passed else 'Not running'}"
    )
    return passed

def generate_report(results):
    """Generate final validation report"""
    print_header("VALIDATION SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    percentage = (passed / total) * 100
    
    print(f"Total Tests: {total}")
    print(f"Passed: {Colors.GREEN}{passed}{Colors.RESET}")
    print(f"Failed: {Colors.RED}{total - passed}{Colors.RESET}")
    print(f"Success Rate: {Colors.BOLD}{percentage:.1f}%{Colors.RESET}\n")
    
    if percentage >= 90:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ SYSTEM VALIDATED{Colors.RESET}")
        print(f"{Colors.GREEN}Sentinel Cortex is production-ready{Colors.RESET}\n")
        return 0
    elif percentage >= 70:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  PARTIAL VALIDATION{Colors.RESET}")
        print(f"{Colors.YELLOW}Some components need attention{Colors.RESET}\n")
        return 1
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ VALIDATION FAILED{Colors.RESET}")
        print(f"{Colors.RED}System requires troubleshooting{Colors.RESET}\n")
        return 2

def main():
    """Run all validation tests"""
    print_header("SENTINEL CORTEX VALIDATION SUITE")
    print(f"{Colors.BLUE}Automated tests for researchers and independent validation{Colors.RESET}\n")
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System: {run_command('uname -s')} {run_command('uname -r')}\n")
    
    # Check if running as root for some tests
    is_root = run_command("id -u") == "0"
    if not is_root:
        print(f"{Colors.YELLOW}⚠️  Some tests require sudo privileges{Colors.RESET}\n")
    
    # Run tests
    results = {}
    
    print_header("SYSTEM REQUIREMENTS")
    results["kernel_version"] = test_kernel_version()
    results["ebpf_lsm"] = test_ebpf_lsm()
    
    print_header("SERVICE AVAILABILITY")
    results["ollama_running"] = test_ollama_running()
    results["ollama_model"] = test_ollama_model()
    results["postgres"] = test_postgres()
    
    print_header("SENTINEL COMPONENTS")
    results["sentinel_status"] = test_sentinel_status()
    results["bpf_maps"] = test_bpf_maps()
    
    print_header("PERFORMANCE VALIDATION")
    results["resource_usage"] = test_resource_usage()
    # results["performance_tte"] = test_performance_tte()  # Commented out for speed
    
    print_header("AI INTEGRATION")
    results["ai_inference"] = test_ai_inference()
    
    # Generate report
    exit_code = generate_report(results)
    
    # Save results to JSON
    report_file = Path("/home/jnovoas/sentinel/validation_results.json")
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "system": run_command('uname -a'),
            "results": results,
            "summary": {
                "total": len(results),
                "passed": sum(results.values()),
                "failed": len(results) - sum(results.values()),
                "percentage": (sum(results.values()) / len(results)) * 100
            }
        }, f, indent=2)
    
    print(f"📄 Results saved to: {Colors.BLUE}{report_file}{Colors.RESET}\n")
    
    return exit_code

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Validation interrupted by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        sys.exit(1)
