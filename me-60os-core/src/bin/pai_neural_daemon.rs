// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/bin/pai_neural_daemon.rs
//! PAI‑60 Neural Daemon
//! Polls eBPF ring buffer, converts entropy to SPA, and updates neural memory.

use libbpf_rs::{MapHandle, RingBufferBuilder};
use me60os_core::ebpf_cortex_bridge::{CortexEvent, RawCortexEvent};
use me60os_core::neural_memory::NeuralMemory;
use me60os_core::spa::SPA;
use std::path::Path;
use std::time::Duration;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🛡️ ME‑60OS: PAI‑60 Neural Daemon Starting...");

    // 1. Initialize Neural Memory
    let mut memory = NeuralMemory::new();

    // 2. Open eBPF Ring Buffer
    // Sentinel Guardian LSM uses /sys/fs/bpf/cortex_events (or legacy fallback)
    let ringbuf_path = if Path::new("/sys/fs/bpf/cortex_events").exists() {
        "/sys/fs/bpf/cortex_events"
    } else if Path::new("/sys/fs/bpf/sentinel/events").exists() {
        "/sys/fs/bpf/sentinel/events"
    } else {
        "/sys/fs/bpf/cortex_events"
    };

    let map = MapHandle::from_pinned_path(ringbuf_path)
        .map_err(|e| format!("Failed to open pinned map at {}: {}", ringbuf_path, e))?;

    println!("✅ Ring buffer map opened: {}", ringbuf_path);

    // 3. Setup Ring Buffer Polling
    let mut builder = RingBufferBuilder::new();

    // We use a closure that captures the memory.
    // Note: NeuralMemory is not Thread-Safe by default, but RingBuffer callback
    // runs in the polling thread synchronously for each event.
    builder.add(&map, move |data: &[u8]| -> i32 {
        if data.len() < std::mem::size_of::<RawCortexEvent>() {
            return 0;
        }

        // SAFETY: Size is verified.
        let raw_ev: RawCortexEvent =
            unsafe { std::ptr::read_unaligned(data.as_ptr() as *const RawCortexEvent) };

        // Convert raw entropy signal to SPA
        let entropy_spa = SPA::from_raw(raw_ev.entropy_signal as i64);

        // Convert to high-level CortexEvent
        let ev = CortexEvent::new(
            raw_ev.timestamp_ns,
            raw_ev.event_type,
            raw_ev.pid,
            raw_ev.entropy_signal,
            raw_ev.severity,
        );

        // Update Neural Memory
        memory.ingest_event(ev, entropy_spa);

        0 // Continue polling
    })?;

    let ringbuf = builder.build()?;

    println!("🚀 Daemon Active. Polling for events...");

    // 4. Main Loop
    loop {
        match ringbuf.poll(Duration::from_millis(100)) {
            Ok(_) => (),
            Err(e) => {
                eprintln!("⚠️ Poll error: {}", e);
                std::thread::sleep(Duration::from_millis(500));
            }
        }
    }
}
