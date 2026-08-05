// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/buffer_system/resonant_buffer.rs! # 🛡️ ZERO-LATENCY BUFFER SYSTEM - SENTINEL CORTEX 🛡️
//!
//! High-performance ring buffer for Quantum/Hardware bridge.
//! Implements lock-free access for S60 data streams.
//
// Lock-free ring buffer primitives; pending integration with the
// collector pipeline. Silenced at module level.
#![allow(dead_code)]

use crate::math::s60::S60;
use std::cell::UnsafeCell;
use std::sync::atomic::{AtomicUsize, Ordering};

/// Constants
pub const BUFFER_SIZE_S60: usize = 3600; // 60^2 blocks
const CACHE_LINE_SIZE: usize = 64;

/// Zero-Latency Ring Buffer
pub struct ResonantBuffer {
    data: Box<[UnsafeCell<S60>]>,
    head: AtomicUsize,               // Write index
    tail: AtomicUsize,               // Read index
    _padding: [u8; CACHE_LINE_SIZE], // Reduce false sharing
}

unsafe impl Sync for ResonantBuffer {}

impl ResonantBuffer {
    /// Create a new resonant buffer aligned to S60 harmonics.
    pub fn new() -> Self {
        let mut vec = Vec::with_capacity(BUFFER_SIZE_S60);
        for _ in 0..BUFFER_SIZE_S60 {
            vec.push(UnsafeCell::new(S60::zero()));
        }

        Self {
            data: vec.into_boxed_slice(),
            head: AtomicUsize::new(0),
            tail: AtomicUsize::new(0),
            _padding: [0; CACHE_LINE_SIZE],
        }
    }

    /// Write a single harmonic quantum packet (S60) to the buffer.
    pub fn push(&self, value: S60) -> bool {
        let head = self.head.load(Ordering::Relaxed);
        let tail = self.tail.load(Ordering::Acquire);

        let next_head = (head + 1) % BUFFER_SIZE_S60;
        if next_head == tail {
            return false; // Full
        }

        unsafe {
            *self.data[head].get() = value;
        }

        self.head.store(next_head, Ordering::Release);
        true
    }

    /// Read a single harmonic quantum packet.
    pub fn pop(&self) -> Option<S60> {
        let tail = self.tail.load(Ordering::Relaxed);
        let head = self.head.load(Ordering::Acquire);

        if tail == head {
            return None; // Empty
        }

        let value = unsafe { *self.data[tail].get() };
        let next_tail = (tail + 1) % BUFFER_SIZE_S60;
        self.tail.store(next_tail, Ordering::Release);

        Some(value)
    }

    /// Current occupancy (Load Factor).
    pub fn load_factor(&self) -> S60 {
        let head = self.head.load(Ordering::Relaxed);
        let tail = self.tail.load(Ordering::Relaxed);

        let count = if head >= tail {
            head - tail
        } else {
            BUFFER_SIZE_S60 - tail + head
        };

        // Convert count to percentage S60 (0-60 degrees roughly)
        let degrees = (count as i64 * 60) / BUFFER_SIZE_S60 as i64;
        S60::from_int(degrees as i32)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Arc;
    use std::thread;

    #[test]
    fn test_spsc_flow() {
        let buffer = Arc::new(ResonantBuffer::new());
        let writer_buf = buffer.clone();
        let reader_buf = buffer.clone();

        let t1 = thread::spawn(move || {
            for i in 0..100 {
                while !writer_buf.push(S60::from_int(i)) {
                    // spin
                }
            }
        });

        let t2 = thread::spawn(move || {
            let mut sum = S60::zero();
            let mut count = 0;
            while count < 100 {
                if let Some(val) = reader_buf.pop() {
                    sum = sum + val;
                    count += 1;
                }
            }
            sum
        });

        t1.join().unwrap();
        let final_sum = t2.join().unwrap();

        // Sum 0..99 = 4950
        // Bug preexistente: `S60::to_raw()` no existe en sentinel-cortex (es de
        // `SPA` en me-60os). Aquí se usa el equivalente `to_base_units()`.
        assert_eq!(final_sum.to_base_units() / S60::SCALE_0, 4950);
    }
}
