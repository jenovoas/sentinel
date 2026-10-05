// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
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
    /// Guardian emisor (solo relevante para eventos Gamma 11-18).
    /// Codificado por Guardian-Gamma en _reserved[0]:
    /// 1=alpha, 2=cognitive, 3=ai, 4=float, 5=gamma. 0 = no aplica.
    pub guardian_code: u8,
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

        // SAFETY: data.len() was checked >= size_of::<CortexEventRaw>() on line 68; pointer is valid for read
        let raw: CortexEventRaw =
            unsafe { std::ptr::read_unaligned(data.as_ptr() as *const CortexEventRaw) };

        let event_type = match raw.event_type {
            1 => "FILE_BLOCKED".to_string(),
            2 => "EXEC_BLOCKED".to_string(),
            3 => "FILE_ALLOWED".to_string(),
            4 => "EXEC_ALLOWED".to_string(),
            5 => "NETWORK_BURST".to_string(),
            6 => "NETWORK_NORMAL".to_string(),
            7 => "SYSTEM_METRIC".to_string(),
            8 => "BIO_PULSE".to_string(),
            9 => "QHC_RESET".to_string(),
            10 => "FLOAT_CONTAMINATION".to_string(),
            11 => "GAMMA_PEER_MISSING".to_string(),
            12 => "GAMMA_DETACH_ATTEMPT".to_string(),
            13 => "GAMMA_MAP_TAMPER".to_string(),
            14 => "GAMMA_PEER_VANISHED".to_string(),
            15 => "GAMMA_PEER_SILENT".to_string(),
            16 => "GAMMA_INCONSISTENCY".to_string(),
            17 => "GAMMA_PEER_UNLOADED".to_string(),
            18 => "GAMMA_HEARTBEAT".to_string(),
            _ => "UNKNOWN".to_string(),
        };

        // _reserved[0] transporta guardian_code cuando el emisor es Gamma
        // (float_detector también lo usa con semántica compatible: 0).
        let guardian_code = raw._reserved[0];

        Some(CortexEvent {
            timestamp_ns: raw.timestamp_ns,
            pid: raw.pid,
            event_type,
            entropy_s60_raw: raw.entropy_signal,
            severity: raw.severity,
            guardian_code,
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

            loop {
                // 1. Intentar abrir el mapa pineado
                let map_res = std::panic::catch_unwind(|| {
                    MapHandle::from_pinned_path(&map_path)
                });

                let map = match map_res {
                    Ok(Ok(map)) => map,
                    Ok(Err(e)) => {
                        tracing::debug!("eBPF pinned map no disponible en {}: {}. Reintentando en 2s...", map_path, e);
                        std::thread::sleep(Duration::from_secs(2));
                        continue;
                    }
                    Err(_) => {
                        tracing::debug!("Pánico prevenido en MapHandle. Reintentando en 2s...");
                        std::thread::sleep(Duration::from_secs(2));
                        continue;
                    }
                };

                // 2. Construir RingBuffer
                let mut builder = RingBufferBuilder::new();
                let tx_clone = tx.clone();
                let buffer_clone = buffer.clone();

                if let Err(e) = builder.add(&map, move |data: &[u8]| -> i32 {
                    if let Some(event) = EbpfBridge::parse_event(data) {
                        if let Some(resonant) = &buffer_clone {
                            let entropy = S60::from_raw(event.entropy_s60_raw as i64);
                            resonant.push(entropy);
                        }
                        let _ = tx_clone.blocking_send(event);
                    }
                    0
                }) {
                    tracing::warn!("Fallo al añadir mapa a RingBufferBuilder: {}. Reintentando en 2s...", e);
                    std::thread::sleep(Duration::from_secs(2));
                    continue;
                }

                // 3. Polling continuo con reconexión ante error
                match builder.build() {
                    Ok(ringbuf) => {
                        tracing::info!("🔗 eBPF Cortex Bridge conectado con éxito al ringbuffer en {}", map_path);
                        loop {
                            if let Err(e) = ringbuf.poll(Duration::from_millis(100)) {
                                tracing::warn!("RingBuf poll status: {:?}. Reconectando...", e);
                                std::thread::sleep(Duration::from_millis(500));
                                break;
                            }
                        }
                    }
                    Err(e) => {
                        tracing::warn!("Fallo al construir RingBuffer: {:?}. Reintentando...", e);
                        std::thread::sleep(Duration::from_secs(2));
                    }
                }
            }
        })
        .await??;

        Ok(())
    }
}
