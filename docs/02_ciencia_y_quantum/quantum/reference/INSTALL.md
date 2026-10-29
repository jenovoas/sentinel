# Installation Instructions for Sentinel Quantum Simulators

## Quick Install (Recommended)

```bash
# Navigate to sentinel directory
cd /home/jnovoas/sentinel

# Install Python dependencies
pip install --user numpy scipy matplotlib psutil

# Verify installation
python3 -c "import numpy, scipy, matplotlib, psutil; print('✅ All dependencies installed!')"

# Run test suite
cd quantum
python3 test_simulators.py

# Run demo
python3 quantum_lite.py
```

## Alternative: Virtual Environment (Cleaner)

```bash
# Create virtual environment
cd /home/jnovoas/sentinel
python3 -m venv venv_quantum

# Activate
source venv_quantum/bin/activate

# Install dependencies
pip install numpy scipy matplotlib psutil

# Run tests
cd quantum
python3 test_simulators.py

# When done, deactivate
deactivate
```

## Troubleshooting

### If pip is not installed
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-pip

# Fedora/RHEL
sudo dnf install python3-pip

# Arch
sudo pacman -S python-pip
```

### If installation fails due to permissions
```bash
# Use --user flag
pip install --user numpy scipy matplotlib psutil
```

### If you want system-wide install
```bash
# With sudo (not recommended)
sudo pip install numpy scipy matplotlib psutil
```

## Verify Installation

```bash
cd /home/jnovoas/sentinel/quantum
python3 << EOF
import numpy as np
import scipy
import matplotlib
import psutil

print("✅ NumPy:", np.__version__)
print("✅ SciPy:", scipy.__version__)
print("✅ Matplotlib:", matplotlib.__version__)
print("✅ psutil:", psutil.__version__)
print("\n🎉 All dependencies ready!")
EOF
```

## Next Steps After Installation

1. Run test suite:
   ```bash
   python3 test_simulators.py
   ```

2. Run demo:
   ```bash
   python3 quantum_lite.py
   ```

3. Explore interactively:
   ```python
   python3
   >>> import sys
   >>> sys.path.append('/home/jnovoas/sentinel')
   >>> from quantum import demo_rift_detection
   >>> demo_rift_detection()
   ```

## Expected Output

After successful installation and running `quantum_lite.py`, you should see:

```
🚀 Sentinel Quantum Lite Initialized
   Membranes: 3, Levels: 5
   Hilbert dimension: 125
   Memory needed: 0.50 GB
   Memory available: 4.23 GB
   ✅ Safe to proceed!

🔬 Running quantum Proyección Cuántica...
   Computing eigendecomposition... ✅
   Evolving quantum state... ✅
📊 Analyzing results...

============================================================
RESULTS
============================================================
Max correlation: 0.847
Rift threshold: 0.700
🚨 RIFT DETECTED: YES ✅

Correlation matrix:
[[1.    0.847 0.623]
 [0.847 1.    0.701]
 [0.623 0.701 1.   ]]

📈 Generating visualization...
✅ Visualization saved: /home/jnovoas/sentinel/quantum/rift_detection_demo.png

============================================================
✅ DEMO COMPLETE - LAPTOP SURVIVED! 💻🎉
============================================================
```

## File Structure After Installation

```
/home/jnovoas/sentinel/quantum/
├── __init__.py                      # Package init
├── core_simulator.py                # Quantum gates & circuits
├── optomechanical_simulator.py      # Membrane physics
├── sentinel_quantum_core.py         # Advanced algorithms (QAOA/VQE)
├── quantum_lite.py                  # Laptop-safe version ⭐
├── test_simulators.py               # Test suite
├── README.md                        # Quick start guide
├── COMPLETE_SUMMARY.md              # Full documentation
├── INSTALL.md                       # This file
└── rift_detection_demo.png          # Generated visualization
```

## Ready to Go! 🚀

Once installation is complete, you have access to:

- ✅ Complete quantum Proyección Cuántica framework
- ✅ Optomechanical physics engine
- ✅ QAOA and VQE algorithms
- ✅ Quantum rift detection
- ✅ Automatic resource management
- ✅ Beautiful visualizations

**Start with**: `python3 quantum_lite.py`

**Your laptop is safe. Sentinel is ready. Let's go! 💻⚛️🚀**
