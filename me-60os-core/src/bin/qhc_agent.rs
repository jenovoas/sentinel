// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 🔱 QHC AGENT (Harmonic Phase Driver)
//! =====================================
//! Agente que mantiene el pulso 10;5,6,5 del sistema.
//! Reemplazo de `yhwh_driver.py`.

use me60os_core::qhc::QhcTensor;
use me60os_core::qhc_ipc::{socket_path, QhcSnapshot};
use parking_lot::Mutex;
use std::{
    fs,
    io::{BufRead, BufReader, Write},
    os::unix::net::{UnixListener, UnixStream},
    path::PathBuf,
    sync::Arc,
    thread,
    time::Duration,
};

struct QhcAgent {
    tensor: QhcTensor,
    ticks: u64,
    snapshot: Arc<Mutex<QhcSnapshot>>,
}

impl QhcAgent {
    pub fn new() -> Self {
        Self {
            tensor: QhcTensor::new(),
            ticks: 0,
            snapshot: Arc::new(Mutex::new(QhcSnapshot::from_tick(0, 10, 0))),
        }
    }

    pub fn run_loop(&mut self) {
        println!("🔱 QHC AGENT ONLINE (Phase Modulator 10;5,6,5)");
        self.start_ipc();

        loop {
            self.tick();
            thread::sleep(Duration::from_secs(1)); // 1s Tick Base
        }
    }

    fn start_ipc(&self) {
        let snapshot = Arc::clone(&self.snapshot);
        let path = socket_path();
        thread::spawn(move || {
            if let Err(error) = serve_socket(path, snapshot) {
                eprintln!("QHC IPC stopped: {error}");
            }
        });
    }

    fn tick(&mut self) {
        let modulation = self.tensor.get_phase_modulation(self.ticks);
        let correction = self.tensor.calculate_drift_correction(self.ticks);
        let snapshot = QhcSnapshot::from_tick(self.ticks, modulation, correction);

        // Visual Heartbeat
        if correction > 0 {
            println!(
                "🔄 TICK {:04} | Phase: {} | ⚠️ SALTO-17 CORRECTION: {}ns",
                self.ticks, snapshot.phase, correction
            );
        } else {
            println!(
                "🔹 TICK {:04} | Pattern: {} | Mod: {}",
                self.ticks, snapshot.phase, modulation
            );
        }

        *self.snapshot.lock() = snapshot;
        self.ticks += 1;
    }
}

fn serve_socket(path: PathBuf, snapshot: Arc<Mutex<QhcSnapshot>>) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    let _ = fs::remove_file(&path);
    let listener = UnixListener::bind(&path)?;
    fs::set_permissions(&path, fs::Permissions::from_mode(0o660))?;
    println!("QHC IPC listening on {}", path.display());

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                if let Err(error) = handle_client(stream, &snapshot) {
                    eprintln!("QHC IPC client error: {error}");
                }
            }
            Err(error) => eprintln!("QHC IPC accept error: {error}"),
        }
    }

    Ok(())
}

fn handle_client(mut stream: UnixStream, snapshot: &Arc<Mutex<QhcSnapshot>>) -> std::io::Result<()> {
    let mut request = String::new();
    BufReader::new(stream.try_clone()?).read_line(&mut request)?;
    let response = match request.trim() {
        "" | "GET_PHASE" | "SNAPSHOT" => {
            serde_json::to_vec(&*snapshot.lock()).map_err(std::io::Error::other)?
        }
        _ => serde_json::to_vec(&serde_json::json!({
            "error": "unsupported_request",
            "supported": ["GET_PHASE", "SNAPSHOT"],
        }))
        .map_err(std::io::Error::other)?,
    };
    stream.write_all(&response)?;
    stream.write_all(b"\n")?;
    stream.flush()
}

#[cfg(unix)]
use std::os::unix::fs::PermissionsExt;

fn main() {
    let mut agent = QhcAgent::new();
    agent.run_loop();
}
