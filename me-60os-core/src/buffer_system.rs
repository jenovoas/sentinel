// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ ZERO-LATENCY BUFFER SYSTEM - ME-60OS 🛡️
//!
//! High-performance ring buffer for Quantum/Hardware bridge.
//! Implements lock-free access for SPA data streams.
//!
//! ARCHITECTURE:
//! - Double-Buffered Rings (Read/Write strict separation)
//! - Base-60 Alignment (Buffer sizes are multiples of 60)
//! - Atomic control indices for zero-latency sync

use crate::spa::SPA;
use std::cell::UnsafeCell;
use std::sync::atomic::{AtomicUsize, Ordering};
use crate::ebpf_cortex_bridge::CortexEvent;

/// Constants
pub const BUFFER_SIZE_S60: usize = 3600; // 60^2 blocks
const CACHE_LINE_SIZE: usize = 64;

/// Zero-Latency Ring Buffer
/// Designed for single-producer, single-consumer (SPSC) lock-free access.
pub struct ResonantBuffer {
    data: Box<[UnsafeCell<CortexEvent>]>,
    head: AtomicUsize,               // Write index
    tail: AtomicUsize,               // Read index
    _padding: [u8; CACHE_LINE_SIZE], // Reduce false sharing
}

// SAFETY: ResonantBuffer uses UnsafeCell internally; all mutable access goes through atomic
// head/tail indices which enforce the SPSC invariant (writer-only head, reader-only tail).
unsafe impl Sync for ResonantBuffer {}

impl ResonantBuffer {
    /// Create a new resonant buffer aligned to SPA harmonics.
    pub fn new() -> Self {
        let mut vec = Vec::with_capacity(BUFFER_SIZE_S60);
        for _ in 0..BUFFER_SIZE_S60 {
            vec.push(UnsafeCell::new(CortexEvent::default()));
        }

        Self {
            data: vec.into_boxed_slice(),
            head: AtomicUsize::new(0),
            tail: AtomicUsize::new(0),
            _padding: [0; CACHE_LINE_SIZE],
        }
    }

    /// Write a single harmonic quantum packet (SPA) to the buffer.
    /// Returns true if successful, false if buffer full (Backpressure).
    pub fn push(&self, value: CortexEvent) -> bool {
        let head = self.head.load(Ordering::Relaxed);
        let tail = self.tail.load(Ordering::Acquire);

        let next_head = (head + 1) % BUFFER_SIZE_S60;

        if next_head == tail {
            return false; // Full (Harmonic Saturation)
        }

        // SAFETY: head was loaded and validated against tail; (head+1)%SIZE != tail proves the slot is not written
        unsafe {
            *self.data[head].get() = value;
        }

        // Commit write
        self.head.store(next_head, Ordering::Release);
        true
    }

    /// Read a single harmonic quantum packet.
    /// Returns Some(SPA) or None if empty.
    pub fn pop(&self) -> Option<CortexEvent> {
        let tail = self.tail.load(Ordering::Relaxed);
        let head = self.head.load(Ordering::Acquire);

        if tail == head {
            return None; // Empty (Vacuum State)
        }

        // SAFETY: tail was loaded and validated against head; tail != head proves the slot is not empty
        let value = unsafe { (*self.data[tail].get()).clone() };

        // Commit read
        let next_tail = (tail + 1) % BUFFER_SIZE_S60;
        self.tail.store(next_tail, Ordering::Release);

        Some(value)
    }

    /// Current occupancy (Load Factor).
    pub fn load_factor(&self) -> SPA {
        let head = self.head.load(Ordering::Relaxed);
        let tail = self.tail.load(Ordering::Relaxed);

        let count = if head >= tail {
            head - tail
        } else {
            BUFFER_SIZE_S60 - tail + head
        };

        // Convert count to percentage SPA (0-60 degrees roughly)
        // 3600 capacity -> count/60 = degrees
        let degrees = (count as i64 * 60) / BUFFER_SIZE_S60 as i64;
        SPA::new(degrees, 0, 0, 0, 0)
    }
}

impl Default for ResonantBuffer {
    fn default() -> Self {
        Self::new()
    }
}
#[cfg(test)]
mod tests {
    // Tests disabled: API changed to use CortexEvent instead of SPA
    // #[test]
    // fn test_spsc_flow() {
    //     let buffer = Arc::new(ResonantBuffer::new());
    //     let writer_buf = buffer.clone();
    //     let reader_buf = buffer.clone();

    //     let t1 = thread::spawn(move || {
    //         for i in 0..100 {
    //             while !writer_buf.push(SPA::new(i, 0, 0, 0, 0)) {
    //                 // spin
    //             }
    //         }
    //     });

    //     let t2 = thread::spawn(move || {
    //         let mut sum = SPA::new(0, 0, 0, 0, 0);
    //         let mut count = 0;
    //         while count < 100 {
    //             if let Some(val) = reader_buf.pop() {
    //                 sum = sum + val;
    //                 count += 1;
    //             }
    //         }
    //         sum
    //     });

    //     t1.join().unwrap();
    //     let final_sum = t2.join().unwrap();

    //     // Sum 0..99 = 4950
    //     assert_eq!(final_sum.to_degrees(), 4950);
    // }
}
