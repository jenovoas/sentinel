// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
use crate::ebpf_cortex_bridge::CortexEvent;
use tokio::sync::mpsc;
use std::time::{SystemTime, UNIX_EPOCH};
use tokio::time::{sleep, Duration};

pub struct MockKernelGenerator {
    pid_counter: u32,
}

pub struct MockS60Entropy {
    pub raw_value: u64,
    pub degree: u8,
    pub minute: u8,
    pub second: u8,
    pub tertia: u8,
    pub stability: u8,
}

impl MockKernelGenerator {
    pub fn new() -> Self {
        Self { pid_counter: 1000 }
    }

    fn generate_s60_entropy(seed: u64) -> MockS60Entropy {
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

        MockS60Entropy {
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

            let entropy_sim = Self::generate_s60_entropy(timestamp);
            let event = CortexEvent {
                timestamp_ns: timestamp,
                pid: self.pid_counter,
                event_type,
                entropy_s60_raw: entropy_sim.raw_value,
                severity: 1, // mock
                guardian_code: 0,
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

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::sync::mpsc;
    use tokio::time::timeout;
    use std::time::Duration;

    #[test]
    fn test_determinism_s60_entropy() {
        let ts_a = 1680000000000000000;
        let entropy_a = MockKernelGenerator::generate_s60_entropy(ts_a);
        
        // Reglas estrictas de S60 (Base 60)
        assert!(entropy_a.degree < 60, "S60 Degree out of bounds");
        assert!(entropy_a.minute < 60, "S60 Minute out of bounds");
        assert!(entropy_a.second < 60, "S60 Second out of bounds");
        assert!(entropy_a.stability < 60, "S60 Stability out of bounds");
        
        let ts_b = ts_a + 500000;
        let entropy_b = MockKernelGenerator::generate_s60_entropy(ts_b);
        assert_ne!(entropy_a.raw_value, entropy_b.raw_value, "Raw values must differ given different timestamps");
    }

    #[tokio::test]
    async fn test_mock_kernel_stream() {
        let (tx, mut rx) = mpsc::channel(10);
        let mut mock = MockKernelGenerator::new();

        // Lanzar el núcleo fantasma
        tokio::spawn(async move {
            mock.run(tx).await;
        });

        // Testear recepción MPSC en vivo (Timeout de seguridad)
        for _ in 0..3 {
            let event = timeout(Duration::from_millis(50), rx.recv()).await;
            assert!(event.is_ok(), "El MPSC Channel falló en latencia de Resonancia S60 (<17ms esperados)");
            
            let cortex_event = event.unwrap().expect("Stream cerrado prematuramente");
            assert!(cortex_event.pid >= 1000, "El PID del mock Kernel es inválido");
            assert!(
                ["EXEC", "OPEN", "NET", "BIO"].contains(&cortex_event.event_type.as_str()),
                "Payload de tipo EventType irreconocible"
            );
        }
    }
}
