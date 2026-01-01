use tauri::command;
use serde::Serialize;
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Serialize)]
struct SystemVector {
    entropy: f64,
    coherence: f64,
    tte_us: f64,
}

use std::process::Command;

#[derive(Serialize)]
struct SystemVector {
    entropy: f64,
    coherence: f64,
    tte_us: f64,
}

#[command]
fn get_system_vector() -> SystemVector {
    // Read from /var/run/sentinel/truthsync_shm (Bytes 0-32)
    // Structure: [entropy(f64) | coherence(f64) | tte_us(f64) | timestamp(u64)]
    
    use std::fs::OpenOptions;
    use std::io::{Read, Seek, SeekFrom};
    use std::mem;

    let shm_path = "/var/run/sentinel/truthsync_shm";
    
    // Fallback if SHM not ready
    let default_vector = SystemVector {
        entropy: 0.0,
        coherence: 0.0,
        tte_us: 0.0,
    };

    let mut file = match OpenOptions::new().read(true).open(shm_path) {
        Ok(f) => f,
        Err(_) => return default_vector,
    };

    let mut buffer = [0u8; 32]; // 3 doubles (24) + 1 u64 (8) = 32 bytes
    if file.read_exact(&mut buffer).is_err() {
        return default_vector;
    }

    // Unsafe transmutation to read f64s from bytes
    // Note: This assumes Little Endian which is standard for x86_64 Linux
    let entropy = f64::from_le_bytes(buffer[0..8].try_into().unwrap_or([0; 8]));
    let coherence = f64::from_le_bytes(buffer[8..16].try_into().unwrap_or([0; 8]));
    let tte_us = f64::from_le_bytes(buffer[16..24].try_into().unwrap_or([0; 8]));
    
    SystemVector {
        entropy,
        coherence,
        tte_us
    }
}

#[command]
async fn execute_semantic_command(prompt: String) -> String {
    // Bridge to Python SemSH (The Brain)
    // We call python3 sem_shell.py with an argument or input
    // Ideally sem_shell.py needs a "one-shot" mode for this integration.
    // For now we will mock the response in Rust to ensure the pipes work
    // or call a specific "process_intent" script if available.
    
    // Simulating Llama 3.2 processing delay
    std::thread::sleep(std::time::Duration::from_millis(800));
    
    // In a real scenario, this executes:
    // python3 scripts/intent_processor.py "{prompt}"
    
    // For prototype v0.4, we return a mock success message to prove the loop
    format!("> Intent analyzed: '{}'.\n> [SEM_SH] Vector approved by LSM (TTE: 3.23us).\n> Executing: ls -la /var/log/sentinel...", prompt)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![get_system_vector, execute_semantic_command])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
