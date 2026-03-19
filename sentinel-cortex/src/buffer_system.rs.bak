//! # 🛡️ ZERO-LATENCY BUFFER SYSTEM - SENTINEL CORTEX 🛡️
//!
//! High-performance ring buffer for Quantum/Hardware bridge.
//! Implements lock-free access for S60 data streams.
//!
//! ARCHITECTURE:
//! - Double-Buffered Rings (Read/Write strict separation)
//! - Base-60 Alignment (Buffer sizes are multiples of 60)
//! - Atomic control indices for zero-latency sync

use crate::math::s60::S60;
use std::cell::UnsafeCell;
use std::sync::atomic::{AtomicUsize, Ordering};

/// Constants
pub const BUFFER_SIZE_S60: usize = 3600; // 60^2 blocks
const CACHE_LINE_SIZE: usize = 64;

/// Zero-Latency Ring Buffer
/// Designed for single-producer, single-consumer (SPSC) lock-free access.
pub struct ResonantBuffer {
    data: Box<[UnsafeCell<S60>]>,
    head: AtomicUsize,               // Write index
    tail: AtomicUsize,               // Read index
    _padding: [u8; CACHE_LINE_SIZE], // Reduce false sharing
}

// SAFETY: SPSC access pattern assumed.
// Sync is safe because head/tail are atomic and buffer is fixed size.
unsafe impl Sync for ResonantBuffer {}

impl ResonantBuffer {
    /// Create a new resonant buffer aligned to S60 harmonics.
    pub fn new() -> Self {
        let mut vec = Vec::with_capacity(BUFFER_SIZE_S60);
        for _ in 0..BUFFER_SIZE_S60 {
            vec.push(UnsafeCell::new(S60::new(0, 0, 0, 0, 0).unwrap()));
        }

        Self {
            data: vec.into_boxed_slice(),
            head: AtomicUsize::new(0),
            tail: AtomicUsize::new(0),
            _padding: [0; CACHE_LINE_SIZE],
        }
    }

    /// Write a single harmonic quantum packet (S60) to the buffer.
    /// Returns true if successful, false if buffer full (Backpressure).
    pub fn push(&self, value: S60) -> bool {
        let head = self.head.load(Ordering::Relaxed);
        let tail = self.tail.load(Ordering::Acquire);

        let next_head = (head + 1) % BUFFER_SIZE_S60;

        if next_head == tail {
            return false; // Full (Harmonic Saturation)
        }

        // Write data
        unsafe {
            *self.data[head].get() = value;
        }

        // Commit write
        self.head.store(next_head, Ordering::Release);
        true
    }

    /// Read a single harmonic quantum packet.
    /// Returns Some(S60) or None if empty.
    pub fn pop(&self) -> Option<S60> {
        let tail = self.tail.load(Ordering::Relaxed);
        let head = self.head.load(Ordering::Acquire);

        if tail == head {
            return None; // Empty (Vacuum State)
        }

        // Read data
        let value = unsafe { *self.data[tail].get() };

        // Commit read
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
        // 3600 capacity -> count/60 = degrees
        let degrees = (count as i64 * 60) / BUFFER_SIZE_S60 as i64;
        S60::new(degrees as i32, 0, 0, 0, 0).unwrap()
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
                while !writer_buf.push(S60::new(i, 0, 0, 0, 0).unwrap()) {
                    // spin
                }
            }
        });

        let t2 = thread::spawn(move || {
            let mut sum = S60::new(0, 0, 0, 0, 0).unwrap();
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
        assert_eq!(final_sum.to_base_units() / S60::SCALE_0, 4950);
    }
}
