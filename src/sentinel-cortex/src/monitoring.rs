use sysinfo::{System, Networks};
use serde::Serialize;
use std::sync::{Arc, Mutex};

#[derive(Serialize, Clone, Debug)]
pub struct SystemMetrics {
    pub cpu_usage: f32,
    pub total_memory: u64,
    pub used_memory: u64,
    pub uptime: u64,
    pub network_rx_bytes: u64,
    pub network_tx_bytes: u64,
}

#[derive(Clone)]
pub struct SystemMonitor {
    sys: Arc<Mutex<System>>,
    networks: Arc<Mutex<Networks>>,
}

impl SystemMonitor {
    pub fn new() -> Self {
        Self {
            sys: Arc::new(Mutex::new(System::new_all())),
            networks: Arc::new(Mutex::new(Networks::new_with_refreshed_list())),
        }
    }

    pub fn get_metrics(&self) -> SystemMetrics {
        let mut sys = self.sys.lock().unwrap();
        // Refresh system stats (CPU, Memory)
        sys.refresh_all();
        
        let mut networks = self.networks.lock().unwrap();
        // Refresh network stats
        networks.refresh(true);
        
        // sysinfo 0.30+: global_cpu_usage() returns f32 directly? Or use cpus().
        // If global_cpu_usage() exists, use it. 
        // Based on error: `method global_cpu_usage exists`.
        let cpu_usage = sys.global_cpu_usage(); 

        let total_memory = sys.total_memory();
        let used_memory = sys.used_memory();
        let uptime = System::uptime();
        
        // Aggregate network traffic
        // In 0.37, Networks is a struct, iterate via inner list? or iterator?
        // Networks implements IntoIterator? Or `iter()`.
        // Aggregate network traffic (Bytes since last refresh)
        let (rx, tx) = networks.iter().fold((0u64, 0u64), |acc, (_name, data)| {
            (acc.0 + data.received(), acc.1 + data.transmitted())
        });

        SystemMetrics {
            cpu_usage,
            total_memory,
            used_memory,
            uptime,
            network_rx_bytes: rx,
            network_tx_bytes: tx,
        }
    }
}
