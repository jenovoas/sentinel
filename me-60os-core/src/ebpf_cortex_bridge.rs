// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛰️ eBPF → Cortex Bridge 🛰️
//!
//! Polls BPF ring buffer for kernel events and feeds them directly
//! to the Cortex neural network.
//!
//! Architecture:
//! ```text
//! Kernel eBPF -> Ring Buffer -> This Bridge -> ResonantBuffer -> Cortex
//! ```
//!
//! Performance:
//! - Zero-copy from kernel to userspace
//! - Lock-free ring buffer
//! - Sub-millisecond latency
//!
//! ## References (eBPF → userspace / verificación formal)
//! - [EXT-003] A flow-based IDS using Machine Learning in eBPF. arXiv:2102.09980.
//! - [EXT-014] Heimdall: Formally Verified Automated Migration of Legacy eBPF Programs to Rust. arXiv:2605.25411.
//! - [P-S20] Novoa, J. (2026). *Sentinel 2.0 Paper.* `docs/02_ciencia_y_quantum/quantum/SENTINEL_2.0_PAPER.md`.

use crate::buffer_system::ResonantBuffer;
use crate::spa::SPA;
use std::sync::Arc;
use std::thread;
use std::time::Duration;

// Event type constants (must match cortex_events.h)
#[allow(dead_code)]
const EVENT_FILE_BLOCKED: u32 = 1;
#[allow(dead_code)]
const EVENT_EXEC_BLOCKED: u32 = 2;
#[allow(dead_code)]
const EVENT_FILE_ALLOWED: u32 = 3;
#[allow(dead_code)]
const EVENT_EXEC_ALLOWED: u32 = 4;
#[allow(dead_code)]
const EVENT_NETWORK_BURST: u32 = 5;
#[allow(dead_code)]
const EVENT_NETWORK_NORMAL: u32 = 6;
#[allow(dead_code)]
const EVENT_FLOAT_CONTAMINATION: u32 = 10;
#[allow(dead_code)]
const EVENT_MATH_DIVERSION: u32 = 19;


// Severity levels
#[allow(dead_code)]
const SEVERITY_LOW: u8 = 0;
#[allow(dead_code)]
const SEVERITY_MEDIUM: u8 = 1;
#[allow(dead_code)]
const SEVERITY_HIGH: u8 = 2;
#[allow(dead_code)]
const SEVERITY_CRITICAL: u8 = 3;

use pyo3::prelude::*;

/// Raw Cortex Event (Packed, matching C layout)
#[repr(C, packed)]
#[derive(Debug, Copy, Clone)]
pub struct RawCortexEvent {
    pub timestamp_ns: u64,
    pub event_type: u32,
    pub pid: u32,
    pub entropy_signal: u64, // SPA raw value
    pub severity: u8,
    pub _reserved: [u8; 7],
}

/// Cortex Event (Python-friendly, unpacked)
#[pyclass] // Exposed to Python
#[derive(Debug, Clone, Default)]
pub struct CortexEvent {
    #[pyo3(get, set)]
    pub timestamp_ns: u64,
    #[pyo3(get, set)]
    pub event_type: u32,
    #[pyo3(get, set)]
    pub pid: u32,
    #[pyo3(get, set)]
    pub entropy_signal: u64,
    #[pyo3(get, set)]
    pub severity: u8,
}

#[pymethods]
impl CortexEvent {
    #[new]
    pub fn new(
        timestamp_ns: u64,
        event_type: u32,
        pid: u32,
        entropy_signal: u64,
        severity: u8,
    ) -> Self {
        Self {
            timestamp_ns,
            event_type,
            pid,
            entropy_signal,
            severity,
        }
    }
}

