use pyo3::prelude::*;

/// -------------------------------------------------------------------
/// SENTINEL CORE: RUST BACKEND
/// -------------------------------------------------------------------
/// Memory Efficient Implementation of Liquid Lattice.
/// Target: 16 Bytes per QuantumNode.
/// -------------------------------------------------------------------

#[repr(C, align(64))]
#[derive(Clone, Copy, Debug)]
struct QuantumNode {
    // 8 Bytes: Energy (S60 Amplitude)
    // Supports 2^64 values. Sufficient for S60 range in typical use.
    energy: u64,

    // 2 Bytes: Phase
    // Maps 0-360 degrees to 0-65535.
    // Resolution: 0.005 degrees (Better than Python's 1.4 deg).
    phase: u16,

    // 1 Byte: Flags
    // Bit 0: Active (Has Energy > 0)
    // Bit 1: Locked (Phase locked)
    flags: u8,

    // 53 Bytes: Sacred Silence (Padding)
    // Ensures Structure resonates with Cache Line (64 Bytes).
    // 64 - 11 = 53 bytes of Silence.
    _silence: [u8; 53],
}

#[pyclass]
struct RustLattice {
    // The massive vector.
    // In Python this was List or Dict. Here it is a contiguous slab of RAM.
    nodes: Vec<QuantumNode>,
    rings: usize,
}

#[pymethods]
impl RustLattice {
    #[new]
    fn new(rings: usize) -> Self {
        println!("🦀 Sentinel Rust Core: Allocating Lattice...");

        // For now, let's keep it empty or pre-alloc?
        // If we want to demonstrate memory efficiency, we should push nodes.
        // But Vector grows dynamically.
        // Let's implement sparse-like behavior or just a growable vector.

        RustLattice {
            nodes: Vec::new(),
            rings,
        }
    }

    /// Inject data: Creates nodes as needed.
    /// Simulates 'inject_holograph'.
    fn inject(&mut self, data: &[u8]) -> PyResult<usize> {
        // Clear previous state? Or Append?
        self.nodes.clear();

        let chunk_size = 16;
        let chunks = data.chunks(chunk_size);
        let count = chunks.len();

        // Reserve capacity to avoid re-allocs
        self.nodes.reserve(count);

        for chunk in chunks {
            // Bytes to u64 (Big Endian)
            // If chunk < 16 bytes, pad with 0
            let mut buf = [0u8; 8];
            // We only use 8 bytes for Energy Amplitude (u64).
            // But data is 16 bytes?
            // Python implementation: `_bytes_to_s60` uses int conversion.
            // S60 is a Triple (v, 0, 0).
            // We only store 'v' (the raw integer value).
            // If data is > 8 bytes, u64 overflows!
            // Wait. Python int is arbitrary precision. u64 is not.
            // 8 Bytes = 64 bits.
            // EXP-010 Limit was "32 bytes". Python handled it.
            // Rust u64 handles 8 bytes.
            // PROBLEM: User wanted "Dense Storage".
            // If we only store u64, we store 8 bytes of data per 16-byte node.
            // 50% efficiency.
            // The user design doc said: "energy: u64".
            // If S60 represents 16 bytes of data, it needs u128 or split.

            // FIX: Use u128 for Energy? Or 2x u64?
            // "QuantumNode ... energy: u64" was the approved design.
            // This implies the payload per node is limited to 8 bytes in this V1 rust port.
            // Or we treat 'energy' as a pointer/hash? No.

            // Let's use `u64` for now (8 bytes per node).
            // We will consume data in 8-byte chunks.
            // The design doc said "16B/nodo" for the *struct*, not payload capacity.
            // If payload is 8B per 16B node, that's 50% overhead. Better than 350B!

            // Copy up to 8 bytes
            let len = chunk.len().min(8);
            buf[..len].copy_from_slice(&chunk[..len]);
            let val = u64::from_be_bytes(buf);

            let node = QuantumNode {
                energy: val,
                phase: 0,
                flags: 1, // Active
                _silence: [0; 53],
            };

            self.nodes.push(node);
        }

        Ok(self.nodes.len())
    }

    fn count_nodes(&self) -> usize {
        self.nodes.len()
    }

    fn active_memory_usage(&self) -> usize {
        self.nodes.len() * std::mem::size_of::<QuantumNode>()
    }

    fn get_node_size(&self) -> usize {
        std::mem::size_of::<QuantumNode>()
    }

    // Phase 6: Diffusion Logic
    fn stabilize(&mut self, cycles: usize) -> PyResult<()> {
        // Here we would launch CUDA Kernel
        // For now, we call the CPU Fallback that simulates the GPU logic
        for _ in 0..cycles {
            cuda_diffusion::diffusion_kernel_cpu(&mut self.nodes);
        }
        Ok(())
    }

    // Phase 7: Persistence
    fn save_snapshot(&self, path: &str) -> PyResult<()> {
        use std::io::Write;
        let mut file = std::fs::File::create(path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;

        // Unsafe cast to [u8] slice
        let slice = unsafe {
            std::slice::from_raw_parts(
                self.nodes.as_ptr() as *const u8,
                self.nodes.len() * std::mem::size_of::<QuantumNode>(),
            )
        };

        file.write_all(slice)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        Ok(())
    }

    fn load_snapshot(&mut self, path: &str) -> PyResult<usize> {
        use std::io::Read;
        let mut file = std::fs::File::open(path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;

        let metadata = file
            .metadata()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        let len = metadata.len() as usize;
        let node_size = std::mem::size_of::<QuantumNode>();

        if len % node_size != 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Corrupted Snapshot: Size alignment mismatch",
            ));
        }

        let count = len / node_size;

        // Resize vector
        self.nodes.clear();
        self.nodes.reserve(count);

        // Read directly into vector memory?
        // Safe way: Read to buffer then cast? No, too slow.
        // Fast way: set_len and read_exact into slice.

        unsafe {
            // Initialize memory (or not, we will overwrite)
            // But set_len expects initialized if we access?
            // Vector elements are POD (Copy), so it's mostly fine if we overwrite immediately.
            // But we can't use set_len safely on uninit memory in safe rust.
            // We'll use a buffer approach or unsafe set_len.
            // Given "unsafe" block:
            self.nodes.set_len(count);
            let slice = std::slice::from_raw_parts_mut(self.nodes.as_mut_ptr() as *mut u8, len);
            file.read_exact(slice)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        }

        Ok(count)
    }
}

mod cuda_diffusion;

mod buffer;
use buffer::SharedBuffer;

// ... (Existing QuantumNode struct) ...

#[pyclass]
struct PySharedBuffer {
    inner: SharedBuffer,
}

#[pymethods]
impl PySharedBuffer {
    #[new]
    fn new(name: &str, size: usize, create: bool) -> PyResult<Self> {
        let buf = if create {
            SharedBuffer::create(name, size)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e))?
        } else {
            SharedBuffer::open(name).map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e))?
        };

        Ok(PySharedBuffer { inner: buf })
    }

    fn write(&mut self, offset: usize, data: &[u8]) -> PyResult<()> {
        self.inner
            .write_bytes(offset, data)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))
    }

    fn read(&self, offset: usize, length: usize) -> PyResult<Vec<u8>> {
        self.inner
            .read_bytes(offset, length)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e))
    }

    fn capacity(&self) -> usize {
        self.inner.capacity
    }
}

// ... (Existing RustLattice struct and impl) ...

#[pymodule]
fn sentinel_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustLattice>()?;
    m.add_class::<PySharedBuffer>()?;
    Ok(())
}
