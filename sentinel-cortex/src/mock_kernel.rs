use crate::ebpf_cortex_bridge::{CortexEvent, S60Entropy};
use tokio::sync::mpsc;
use std::time::{SystemTime, UNIX_EPOCH};
use tokio::time::{sleep, Duration};

pub struct MockKernelGenerator {
    pid_counter: u32,
}

impl MockKernelGenerator {
    pub fn new() -> Self {
        Self { pid_counter: 1000 }
    }

    fn generate_s60_entropy(seed: u64) -> S60Entropy {
        // Simulación determinista de entropía S60 (Sin Floats)
        // seed es nanosegundos
        let val = seed;
        
        let second = (val % 60) as u8;
        let val = val / 60;
        let minute = (val % 60) as u8;
        let val = val / 60;
        let degree = (val % 60) as u8;
        
        // Estabilidad calculada armónicamente
        let stability = (degree + minute + second) % 60;

        S60Entropy {
            raw_value: seed,
            degree,
            minute,
            second,
            tertia: 0, // Simplificado para mock
            stability,
        }
    }

    pub async fn run(&mut self, tx: mpsc::Sender<CortexEvent>) {
        tracing::info!("👻 PHANTOM MODE: Generating synthetic S60 kernel events...");
        
        loop {
            // Generar timestamp
            let start = SystemTime::now();
            let since_the_epoch = start
                .duration_since(UNIX_EPOCH)
                .expect("Time went backwards");
            let timestamp = since_the_epoch.as_nanos() as u64;

            // Simular actividad variada
            self.pid_counter = (self.pid_counter + 1) % 32768;
            if self.pid_counter < 1000 { self.pid_counter = 1000; }

            let event_type = match timestamp % 4 {
                0 => "EXEC".to_string(),
                1 => "OPEN".to_string(),
                2 => "NET".to_string(),
                _ => "BIO".to_string(),
            };

            let payload = format!("/bin/simulation_proc_{}", self.pid_counter);

            let event = CortexEvent {
                timestamp,
                pid: self.pid_counter,
                event_type,
                entropy: Self::generate_s60_entropy(timestamp),
                payload,
                cpu_id: 0,
            };

            // Enviar evento (Simulando Ring Buffer push)
            if let Err(e) = tx.send(event).await {
                tracing::error!("❌ Receiver dropped: {}", e);
                break;
            }

            // Ritmo de 17ms (Resonancia biológica simulada)
            sleep(Duration::from_millis(17)).await;
        }
    }
}