impl CortexEvent {
    // Constructor from RawCortexEvent (Internal Rust only)
    pub fn from_raw_event(raw_event: RawCortexEvent) -> Self {
        Self {
            timestamp_ns: raw_event.timestamp_ns,
            event_type: raw_event.event_type,
            pid: raw_event.pid,
            entropy_signal: raw_event.entropy_signal,
            severity: raw_event.severity,
        }
    }
}

/// eBPF to Cortex Bridge
pub struct EbpfCortexBridge {
    buffer: Arc<ResonantBuffer>,
    #[allow(dead_code)]
    neuron_map: NeuronMapping,
}

/// Maps event types to specific neurons
#[allow(dead_code)]
struct NeuronMapping {
    file_blocked: usize,
    exec_blocked: usize,
    file_allowed: usize,
    exec_allowed: usize,
    network_burst: usize,
    network_normal: usize,
}

impl Default for NeuronMapping {
    fn default() -> Self {
        Self {
            file_blocked: 0,     // Neuron 0: File access threats
            exec_blocked: 64,    // Neuron 64: Execution threats
            file_allowed: 128,   // Neuron 128: Normal file ops
            exec_allowed: 192,   // Neuron 192: Normal exec ops
            network_burst: 256,  // Neuron 256: Network anomalies
            network_normal: 320, // Neuron 320: Normal network
        }
    }
}

impl EbpfCortexBridge {
    pub fn new(buffer: Arc<ResonantBuffer>) -> Self {
        Self {
            buffer,
            neuron_map: NeuronMapping::default(),
        }
    }

    /// Start polling ring buffer (blocking, run in dedicated thread)
    ///
    /// Polls the eBPF ring buffer for cortex events and feeds them to the neural network.
    /// This function blocks and should be run in a dedicated thread.
    ///
    /// # Arguments
    /// * `ringbuf_path` - Path to the pinned ring buffer map (e.g., "/sys/fs/bpf/ai_guardian_maps/cortex_events")
    ///
    /// # Returns
    /// Returns an error if the ring buffer cannot be opened or polling fails
    pub fn start_polling(&self, ringbuf_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        use libbpf_rs::{MapHandle, RingBufferBuilder};
        use std::path::Path;

        eprintln!("🛰️ eBPF Cortex Bridge: Starting ring buffer polling...");
        eprintln!("   Ring buffer: {}", ringbuf_path);

        // Check if path is a directory (old API) or file (new API)
        let map_path = if Path::new(ringbuf_path).is_dir() {
            // Directory provided, append cortex_events
            format!("{}/cortex_events", ringbuf_path)
        } else {
            // Direct path to ring buffer
            ringbuf_path.to_string()
        };

        eprintln!("   Using map path: {}", map_path);

        // Open the pinned ring buffer map
        let map = MapHandle::from_pinned_path(&map_path)
            .map_err(|e| format!("Failed to open pinned map at {}: {}", map_path, e))?;

        eprintln!("✅ Ring buffer map opened successfully");

        // Create ring buffer with callback
        let mut builder = RingBufferBuilder::new();

        // Clone self for the closure
        let buffer = self.buffer.clone();

        builder.add(&map, move |data: &[u8]| -> i32 {
            // Handle event in the callback
            if data.len() < std::mem::size_of::<RawCortexEvent>() {
                eprintln!("⚠️ Invalid event size: {}", data.len());
                return 0;
            }

            // SAFETY: We've verified the size matches RawCortexEvent
            let event: RawCortexEvent =
                unsafe { std::ptr::read_unaligned(data.as_ptr() as *const RawCortexEvent) };

            // Push CortexEvent to resonant buffer
            buffer.push(CortexEvent::from_raw_event(event));

            // Copy fields to avoid unaligned references
            let event_type = event.event_type;
            let pid = event.pid;
            let entropy_signal = event.entropy_signal;
            let severity = event.severity;

            // Log event
            eprintln!(
                "📡 eBPF Event: type={} pid={} entropy={} severity={}",
                event_type, pid, SPA::from_raw(entropy_signal as i64), severity
            );

            0 // Return 0 to continue polling
        })?;

        let ringbuf = builder.build()?;

        eprintln!("✅ Ring buffer polling active! Waiting for kernel events...");
        eprintln!("   Press Ctrl+C to stop");

        // Poll loop - blocks here
        loop {
            match ringbuf.poll(Duration::from_millis(100)) {
                Ok(_) => {}
                Err(e) => {
                    eprintln!("⚠️ Ring buffer poll error: {}", e);
                    thread::sleep(Duration::from_millis(100));
                }
            }
        }
    }

