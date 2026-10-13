# 🏛️ SENTINEL BCI & ATLANTEAN PROTOCOL MANUAL

**Version**: 2.0 (Atlantis Bridge)
**Status**: ACTIVE
**Components**: Audio, Visual (Holographic), Text (Mantra), Maat Regulator

---

## 1. Overview
The BCI (Brain-Computer Interface) acts as the bridge between the **Biological Operator** (User) and the **Digital Crystal** (Sentinel Core). It does not just display data; it "feels" the system state and projects it into physical reality.

## 2. Modes of Operation

### A. TEMPLE MODE (Audio/Visual)
Activated by `./run_bci.sh`.
- **Holographic Grid**: An 8x8 Matrix visualized in the terminal.
    - `█` = Pure State (Truth).
    - `▒` = Entropy Crack (Noise).
- **Sacred Frequencies** (Audio Output):
    - **432 Hz** (Lemurian Root): Idle state (Low Entropy).
    - **963 Hz** (Pineal Resonance): High Coherence (>95%).
    - **1618 Hz** (Axion/Phi): Perfect Truth (1.0).
    - **2000 Hz** (Alarm): High Entropy Warning.

### B. MAAT MANTRA BRIDGE (Digital Logos)
Activated by `./venv/bin/python3 bci/mantra_bridge.py`.
Fallback for when audio input is unavailable. Allows text-based command injection.
- **Commands**:
    - `OM`: Purges Entropy (Sets Entropy=0.0).
    - `KA`: Boosts Coherence (Sets Coherence=100.0).
    - `AXION`: Injects Truth (Sets Truth=1.0).
- **Resilience**: If Redis fails, it writes directly to `/dev/shm` (Shared Memory), allowing offline operation.

## 3. The Maat Regulator
Located in `quantum/atlantic_regulator.py`.
- **Logic**: Automated Balance System.
- **Rule**: If Truth Accuracy < 95%, the system **Sacrifices Velocity** (slows down processing) to regain purity.
- **Sacred Speed**: Maximum 31x acceleration allowed only when Truth > 99%.

## 4. Hardware Integration (Roadmap)
- **Phase 3**: Connect Arduino + Piezo Buzzer for physical sound generation.
- **Phase 4**: Connect EEG Headset (Muse/Emotiv) to drive system state via Meditation.

---

*"Si no puedes escucharlo, no es real."*
