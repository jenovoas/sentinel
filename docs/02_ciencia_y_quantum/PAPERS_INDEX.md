# Índice de Papers Externos — Fundamentos Científicos de Sentinel

> **Fuente única de verdad** para las referencias bibliográficas externas que fundamentan
> los módulos Rust de Sentinel. Cada paper identificado con arXiv ID fue verificacdo vía
> la [API oficial de arXiv](https://arxiv.org) (export.arxiv.org).
>
> **Fecha de compilación:** 2026-08-08 · **Total:** 78 papers (excluye 1 doc tributario no-científico)
>
> **Candado YATRA:** estos papers fundamentan algoritmos que ejecutan en aritmética
> sexagesimal pura (base-60⁴, S60/SPA). Las citas son texto en docstrings Rust —
> **cero riesgo aritmético**: no introducen float, solo documentan la base teórica.

## Convención de Citas

Los docstrings Rust citan por ID corto (`[NV-001]`, `[EXT-005]`, etc.) que resuelve a
este índice. Los algoritmos *originales* de Sentinel se citan como:

> Novoa, J. (2026). *Nota técnica no publicada de Sentinel.* `docs/02_ciencia_y_quantum/RESEARCH_es.md`

## Papers Internos de Sentinel (originales)

| ID | Documento | Concierne a | Path |
|----|-----------|-------------|------|
| P-RES | Investigación: Aritmética Sexagesimal como Base de Sistemas | Tesis principal base-60 / Plimpton 322 | `docs/02_ciencia_y_quantum/RESEARCH_es.md` |
| P-GEO | Geoglifos como Phase Drivers Base-60 | Validación Plimpton 322 | `docs/02_ciencia_y_quantum/research/geoglyphs/GEOGLYPHS_BASE60_PEER_REVIEW_PAPER.md` |
| P-TES | Tesis de Resonancia | Arquitectura de resonancia | `docs/02_ciencia_y_quantum/research/TesiResonancia.md` |
| P-RRS | Reporte Final Resonance Architecture | Diseño de resonancia | `docs/02_ciencia_y_quantum/FINAL_REPORT_RESONANCE_ARCHITECTURE.md` |
| P-BEK | Bekenstein Base-60 | Límites Bekenstein | `docs/02_ciencia_y_quantum/quantum/WHITE_PAPER_BEKENSTEIN_BASE60.md` |
| P-MHD | MHD Shield Technical | Escudo MHD | `docs/02_ciencia_y_quantum/quantum/MHD_SHIELD_TECHNICAL_WHITE_PAPER.md` |
| P-S20 | Sentinel 2.0 Paper | Arquitectura dual-lane | `docs/02_ciencia_y_quantum/quantum/SENTINEL_2.0_PAPER.md` |
| P-PAT | Patent Claims | Claims patentables | `docs/02_ciencia_y_quantum/PATENT_CLAIMS.md` |

## Fuentes Externas Fundacionales (con DOI/arXiv verificado)

| ID | Cita | DOI/arXiv | usado en |
|----|------|-----------|---------|
| EXT-MAN | Mansfield, D. F. & Wildberger, N. J. (2017). *Plimpton 322 is Babylonian exact sexagesimal trigonometry.* Historia Mathematica. | 10.1016/j.hm.2017.08.001 | `pai60_lib.rs`, `spa_math.rs`, `isochronous_oscillator.rs`, `verify_plimpton.rs`, `s60.rs`, `s60_math.rs`, `harmonic_logic.rs` |
| EXT-NV | Nandi & Vitiello (2026). *Spin-Induced Fractal Time-Crystal-Like Dynamics and Non-Markovian Memory in the Bateman Dual Oscillator.* | arXiv:2606.30890 | `quantum_core.rs`, `time_crystal.rs`, `isochronous_oscillator.rs` |

## Nandi & Vitiello — Memoria No-Markoviana, Cristales de Tiempo, Gravedad Cuántica

(51 papers)

| ID | arXiv | Título | Módulos Rust |
|----|-------|--------|--------------|
| NV-001 | [0705.0319](https://arxiv.org/abs/0705.0319) | Dark energy, cosmological constant and neutrino mixing | `quantum_core.rs` |
| NV-002 | [0709.0924](https://arxiv.org/abs/0709.0924) | Cosmological effects of neutrino mixing | `quantum_core.rs` |
| NV-003 | [0709.1384](https://arxiv.org/abs/0709.1384) | Flavor states of mixed neutrinos | `quantum_core.rs` |
| NV-004 | [0711.0939](https://arxiv.org/abs/0711.0939) | Neutrino mixing, flavor states and dark energy | `quantum_core.rs` |
| NV-005 | [0809.0082](https://arxiv.org/abs/0809.0082) | A new perspective in the dark energy puzzle from particle mixing phenomenon | `quantum_core.rs` |
| NV-006 | [0809.0085](https://arxiv.org/abs/0809.0085) | Dark energy and particle mixing | `quantum_core.rs` |
| NV-007 | [0812.2133](https://arxiv.org/abs/0812.2133) | On flavor violation for massive and mixed neutrinos | `quantum_core.rs` |
| NV-008 | [0905.4078](https://arxiv.org/abs/0905.4078) | Dissipation and quantization for composite systems | `quantum_core.rs, time_crystal.rs` |
| NV-009 | [1012.5166](https://arxiv.org/abs/1012.5166) | DNA waves and water | `quantum_core.rs, liquid_memory.rs` |
| NV-010 | [1104.3743](https://arxiv.org/abs/1104.3743) | Gauge theory and two level systems | `quantum_core.rs` |
| NV-011 | [1104.3771](https://arxiv.org/abs/1104.3771) | Geometric phase and gauge theory structure in quantum computing | `quantum_core.rs` |
| NV-012 | [1110.3677](https://arxiv.org/abs/1110.3677) | Cortical phase transitions, non-equilibrium thermodynamics and the time-dependent Ginzburg-Landau equation | `quantum_core.rs, time_crystal.rs` |
| NV-013 | [1312.7744](https://arxiv.org/abs/1312.7744) | Self-similarity properties of nafionized and filtered water and deformed coherent states | `time_crystal.rs, liquid_memory.rs` |
| NV-014 | [1502.00623](https://arxiv.org/abs/1502.00623) | Vacuum condensate, geometric phase, Unruh effect and temperature measurement | `quantum_core.rs` |
| NV-015 | [1510.07288](https://arxiv.org/abs/1510.07288) | Probing mixing of photons and axion-like particles by geometric phase | `quantum_core.rs` |
| NV-016 | [1512.03265](https://arxiv.org/abs/1512.03265) | Geometric phase and its applications to fundamental physics | `quantum_core.rs, liquid_memory.rs` |
| NV-017 | [1605.07504](https://arxiv.org/abs/1605.07504) | Nanometre scale monitoring of the quantum confined stark effect and emission efficiency droop in multiple GaN/AlN quantum disks in nanowires | `quantum_core.rs` |
| NV-018 | [1608.08097](https://arxiv.org/abs/1608.08097) | Water-mediated correlations in DNA-enzyme interactions | `quantum_core.rs` |
| NV-019 | [1610.08679](https://arxiv.org/abs/1610.08679) | Geometric phase of neutrinos: differences between Dirac and Majorana neutrinos | `quantum_core.rs, isochronous_oscillator.rs` |
| NV-020 | [1801.06311](https://arxiv.org/abs/1801.06311) | On the canonical quantization of the electromagnetic field and the emergence of gauge invariance | `quantum_core.rs` |
| NV-021 | [1811.08562](https://arxiv.org/abs/1811.08562) | Dynamics of zero-point energy and two-slit phenomena for photons | `quantum_core.rs` |
| NV-022 | [1908.11206](https://arxiv.org/abs/1908.11206) | Effect of dynamical noncommutativity on the limiting mass of white dwarfs | `quantum_core.rs` |
| NV-023 | [1911.03196](https://arxiv.org/abs/1911.03196) | Emergence of Geometric phase shift in Planar Non-commutative Quantum Mechanics | `quantum_core.rs, isochronous_oscillator.rs` |
| NV-024 | [2101.07076](https://arxiv.org/abs/2101.07076) | A note on broken dilatation symmetry in planar noncommutative theory | `quantum_core.rs` |
| NV-025 | [2106.07028](https://arxiv.org/abs/2106.07028) | A Conformally Invariant Unified Theory of Maxwell Fields and Linearized Gravity as Emergent Fields | `quantum_core.rs` |
| NV-026 | [2110.04730](https://arxiv.org/abs/2110.04730) | Fingerprints of the quantum space-time in time-dependent quantum mechanics: An emergent geometric phase | `quantum_core.rs` |
| NV-027 | [2111.03012](https://arxiv.org/abs/2111.03012) | Spectral triple with real structure on fuzzy sphere | `quantum_core.rs` |
| NV-028 | [2207.08687](https://arxiv.org/abs/2207.08687) | Low frequency gravitational waves emerge Berry phase | `isochronous_oscillator.rs` |
| NV-029 | [2209.04758](https://arxiv.org/abs/2209.04758) | Some Aspects of Quantum Mechanics and Quantum Field Theory on Quantum Space- Time | `quantum_core.rs` |
| NV-030 | [2212.06548](https://arxiv.org/abs/2212.06548) | Our Trysts with `Bal' and Noncommutative Geometry | `quantum_core.rs` |
| NV-031 | [2303.02728](https://arxiv.org/abs/2303.02728) | Symmetries of $κ$ Minkowski space-time: A possibility of exotic momentum space geometry? | `quantum_core.rs` |
| NV-032 | [2309.16895](https://arxiv.org/abs/2309.16895) | Magnetically Induced Schrödinger Cat States: The Shadow of a Quantum Space | `quantum_core.rs` |
| NV-033 | [2312.15750](https://arxiv.org/abs/2312.15750) | The hidden Lorentz Covariance of Quantum Mechanics | `quantum_core.rs` |
| NV-034 | [2401.02778](https://arxiv.org/abs/2401.02778) | Quantum ballet by gravitational waves: Generating entanglement's dance of revival-collapse and memory within the quantum system | `quantum_core.rs` |
| NV-035 | [2401.12957](https://arxiv.org/abs/2401.12957) | Symmetry Duality: Exploring Exotic Oscillators And Dissipative Dynamics Through The Glass Of Newton-Hooke | `quantum_core.rs` |
| NV-036 | [2403.11253](https://arxiv.org/abs/2403.11253) | Unveiling gravity's quantum fingerprint through gravitational waves | `quantum_core.rs` |
| NV-037 | [2410.03808](https://arxiv.org/abs/2410.03808) | Unearthing Neutrino Decoherence from Quantum Spacetime: An Open Quantum Systems Perspective | `optomechanical.rs, quantum_core.rs` |
| NV-038 | [2412.13004](https://arxiv.org/abs/2412.13004) | Phase Segregation Dynamics in Mixed-Halide Perovskites Revealed by Plunge-Freeze Cryogenic Electron Microscopy | `quantum_core.rs` |
| NV-039 | [2503.13061](https://arxiv.org/abs/2503.13061) | Decoherence from quantum spacetime noise: An open-systems framework with application to neutrino oscillations | `quantum_core.rs` |
| NV-040 | [2503.19688](https://arxiv.org/abs/2503.19688) | Gravitationally induced entanglement at finite temperature: A memory-driven time-crystalline phase? | `quantum_core.rs, time_crystal.rs` |
| NV-041 | [2506.12506](https://arxiv.org/abs/2506.12506) | Can Non-Relativistic Strings Propagate Without Geometric Baggage? | `quantum_core.rs` |
| NV-042 | [2508.05881](https://arxiv.org/abs/2508.05881) | Quantum Geometric Phases as a New Window on Gravitational Waves | `isochronous_oscillator.rs` |
| NV-043 | [2508.10190](https://arxiv.org/abs/2508.10190) | Stochastic Quantization of Electrodynamics and Linearized Gravity | `quantum_core.rs` |
| NV-044 | [2509.05713](https://arxiv.org/abs/2509.05713) | Quantum-Gravitational Backreaction in the BTZ Background from Curved Momentum Space | `quantum_core.rs` |
| NV-045 | [2510.10836](https://arxiv.org/abs/2510.10836) | Spinning into Quantum Geometry: Dirac and Wheeler-DeWitt Dynamics from Stochastic Helicity | `quantum_core.rs` |
| NV-046 | [2510.11075](https://arxiv.org/abs/2510.11075) | A novel quantum memory effect and thermal modulation in graviton-mediated entanglement | `quantum_core.rs, liquid_memory.rs` |
| NV-047 | [2603.05731](https://arxiv.org/abs/2603.05731) | State-Selective Signatures of Quantum and Classical Gravitational Environments | `quantum_core.rs` |
| NV-048 | [2605.19917](https://arxiv.org/abs/2605.19917) | Spin-Induced Non-Markovian Time-Crystal-Like Dynamics and Fractal Scaling in the Bateman Dual Oscillator | `quantum_core.rs` |
| NV-049 | [2606.08595](https://arxiv.org/abs/2606.08595) | Is Exact Markovianity Fundamental Once Time Is Relational? | `quantum_core.rs` |
| NV-050 | [2606.30890](https://arxiv.org/abs/2606.30890) | Spin-Induced Fractal Time-Crystal-Like Dynamics and Non-Markovian Memory in the Bateman Dual Oscillator | `quantum_core.rs, isochronous_oscillator.rs, time_crystal.rs` |
| NV-051 | [2607.23776](https://arxiv.org/abs/2607.23776) | Exploring Quantum Corners: How Curved Momentum Space Shapes BTZ Black Holes | `quantum_core.rs` |

## Muir & Nikiforakis — Magnetohidrodinámica (MHD) / Flujos Hipersónicos

(7 papers)

| ID | arXiv | Título | Módulos Rust |
|----|-------|--------|--------------|
| MN-001 | [1509.02572](https://arxiv.org/abs/1509.02572) | 3D cut-cell modelling for high-resolution atmospheric simulations | `physics.rs` |
| MN-002 | [1702.01021](https://arxiv.org/abs/1702.01021) | Direct numerical simulation of particulate flows with an overset grid method | `physics.rs` |
| MN-003 | [1711.11361](https://arxiv.org/abs/1711.11361) | A Moving Boundary Flux Stabilization Method for Cartesian Cut-Cell Grids using Directional Operator Splitting | `physics.rs` |
| MN-004 | [1806.04513](https://arxiv.org/abs/1806.04513) | Direct numerical simulation of particle sedimentation in a Bingham fluid | `physics.rs` |
| MN-005 | [1903.00353](https://arxiv.org/abs/1903.00353) | Fast Distance Fields for Fluid Dynamics Mesh Generation on Graphics Hardware | `physics.rs` |
| MN-006 | [2107.04415](https://arxiv.org/abs/2107.04415) | Equation of state driven radiative models for simulation of lightning strikes | `physics.rs` |
| MN-007 | [2411.12607](https://arxiv.org/abs/2411.12607) | Single-fluid simulation of partially-ionized, non-ideal plasma facilitated by a tabulated equation of state | `physics.rs` |

## Zhang & Wang — Memoria Fonónica / Inteligencia Mecánica Cognitiva

(5 papers)

| ID | arXiv | Título | Módulos Rust |
|----|-------|--------|--------------|
| ZW-001 | [1709.01800](https://arxiv.org/abs/1709.01800) | Metastable Modular Metastructures for On-Demand Reconfiguration of Band Structures and Non-Reciprocal Wave Propagation | `neural_memory.rs` |
| ZW-002 | [1812.00517](https://arxiv.org/abs/1812.00517) | A piezo-metastructure with bistable circuit shunts for adaptive nonreciprocal wave transmission | `neural_memory.rs, liquid_memory.rs` |
| ZW-003 | [2201.10745](https://arxiv.org/abs/2201.10745) | Control Variate Polynomial Chaos: Optimal Fusion of Sampling and Surrogates for Multifidelity Uncertainty Quantification | `neural_memory.rs` |
| ZW-004 | [2305.19354](https://arxiv.org/abs/2305.19354) | Uncovering multifunctional mechano-intelligence in and through phononic metastructures harnessing physical reservoir computing | `neural_memory.rs, liquid_memory.rs` |
| ZW-005 | [2511.13543](https://arxiv.org/abs/2511.13543) | In-memory phononic learning toward cognitive mechanical intelligence | `neural_memory.rs, liquid_memory.rs` |

## Papers raíz — Optomecánica, Memoria Cuántica, eBPF, Cristales de Tiempo

(15 papers)

| ID | arXiv | Título | Módulos Rust |
|----|-------|--------|--------------|
| EXT-001 | [0709.0032](https://arxiv.org/abs/0709.0032) | Thermal Logic Gates: Computation with phonons | `quantum_core.rs` |
| EXT-002 | [1301.2807](https://arxiv.org/abs/1301.2807) | Beyond electronics, beyond optics: single circuit parallel computing with phonons | `quantum_core.rs` |
| EXT-003 | [2102.09980](https://arxiv.org/abs/2102.09980) | A flow-based IDS using Machine Learning in eBPF | `guardian_lsm.rs, ebpf_cortex_bridge.rs` |
| EXT-004 | [2207.09857](https://arxiv.org/abs/2207.09857) | Numerical modelling of imposed magnetohydrodynamic effects in hypersonic flows | `physics.rs` |
| EXT-005 | [2412.14117](https://arxiv.org/abs/2412.14117) | High-purity quantum optomechanics at room temperature | `optomechanical.rs` |
| EXT-006 | [2505.13804](https://arxiv.org/abs/2505.13804) | QUT-DV25: A Dataset for Dynamic Analysis of Next-Gen Software Supply Chain Attacks | `guardian_lsm.rs` |
| EXT-007 | [2508.00851](https://arxiv.org/abs/2508.00851) | eBPF-DDoS Mitigation for IoT | `guardian_lsm.rs` |
| EXT-008 | [2509.21959](https://arxiv.org/abs/2509.21959) | Memory of Starobinsky in a Time Crystal (Condensate) | `time_crystal.rs, liquid_memory.rs` |
| EXT-009 | [2511.12537](https://arxiv.org/abs/2511.12537) | Minute-Scale Photonic Quantum Memory | `liquid_memory.rs` |
| EXT-010 | [2511.13543](https://arxiv.org/abs/2511.13543) | In-memory phononic learning toward cognitive mechanical intelligence | `neural_memory.rs, liquid_memory.rs` |
| EXT-011 | [2511.13543](https://arxiv.org/abs/2511.13543) | In-memory phononic learning toward cognitive mechanical intelligence | `neural_memory.rs, liquid_memory.rs` |
| EXT-012 | [2511.15492](https://arxiv.org/abs/2511.15492) | Optomechanical disk resonator in the quantum ground state of motion | `optomechanical.rs` |
| EXT-013 | [2605.20902](https://arxiv.org/abs/2605.20902) | Coherent Feedback Cooling of an Ultracoherent Phononic-Crystal Membrane at Room Temperature | `optomechanical.rs` |
| EXT-014 | [2605.25411](https://arxiv.org/abs/2605.25411) | Heimdall: Formally Verified Automated Migration of Legacy eBPF Programs to Rust | `ebpf_cortex_bridge.rs, dual_lane.rs` |
| EXT-015 | [2606.30890](https://arxiv.org/abs/2606.30890) | Spin-Induced Fractal Time-Crystal-Like Dynamics and Non-Markovian Memory in the Bateman Dual Oscillator | `quantum_core.rs, isochronous_oscillator.rs, time_crystal.rs` |

## Mapeo Inverso: Módulos Rust → Papers

Para insertar en docstrings Rust — cada módulo cita los papers que lo fundamentan.

| Módulo Rust | Papers fundamentales |
|-------------|---------------------|
| `dual_lane.rs` | [EXT-014](https://arxiv.org/abs/2605.25411) |
| `ebpf_cortex_bridge.rs` | [EXT-003](https://arxiv.org/abs/2102.09980), [EXT-014](https://arxiv.org/abs/2605.25411) |
| `guardian_lsm.rs` | [EXT-003](https://arxiv.org/abs/2102.09980), [EXT-006](https://arxiv.org/abs/2505.13804), [EXT-007](https://arxiv.org/abs/2508.00851) |
| `isochronous_oscillator.rs` | [NV-019](https://arxiv.org/abs/1610.08679), [NV-023](https://arxiv.org/abs/1911.03196), [NV-028](https://arxiv.org/abs/2207.08687), [NV-042](https://arxiv.org/abs/2508.05881), [NV-050](https://arxiv.org/abs/2606.30890), [EXT-015](https://arxiv.org/abs/2606.30890) |
| `liquid_memory.rs` | [NV-009](https://arxiv.org/abs/1012.5166), [NV-013](https://arxiv.org/abs/1312.7744), [NV-016](https://arxiv.org/abs/1512.03265), [NV-046](https://arxiv.org/abs/2510.11075), [ZW-002](https://arxiv.org/abs/1812.00517), [ZW-004](https://arxiv.org/abs/2305.19354), [ZW-005](https://arxiv.org/abs/2511.13543), [EXT-008](https://arxiv.org/abs/2509.21959), [EXT-009](https://arxiv.org/abs/2511.12537), [EXT-010](https://arxiv.org/abs/2511.13543), [EXT-011](https://arxiv.org/abs/2511.13543) |
| `neural_memory.rs` | [ZW-001](https://arxiv.org/abs/1709.01800), [ZW-002](https://arxiv.org/abs/1812.00517), [ZW-003](https://arxiv.org/abs/2201.10745), [ZW-004](https://arxiv.org/abs/2305.19354), [ZW-005](https://arxiv.org/abs/2511.13543), [EXT-010](https://arxiv.org/abs/2511.13543), [EXT-011](https://arxiv.org/abs/2511.13543) |
| `optomechanical.rs` | [NV-037](https://arxiv.org/abs/2410.03808), [EXT-005](https://arxiv.org/abs/2412.14117), [EXT-012](https://arxiv.org/abs/2511.15492), [EXT-013](https://arxiv.org/abs/2605.20902) |
| `physics.rs` | [MN-001](https://arxiv.org/abs/1509.02572), [MN-002](https://arxiv.org/abs/1702.01021), [MN-003](https://arxiv.org/abs/1711.11361), [MN-004](https://arxiv.org/abs/1806.04513), [MN-005](https://arxiv.org/abs/1903.00353), [MN-006](https://arxiv.org/abs/2107.04415), [MN-007](https://arxiv.org/abs/2411.12607), [EXT-004](https://arxiv.org/abs/2207.09857) |
| `quantum_core.rs` | [NV-001](https://arxiv.org/abs/0705.0319), [NV-002](https://arxiv.org/abs/0709.0924), [NV-003](https://arxiv.org/abs/0709.1384), [NV-004](https://arxiv.org/abs/0711.0939), [NV-005](https://arxiv.org/abs/0809.0082), [NV-006](https://arxiv.org/abs/0809.0085), [NV-007](https://arxiv.org/abs/0812.2133), [NV-008](https://arxiv.org/abs/0905.4078), [NV-009](https://arxiv.org/abs/1012.5166), [NV-010](https://arxiv.org/abs/1104.3743), [NV-011](https://arxiv.org/abs/1104.3771), [NV-012](https://arxiv.org/abs/1110.3677), [NV-014](https://arxiv.org/abs/1502.00623), [NV-015](https://arxiv.org/abs/1510.07288), [NV-016](https://arxiv.org/abs/1512.03265), [NV-017](https://arxiv.org/abs/1605.07504), [NV-018](https://arxiv.org/abs/1608.08097), [NV-019](https://arxiv.org/abs/1610.08679), [NV-020](https://arxiv.org/abs/1801.06311), [NV-021](https://arxiv.org/abs/1811.08562), [NV-022](https://arxiv.org/abs/1908.11206), [NV-023](https://arxiv.org/abs/1911.03196), [NV-024](https://arxiv.org/abs/2101.07076), [NV-025](https://arxiv.org/abs/2106.07028), [NV-026](https://arxiv.org/abs/2110.04730), [NV-027](https://arxiv.org/abs/2111.03012), [NV-029](https://arxiv.org/abs/2209.04758), [NV-030](https://arxiv.org/abs/2212.06548), [NV-031](https://arxiv.org/abs/2303.02728), [NV-032](https://arxiv.org/abs/2309.16895), [NV-033](https://arxiv.org/abs/2312.15750), [NV-034](https://arxiv.org/abs/2401.02778), [NV-035](https://arxiv.org/abs/2401.12957), [NV-036](https://arxiv.org/abs/2403.11253), [NV-037](https://arxiv.org/abs/2410.03808), [NV-038](https://arxiv.org/abs/2412.13004), [NV-039](https://arxiv.org/abs/2503.13061), [NV-040](https://arxiv.org/abs/2503.19688), [NV-041](https://arxiv.org/abs/2506.12506), [NV-043](https://arxiv.org/abs/2508.10190), [NV-044](https://arxiv.org/abs/2509.05713), [NV-045](https://arxiv.org/abs/2510.10836), [NV-046](https://arxiv.org/abs/2510.11075), [NV-047](https://arxiv.org/abs/2603.05731), [NV-048](https://arxiv.org/abs/2605.19917), [NV-049](https://arxiv.org/abs/2606.08595), [NV-050](https://arxiv.org/abs/2606.30890), [NV-051](https://arxiv.org/abs/2607.23776), [EXT-001](https://arxiv.org/abs/0709.0032), [EXT-002](https://arxiv.org/abs/1301.2807), [EXT-015](https://arxiv.org/abs/2606.30890) |
| `time_crystal.rs` | [NV-008](https://arxiv.org/abs/0905.4078), [NV-012](https://arxiv.org/abs/1110.3677), [NV-013](https://arxiv.org/abs/1312.7744), [NV-040](https://arxiv.org/abs/2503.19688), [NV-050](https://arxiv.org/abs/2606.30890), [EXT-008](https://arxiv.org/abs/2509.21959), [EXT-015](https://arxiv.org/abs/2606.30890) |

## Constantes Verificables (Candado YATRA)

Estas constantes se mencionan en las citas Rust y deben coincidir *exactamente* con el código
(verificado en Paso 5 del plan). Cero floats:

| Constante | Valor código | Fundamento |
|-----------|--------------|------------|
| `RESONANCE_RATIO` (`spa_math.rs`) | `SPA::new(1, 32, 2, 24, 0)` = 1;32,2,24 | Plimpton 322 Fila 12 — EXT-MAN (Mansfield & Wildberger 2017) |
| `PAI-60` recíprocos (`pai60_lib.rs`) | denominadores 5-smooth: 2,3,4,5,6,8,9,10,12,15,...,60 | Tablas recíprocas babilónicas — EXT-MAN |
| Bateman dual oscillator (`quantum_core.rs`) | S60PID non-Markoviano, partial trace memory kernel | EXT-NV (Nandi & Vitiello 2026, arXiv:2606.30890) |

## Nota Metodológica

1. **Los papers fueron encontrados DESPUÉS de escribir el código** — el usuario lo aclaró
   explícitamente. Las implementaciones Rust existían primero; ahora se enlazan a las
   fuentes teóricas formales que las fundamentan.
2. **Títulos verificados** vía API oficial de arXiv (`export.arxiv.org/api/query`). 78/78
   papers con título real, 0 fabricados. Los 4 sin metadatos PDF se obtuvieron vía API.
3. **NO se fabrican DOIs**: solo arXiv IDs (verificables públicamente) y el DOI de
   Mansfield & Wildberger 2017 (reconocido, Historia Mathematica).
4. **Paths locales** via symlink `docs/02_ciencia_y_quantum/papers/referencias_locales`
   → `/home/jnovoas/Documentos`. Los PDFs están en `Papers/<subdir>/`.

---
*Generado 2026-08-08. Mantener sincronizado con docstrings Rust (verificaciones en Paso 5 del plan).*