    /// Consumes events for a limited time (Energy Saving Mode)
    #[allow(dead_code)]
    pub fn consume_pulse(
        &self,
        ringbuf_path: &str,
        timeout_ms: u64,
    ) -> Result<usize, Box<dyn std::error::Error>> {
        use libbpf_rs::{MapHandle, RingBufferBuilder};
        use std::path::Path;
        use std::sync::atomic::{AtomicUsize, Ordering};
        use std::sync::Arc;
        use std::time::Duration;

        let path = Path::new(ringbuf_path);

        let map_path = if path.display().to_string().ends_with("cortex_events") {
            path.to_path_buf()
        } else if path.is_dir() {
            path.join("cortex_events")
        } else {
            path.to_path_buf()
        };

        let map = MapHandle::from_pinned_path(&map_path)
            .map_err(|e| format!("Failed to open pinned map at {}: {}", map_path.display(), e))?;

        let mut builder = RingBufferBuilder::new();
        let buffer = self.buffer.clone();

        let event_count = Arc::new(AtomicUsize::new(0));
        let count_clone = event_count.clone();

        builder
            .add(&map, move |data: &[u8]| -> i32 {
                if data.len() < std::mem::size_of::<RawCortexEvent>() {
                    return 0;
                }
                // SAFETY: data.len() was checked >= size_of::<RawCortexEvent>() above; pointer is valid for read
                let event: RawCortexEvent =
                    unsafe { std::ptr::read_unaligned(data.as_ptr() as *const RawCortexEvent) };
                buffer.push(CortexEvent::from_raw_event(event));

                count_clone.fetch_add(1, Ordering::Relaxed);
                0
            })
            .map_err(|e| format!("Failed to add map to ring buffer: {}", e))?;

        let ringbuf = builder
            .build()
            .map_err(|e| format!("Could not build ringbuf: {}", e))?;

        // Poll and ignore return value (since it might be unit)
        let _ = ringbuf.poll(Duration::from_millis(timeout_ms));

        Ok(event_count.load(Ordering::Relaxed))
    }

    /// Consumes events for a limited time and returns the actual event data
    pub fn consume_events(
        &self,
        ringbuf_path: &str,
        timeout_ms: u64,
    ) -> Result<Vec<CortexEvent>, Box<dyn std::error::Error>> {
        use libbpf_rs::{MapHandle, RingBufferBuilder};
        use std::path::Path;
        use std::sync::Mutex;
        use std::time::Duration;

        let path = Path::new(ringbuf_path);
        let map_path = if path.display().to_string().ends_with("cortex_events") {
            path.to_path_buf()
        } else if path.is_dir() {
            path.join("cortex_events")
        } else {
            path.to_path_buf()
        };

        let map = MapHandle::from_pinned_path(&map_path)
            .map_err(|e| format!("Failed to open pinned map at {}: {}", map_path.display(), e))?;

        let mut builder = RingBufferBuilder::new();
        let buffer = self.buffer.clone();

        let collected_events = Arc::new(Mutex::new(Vec::new()));
        let events_clone = collected_events.clone();

        builder
            .add(&map, move |data: &[u8]| -> i32 {
                if data.len() < std::mem::size_of::<RawCortexEvent>() {
                    return 0;
                }
                // SAFETY: data.len() was checked >= size_of::<RawCortexEvent>() above; pointer is valid for read
                let event: RawCortexEvent =
                    unsafe { std::ptr::read_unaligned(data.as_ptr() as *const RawCortexEvent) };

                buffer.push(CortexEvent::from_raw_event(event));

                let mut events = events_clone.lock().unwrap();
                events.push(CortexEvent::from_raw_event(event));
                0
            })
            .map_err(|e| format!("Failed to add map to ring buffer: {}", e))?;

        let ringbuf = builder
            .build()
            .map_err(|e| format!("Could not build ringbuf: {}", e))?;

        let _ = ringbuf.poll(Duration::from_millis(timeout_ms));

        let events = collected_events.lock().unwrap();
        Ok(events.clone())
    }

