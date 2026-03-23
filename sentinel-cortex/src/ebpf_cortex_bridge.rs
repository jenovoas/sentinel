use crate::buffer_system::ResonantBuffer;
use crate::math::s60::S60;
use serde::{Deserialize, Serialize};
use std::path::Path;
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::mpsc;

// Mirroring C structs from cortex_events.h
// #[repr(C)] ensures C-compatible memory layout
// Matching the 32-byte struct cortex_event from cortex_events.h
#[repr(C, packed)]
#[derive(Debug, Clone, Copy)]
pub struct CortexEventRaw {
    pub timestamp_ns: u64,
    pub event_type: u32,
    pub pid: u32,
    pub entropy_signal: u64,
    pub severity: u8,
    pub _reserved: [u8; 7],
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CortexEvent {
    pub timestamp_ns: u64,
    pub pid: u32,
    pub event_type: String,
    pub entropy_s60_raw: u64,
    pub severity: u8,
}

#[allow(dead_code)]
pub struct EbpfBridge {
    // skel: Option<Skel>, // In a real impl, we'd hold the BPF skeleton here
    ringbuf_path: Option<String>,
    buffer: Option<Arc<ResonantBuffer>>,
}

#[allow(dead_code)]
impl EbpfBridge {
    pub fn new() -> Self {
        Self {
            ringbuf_path: None,
            buffer: None,
        }
    }

    /// Attach a resonant buffer for zero-copy S60 ingestion.
    pub fn with_buffer(mut self, buffer: Arc<ResonantBuffer>) -> Self {
        self.buffer = Some(buffer);
        self
    }

    /// Set ring buffer path (pinned map or directory).
    pub fn with_ringbuf_path(mut self, ringbuf_path: impl Into<String>) -> Self {
        self.ringbuf_path = Some(ringbuf_path.into());
        self
    }

    pub fn parse_event(data: &[u8]) -> Option<CortexEvent> {
        if data.len() < std::mem::size_of::<CortexEventRaw>() {
            return None;
        }

        let raw: CortexEventRaw =
            unsafe { std::ptr::read_unaligned(data.as_ptr() as *const CortexEventRaw) };

        let event_type = match raw.event_type {
            1 => "FILE_BLOCKED".to_string(), // EVENT_FILE_BLOCKED
            2 => "EXEC_BLOCKED".to_string(),
            3 => "FILE_ALLOWED".to_string(),
            4 => "EXEC_ALLOWED".to_string(),
            5 => "NETWORK_BURST".to_string(),
            6 => "NETWORK_NORMAL".to_string(),
            7 => "SYSTEM_METRIC".to_string(),
            8 => "BIO_PULSE".to_string(),
            9 => "QHC_RESET".to_string(),
            _ => "UNKNOWN".to_string(),
        };

        Some(CortexEvent {
            timestamp_ns: raw.timestamp_ns,
            pid: raw.pid,
            event_type,
            entropy_s60_raw: raw.entropy_signal,
            severity: raw.severity,
        })
    }

    /// Start ring buffer polling loop (blocking).
    ///
    /// This consumes the pinned ring buffer map and forwards events to:
    /// - the optional ResonantBuffer (S60 ingestion)
    /// - the provided Tokio channel (CortexEvent stream)
    pub async fn run_monitor(&self, tx: mpsc::Sender<CortexEvent>) -> anyhow::Result<()> {
        let ringbuf_path = self
            .ringbuf_path
            .clone()
            .ok_or_else(|| anyhow::anyhow!("ringbuf_path is required for EbpfBridge"))?;

        let buffer = self.buffer.clone();

        tracing::info!("Starting eBPF Cortex Bridge Monitor...");

        tokio::task::spawn_blocking(move || -> anyhow::Result<()> {
            use libbpf_rs::{MapHandle, RingBufferBuilder};

            // Accept either pinned map file or directory containing cortex_events
            let map_path = if Path::new(&ringbuf_path).is_dir() {
                format!("{}/cortex_events", ringbuf_path)
            } else {
                ringbuf_path
            };

            let map = MapHandle::from_pinned_path(&map_path)
                .map_err(|e| anyhow::anyhow!("Failed to open pinned map at {}: {}", map_path, e))?;

            let mut builder = RingBufferBuilder::new();
            let tx = tx.clone();
            let buffer = buffer.clone();

            builder.add(&map, move |data: &[u8]| -> i32 {
                if let Some(event) = EbpfBridge::parse_event(data) {
                    if let Some(ref resonant) = buffer {
                        let entropy = S60::from_raw(event.entropy_s60_raw as i64);
                        resonant.push(entropy);
                    }

                    let _ = tx.blocking_send(event);
                }
                0
            })?;

            let mut ringbuf = builder.build()?;

            loop {
                ringbuf.poll(Duration::from_millis(100))?;
            }
        })
        .await??;

        Ok(())
    }
}
