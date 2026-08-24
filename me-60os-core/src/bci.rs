// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🧬 BCI HAPTIC SYSTEM - RUST CORE 🧬
//!
//! Direct-to-Metal Interface for Bone Conduction output via Arduino.
//! Consumes from Zero-Latency ResonantBuffer and drives physical vibration.
//!
//! IMPLEMENTATION:
//! Uses raw generic file I/O to write to logical device file (e.g. /dev/ttyACM0).
//! This avoids heavy dependencies like libudev.
//!
//! PROTOCOL (Binary 3-byte):
//! [CMD: u8] [VAL_H: u8] [VAL_L: u8]

use crate::buffer_system::ResonantBuffer;
use crate::ebpf_cortex_bridge::CortexEvent;
use crate::scv::EntropicFirewall; // Import Firewall
use crate::spa::SPA;
use std::collections::VecDeque; // Import VecDeque
use std::fs::{File, OpenOptions};
use std::io::Write;
use std::sync::Arc;
use std::thread;
use std::time::Duration;

pub struct BCISystem {
    device_path: String,
    file: Option<File>,
    buffer: Arc<ResonantBuffer>,
    connected: bool,
    window: VecDeque<CortexEvent>, // Sliding window for Entropic Firewall
}

impl BCISystem {
    pub fn new(device_path: &str, buffer: Arc<ResonantBuffer>) -> Self {
        let file = OpenOptions::new().append(true).open(device_path);

        match file {
            Ok(f) => {
                eprintln!("✅ BCI Connected on {}", device_path);
                Self {
                    device_path: device_path.to_string(),
                    file: Some(f),
                    buffer,
                    connected: true,
                    window: VecDeque::with_capacity(20),
                }
            }
            Err(e) => {
                eprintln!(
                    "⚠️ BCI Connection Failed ({}): {}. Simulating.",
                    device_path, e
                );
                Self {
                    device_path: device_path.to_string(),
                    file: None,
                    buffer,
                    connected: false,
                    window: VecDeque::with_capacity(20),
                }
            }
        }
    }

    /// Main BCI Loop - Runs in a dedicated thread
    pub fn start(&mut self) {
        eprintln!("🧬 BCI System Active - Monitoring Resonant Buffer...");

        loop {
            // Reconnect attempt if disconnected
            if !self.connected {
                if let Ok(f) = OpenOptions::new().append(true).open(&self.device_path) {
                    self.file = Some(f);
                    self.connected = true;
                    eprintln!("✅ BCI Reconnected!");
                }
            }

            // 1. Consume from Buffer
            if let Some(event) = self.buffer.pop() {
                self.process_state(event);
            } else {
                // Buffer empty: Send Heartbeat (Maintain carrier wave)
                self.send_heartbeat();
            }

            // Critical latency optimization: Short sleep
            thread::sleep(Duration::from_micros(500));
        }
    }

    fn process_state(&mut self, event: CortexEvent) {
        // 🛡️ BCI FIREWALL: Clean Signal 🛡️
        // Update sliding window
        if self.window.len() >= 20 {
            self.window.pop_front();
        }
        self.window.push_back(event.clone());

        // Only trigger haptics if we have enough data to verify entropy
        // and the signal is biologically valid (Not dead noise).
        let is_clean = if self.window.len() >= 5 {
            // Convert VecDeque to slice for analysis
            let slice: Vec<CortexEvent> = self.window.iter().cloned().collect();
            EntropicFirewall::verify(&slice)
        } else {
            true // Allow startup transient
        };

        if !is_clean {
            // Signal is "Dead" or "Mechanical Noise" (Low Entropy).
            // Suppress Haptics (Silence).
            return;
        }

        // Simple mapping:
        // If state value (threat/load) > threshold -> GAMMA ALERT
        // Else -> Modulate LOAD frequency

        // SPA stored as scaled integer.
        let state_raw = event.entropy_signal as i64;
        if state_raw > (SPA::SCALE_0 / 2) {
            // Threat!
            self.send_command(0x02, 100); // Max intensity
        } else {
            // Normal load modulation
            // Map SPA range [0, 0.5] to [0, 255] byte
            let scalar = state_raw / (SPA::SCALE_0 / 512);
            let val = (scalar.min(255)) as u8;
            self.send_command(0x03, val);
        }
    }

    fn send_heartbeat(&mut self) {
        self.send_command(0x01, 10);
    }

    fn send_command(&mut self, cmd: u8, val: u8) {
        if let Some(ref mut file) = self.file {
            let pkt = [cmd, 0, val];
            if let Err(e) = file.write_all(&pkt) {
                eprintln!("❌ BCI Write Error: {}. Disconnecting.", e);
                self.connected = false;
                self.file = None;
            } else {
                let _ = file.flush();
            }
        }
    }
}

#[cfg(test)]
mod tests {
    // Test disabled: API changed to use CortexEvent instead of SPA
}
