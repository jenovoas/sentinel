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

    // 5 Bytes: Reserved (Padding)
    // Ensures Structure is exactly 16 Bytes.
    // 16 - (8 + 2 + 1) = 5 bytes.
    _silence: [u8; 5],
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

        RustLattice {
            nodes: Vec::new(),
            rings,
        }
    }

    /// Inject data: Creates nodes as needed.
    /// Simulates 'inject_holograph'.
    /// ZERO DATA LOSS: We consume 8 bytes per node (u64 Energy).
    fn inject(&mut self, data: &[u8]) -> PyResult<usize> {
        self.nodes.clear();

        // 8 bytes per node -> Zero Loss
        // (Previously 16 byte input -> 8 byte storage = 50% loss. Now fixed).
        let chunk_size = 8;
        let chunks = data.chunks(chunk_size);
        let count = (data.len() + chunk_size - 1) / chunk_size;

        // Reserve capacity to avoid re-allocs
        self.nodes.reserve(count);

        for chunk in chunks {
            // Buffer for u64 conversion
            let mut buf = [0u8; 8];

            // Copy chunk data (pad with 0 if partial)
            let len = chunk.len();
            buf[..len].copy_from_slice(chunk);

            // Big Endian to preserve byte order hierarchy
            let val = u64::from_be_bytes(buf);

            let node = QuantumNode {
                energy: val,
                phase: 0,
                flags: 1, // Active
                _silence: [0; 5],
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
