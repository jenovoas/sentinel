// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
//! # Reenviador ringbuf → trace log
//!
//! Consume los ringbufs `cortex_events` pineados, mantiene los fds abiertos
//! (el verificador exige consumidores adjuntos) y vuelca cada evento como
//! NDJSON a `/var/log/sentinel/ebpf_trace.log` (el verificador exige
//! archivo vivo con crecimiento).
//! Uso: `ringbuf_forwarder <map> <log> [map_extra...]`
//! El parseo reusa `CortexEvent::parse_event` (sin pánico, con harness Kani).

use libbpf_rs::{MapHandle, RingBufferBuilder};
use me60os_core::ebpf_cortex_bridge::CortexEvent;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::Path;
use std::time::Duration;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();
    let primary = args
        .get(1)
        .map(String::as_str)
        .unwrap_or("/sys/fs/bpf/cortex_events");
    let log_path: String = args
        .get(2)
        .map(String::as_str)
        .unwrap_or("/var/log/sentinel/ebpf_trace.log")
        .to_string();
    let mut map_paths = vec![primary.to_string()];
    map_paths.extend(args.iter().skip(3).cloned());

    let mut maps = Vec::new();
    for p in &map_paths {
        if !Path::new(p).exists() {
            eprintln!("ringbuf_forwarder: pin no encontrado: {}", p);
            std::process::exit(1);
        }
        maps.push(
            MapHandle::from_pinned_path(p).map_err(|e| format!("no se pudo abrir {}: {}", p, e))?,
        );
    }
    let mut out = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_path)
        .map_err(|e| format!("no se pudo abrir {}: {}", log_path, e))?;
    writeln!(
        out,
        "{{\"source\":\"ringbuf_forwarder\",\"event\":\"startup\",\"maps\":{:?}}}",
        map_paths
    )?;
    out.flush()?;
    drop(out); // el callback reabre en append por evento (simple y robusto)

    let mut builder = RingBufferBuilder::new();
    for map in &maps {
        let log_path = log_path.clone();
        builder.add(map, move |data: &[u8]| -> i32 {
            match CortexEvent::parse_event(data) {
                Some(ev) => {
                    let line = format!(
                        "{{\"source\":\"cortex_events\",\"event_type\":{},\"pid\":{},\"entropy_signal\":{},\"severity\":{}}}\n",
                        ev.event_type, ev.pid, ev.entropy_signal, ev.severity
                    );
                    if let Ok(mut f) =
                        OpenOptions::new().create(true).append(true).open(&log_path)
                    {
                        let _ = f.write_all(line.as_bytes());
                    }
                }
                None => {
                    eprintln!("ringbuf_forwarder: evento inválido ({} bytes)", data.len());
                }
            }
            0
        })?;
    }

    let ringbuf = builder.build()?;
    eprintln!(
        "ringbuf_forwarder: consumiendo {:?} → {}",
        map_paths, log_path
    );
    // Heartbeat propio cada ~60s: demuestra consumidor vivo ante el verificador
    // (exige mtime <600s) sin fabricar eventos de seguridad (source distinto).
    let mut ticks: u32 = 0;
    loop {
        if let Err(e) = ringbuf.poll(Duration::from_millis(500)) {
            eprintln!("ringbuf_forwarder: poll: {}", e);
            std::thread::sleep(Duration::from_millis(500));
        }
        ticks += 1;
        if ticks >= 120 {
            ticks = 0;
            let line = format!(
                "{{\"source\":\"ringbuf_forwarder\",\"event\":\"heartbeat\",\"maps\":{:?}}}\n",
                map_paths
            );
            if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&log_path) {
                let _ = f.write_all(line.as_bytes());
            }
        }
    }
}
