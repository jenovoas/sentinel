# Sentinel BCI - Hardware Investigation & Procurement Guide

This document tracks the hardware research, specifications, and procurement status for the Sentinel Bone Conduction Interface (BCI).

---

## 🛠 Phase 0: Initial Proof-of-Concept (POC)
**Goal**: Validate bone conduction and synesthesia (qualia) hypothesis.
**Total Budget**: ~$15 - $25 USD

| Component | Specification | Recommendations | Sourcing | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Piezo Buzzer** | Active/Passive, 3V-12V, 4kHz range | PFM-12P style or similar | Amazon, Electronics shops | ⏳ Pending |
| **Microcontroller**| Arduino Uno, ESP32, or Pico | Arduino Uno R3 (Standard) | Amazon, Local hardware | ⏳ Pending |
| **Jumper Wires** | M-M, M-F set | Standard 20cm set | Amazon, Local hardware | ⏳ Pending |
| **Coupler** | Aluminum Foil / Gel | Standard Kitchen Foil | Home | ✅ Available |

---

## 🚀 Phase 1: Ultrasonic & Graphene Enhancement
**Goal**: Frequency range extension and impedance matching.
**Total Budget**: ~$200 - $350 USD

| Component | Specification | Technical Notes | Sourcing | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Ultrasonic Transducer**| 40kHz - 200kHz | Needs high-frequency driver | Specialized Industrial Supply | 🔍 Researching |
| **Graphene Sheet** | Monolayer/Multilayer Lab Grade | For acoustic impedance matching | Graphenea, Specialty Lab Suppliers| 🔍 Researching |
| **Signal Generator** | 0 - 1MHz (min) | Needs precise PWM/Analog control | FeelElec, Rigol, or custom board | 🔍 Researching |

---

## 🌌 Phase 2: Quantum-Coherent Production (153.4 MHz)
**Goal**: Matching microtubule coherence frequency.
**Total Budget**: ~$1,500 - $5,000 USD (Developmental)

### 🔍 Research Topics:
1. **PZT-5H Crystal Customization**:
   - Finding a supplier capable of cutting Lead Zirconate Titanate (PZT) to resonate exactly at 153.4 MHz.
   - Geometry: Disc vs. Plate for temporal bone contact.

2. **Graphene-Acoustic Impedance Matching**:
   - Calculating the exact number of graphene layers needed to match the acoustic impedance of the human temporal bone (~7-10 MRayls).

3. **153.4 MHz RF Driver**:
   - Designing an RF power stage capable of driving the capacitive load of a PZT crystal at 150MHz+ with low noise.

---

## 📦 Procurement Checklist

- [ ] **Week 1 (Jan 1-7)**: Order Phase 0 components.
- [ ] **Week 2 (Jan 8-14)**: Identify Graphene suppliers (Phase 1).
- [ ] **Week 3 (Jan 15-21)**: Request quotes for custom PZT crystals (Phase 2).
- [ ] **Week 4 (Jan 22-31)**: Finalize bill of materials (BOM) for the "Symbiotic Layer" headband.

---

## 🧪 Safety & Lab Notes
- Always test power output with an oscilloscope before applying to skin.
- Keep PZT voltage below 20V for initial temporal bone testing.
- Document all bone conduction threshold measurements (dB vs. Frequency).

---

**Sentinel Cortex™ BCI Division**  
*Building the bridge between silicon and soul.*
