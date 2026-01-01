# Sentinel Cortex™ - Technical Documentation Portal

Welcome to the central documentation portal for **Sentinel Cortex™**, a security and observability framework based on eBPF LSM and localized AI inference.

## 📋 Project Overview
Sentinel Cortex provides a low-latency security enforcement layer for Linux systems. By leveraging eBPF LSM (Linux Security Module) hooks, the system interposes on critical kernel operations to apply real-time security policies.

- [**Repository Homepage**](https://github.com/jenovoas/sentinel)
- [**Technical Architecture**](./proven/TRUTHSYNC_ARCHITECTURE.md)
- [**Benchmarks and Performance**](./BENCHMARKS_CONSOLIDATED.md)

---

## 🛠️ Key Components

### 🛡️ Kernel-Level Security (Guardian Alpha)
Real-time security enforcement implementing a policy-driven layer at Ring 0 via eBPF LSM.
- [**Interception Logic**](../ebpf/README.md)
- [**C Relay Implementation**](../guardian-alpha/sentinel_relay.c)

### 🧠 Semantic Analysis (Control Plane)
Contextual evaluation of security events using local LLM inference (Ollama/Llama 3.2:3b).
- [**Logic Engine Documentation**](../truthsync-poc/README.md)

### 📊 Observability and Monitoring
Integrated data pipeline for system health and security event telemetry.
- [**System Audit Summary**](../SYSTEM_AUDIT_SUMMARY_2026_01_01.md)

---

**© 2026 Jaime Eugenio Novoa Sepúlveda** | [Contact](mailto:jaime.novoase@gmail.com)