    /// Handle incoming event from ring buffer
    #[allow(dead_code)]
    fn handle_event(&self, data: &[u8]) {
        if data.len() < std::mem::size_of::<RawCortexEvent>() {
            eprintln!("⚠️ Invalid event size: {}", data.len());
            return;
        }

        // SAFETY: We've verified the size matches RawCortexEvent
        let event: RawCortexEvent =
            unsafe { std::ptr::read_unaligned(data.as_ptr() as *const RawCortexEvent) };

        // Push CortexEvent to resonant buffer
        self.buffer.push(CortexEvent::from_raw_event(event));

        // Copy fields to avoid unaligned references in packed struct
        let event_type = event.event_type;
        let pid = event.pid;
        let entropy_signal = event.entropy_signal;
        let severity = event.severity;

        // Log for debugging
        eprintln!(
            "📡 eBPF Event: type={} pid={} entropy={} severity={}",
            event_type, pid, SPA::from_raw(entropy_signal as i64), severity
        );
    }

    /// Map event type to neuron ID
    #[allow(dead_code)]
    fn map_event_to_neuron(&self, event_type: u32) -> usize {
        match event_type {
            EVENT_FILE_BLOCKED => self.neuron_map.file_blocked,
            EVENT_EXEC_BLOCKED => self.neuron_map.exec_blocked,
            EVENT_FILE_ALLOWED => self.neuron_map.file_allowed,
            EVENT_EXEC_ALLOWED => self.neuron_map.exec_allowed,
            EVENT_NETWORK_BURST => self.neuron_map.network_burst,
            EVENT_NETWORK_NORMAL => self.neuron_map.network_normal,
            _ => 0, // Default to neuron 0
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_event_size() {
        // Verify struct size matches C definition (32 bytes)
        assert_eq!(std::mem::size_of::<RawCortexEvent>(), 32);
    }

    #[test]
    fn test_neuron_mapping() {
        let bridge = EbpfCortexBridge::new(Arc::new(ResonantBuffer::new()));

        assert_eq!(bridge.map_event_to_neuron(EVENT_FILE_BLOCKED), 0);
        assert_eq!(bridge.map_event_to_neuron(EVENT_EXEC_BLOCKED), 64);
        assert_eq!(bridge.map_event_to_neuron(EVENT_FILE_ALLOWED), 128);
    }

    #[test]
    fn test_handle_event() {
        let bridge = EbpfCortexBridge::new(Arc::new(ResonantBuffer::new()));

        // Create test event data directly as bytes
        let mut data = [0u8; 32];
        let event = RawCortexEvent {
            timestamp_ns: 1234567890,
            event_type: EVENT_FILE_BLOCKED,
            pid: 1000,
            entropy_signal: 39657600000, // High entropy (0.85)
            severity: SEVERITY_HIGH,
            _reserved: [0; 7],
        };

        // SAFETY: data buffer is 32 bytes; write to it with exact-size struct; only used in test
        unsafe {
            std::ptr::write_unaligned(data.as_mut_ptr() as *mut RawCortexEvent, event);
        }

        bridge.handle_event(&data);

        // Verify buffer has data
        assert!(bridge.buffer.pop().is_some());
    }
}
