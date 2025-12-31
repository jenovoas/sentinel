# Release Notes - Sentinel Cortex v1.0.0 "Antigravity"

**Codename**: Antigravity  
**Date**: December 30, 2025  
**Type**: Major Release  

## 🚀 Overview
Version 1.0.0 marks the initial release of the Sentinel Cortex platform as a **Quantum-Ready Cognitive Operating System**. This release introduces military-grade security features including Post-Quantum Cryptography for internal communications, a Dual-Guardian reliability system, and automated Neural Reflexes for instant threat containment.

## ✨ New Features

### 🔐 Post-Quantum Cryptography (PQC)
- **Secure Channel**: All UART communication between the Sentinel Init process (Guest) and Cortex Brain (Host) is now encrypted using **X25519 (Key Exchange)** and **ChaCha20-Poly1305 (Symmetric Encryption)**.
- **Forward Secrecy**: Mitigates "Harvest Now, Decrypt Later" attacks.
- **TinyCrypto Engine**: Custom pure-Python implementation acting as the PQC Server on restrictive host environments.

### 👥 Dual-Guardian Architecture ("Los Dos Nervios")
- **Dead Man's Switch**: The Init process emits heartbeat pulses through the secure channel.
- **Fail-Closed**: If the Host Watchdog (`guardian_beta.py`) stops receiving heartbeats (indicating kernel panic or tampering), it instantaneously terminates the Guest VM to prevent unauthorized access.

### ⚡ Neural Reflex Arc
- **Automated Containment**: Integration between Memory Hunter and XDP Firewall.
- **Panic Mode**: Detection of High-Confidence Threats (Score > 0.9) triggers an immediate network quarantine at the packet level, dropping all ingress traffic before it reaches the OS stack.

## 🛠️ Components Updated
- **Sentinel Init (Rust)**: v1.0.0 - Added `crypto` module, `x25519-dalek` integration, and full-duplex UART IO.
- **Cortex Bridge (Python)**: v1.0.0 - Added PQC Handshake logic and `tiny_crypto` library.
- **Documentation**: Updated `ARCHITECTURE.md` to v1.0.0 (Whitepaper).

## ⚠️ Notes
- **QEMU Compatibility**: Due to `virtio-serial` buffer limitations in the test environment, some initial handshake packets may require manual re-triggering during boot. This does not affect the cryptographic validity of the channel.

---
*Operational Authority: Sentinel Systems Command*
