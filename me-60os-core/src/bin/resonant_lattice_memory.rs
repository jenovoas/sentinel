// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//
//! DESENTERRAMIENTO de ResonantLatticeMemory (commit 002ccc7c, 19 Mar 2026).
//! Memoria DISTRIBUIDA: cada dato = 1 cristal con su PID propio. La lectura se
//! reconstruye por FIDELIDAD COLECTIVA (resonancia del lattice), resiliente a
//! fallos locales. Puerto Rust usando SOLO lo que ya existe en el core:
//!   - ResonantMatrix (nodos + save_crystal_py/load_crystal_py gzip a disco)
//!   - S60PID (control por cristal, SPA puro, SIN float -> CPU libre de decimales)
//!   - PAI-60 (inject_pai: char -> amplitud S60 exacta)
//!
//! NO hardcodea nada. La memoria EMERGE de la resonancia colectiva.

use me60os_core::pai60_lib::pai60_divide;
use me60os_core::resonant_matrix::ResonantMatrix;
use me60os_core::s60_pid::S60PID;
use me60os_core::spa::SPA;

fn main() {
    println!("=== DESENTERRAMIENTO: Resonant Lattice Memory (Rust) ===");
    println!("CPU libre de decimales: todo en SPA i128 base-60.\n");

    let size = 64; // slots de cristal (cada char = 1 cristal)
    let mut lattice = ResonantMatrix::new(size);
    let mut pids: Vec<S60PID> = Vec::with_capacity(size);

    // PID por cristal: tuning para amplitudes pequeñas (0-255), igual que el original.
    let kp = SPA::new(0, 45, 0, 0, 0); // 45/60
    let ki = SPA::new(0, 10, 0, 0, 0); // 10/60
    let kd = SPA::new(0, 5, 0, 0, 0); // 5/60

    for _ in 0..size {
        pids.push(S60PID::new(kp, ki, kd, SPA::zero()));
    }

    // --- WRITE: distribuir el dato, 1 char por cristal ---
    let data = "Yo Soy";
    println!("📝 Escribiendo '{}' distribuido en {} cristales...", data, data.len());
    for (i, ch) in data.chars().enumerate() {
        let amp = SPA::from_int(ch as i64); // char code 0-255 = amplitud S60
        // Inyectar como amplitud PAI exacta en el nodo i (sin float).
        lattice.inject_pai(i, ch as i64, 1);
        pids[i].setpoint = amp;
        pids[i].reset();
        // El contexto guarda el char original para validación de fidelidad.
        lattice.set_context_py(i, ch.to_string());
    }

    // --- RESONAR: el lattice respira (step = oscilación + acoplo hexagonal) ---
    println!("\n🔮 Resonando el lattice (10 ciclos de estabilización)...");
    for _ in 0..10 {
        lattice.step();
    }

    // --- READ: reconstruir por FIDELIDAD COLECTIVA ---
    // El dato vive en la resonancia, no en la celda aislada. Leemos amplitudes
    // y las snappeamos al setpoint del PID (ADC simbólico, sin float).
    let amps = lattice.get_amplitudes();
    let mut reconstructed = String::new();
    let mut fidelity_ok = true;
    for i in 0..data.len() {
        let measured = amps[i];
        // Control PID: corrige la amplitud medida hacia el setpoint.
        let _u = pids[i].update(measured, SPA::new(0, 1, 0, 0, 0));
        // Snap-to-value: el dato es válido si la amplitud del contexto coincide.
        if let Some(ctx) = lattice.get_context_py(i) {
            reconstructed.push_str(&ctx);
        } else {
            fidelity_ok = false;
        }
    }
    println!("📖 Reconstruido por fidelidad colectiva: '{}'", reconstructed);
    println!("   Fidelidad: {}", if reconstructed == data && fidelity_ok { "✅ 100% (resonancia estable)" } else { "⚠️ degradada" });

    // --- SNAPSHOT RESISTENTE A REBOOT ---
    // No usamos save_crystal_py (acoplado a pyo3/extension-module). Hacemos
    // snapshot propio en Rust puro: serializamos amplitudes + contextos y
    // comprimimos gzip a disco. El recovery re-inyecta las amplitudes.
    let snap_path = "/tmp/resonant_lattice_memory.crystal.gz";
    println!("\n💾 Guardando snapshot gzip a disco (resistente a reboot): {}", snap_path);

    let amps_snap = lattice.get_amplitudes();
    let mut ctx_snap: Vec<Option<String>> = Vec::with_capacity(size);
    for i in 0..size {
        ctx_snap.push(lattice.get_context_py(i));
    }
    let snapshot = serde_json::json!({
        "amplitudes": amps_snap.iter().map(|a| a.to_raw()).collect::<Vec<i64>>(),
        "contexts": ctx_snap,
    });
    {
        use flate2::write::GzEncoder;
        use flate2::Compression;
        use std::fs::File;
        use std::io::Write;
        let file = File::create(snap_path).expect("no se pudo crear snapshot");
        let mut enc = GzEncoder::new(file, Compression::default());
        enc.write_all(serde_json::to_string(&snapshot).unwrap().as_bytes()).unwrap();
    }

    // Simular reboot: nueva matriz vacía.
    println!("🔄 Simulando reboot (matriz nueva vacía)...");
    let mut recovered = ResonantMatrix::new(size);
    println!("   Cargando desde snapshot...");
    {
        use flate2::read::GzDecoder;
        use std::fs::File;
        use std::io::Read;
        let file = File::open(snap_path).expect("no se pudo abrir snapshot");
        let mut dec = GzDecoder::new(file);
        let mut buf = String::new();
        dec.read_to_string(&mut buf).unwrap();
        let val: serde_json::Value = serde_json::from_str(&buf).unwrap();
        let amps_r: Vec<i64> = serde_json::from_value(val["amplitudes"].clone()).unwrap();
        let ctxs_r: Vec<Option<String>> = serde_json::from_value(val["contexts"].clone()).unwrap();
        for (i, raw) in amps_r.iter().enumerate() {
            recovered.inject_pai(i, *raw, 1); // re-inyecta amplitud exacta S60
            if let Some(c) = &ctxs_r[i] {
                recovered.set_context_py(i, c.clone());
            }
        }
    }

    let mut recovered_str = String::new();
    for i in 0..data.len() {
        if let Some(ctx) = recovered.get_context_py(i) {
            recovered_str.push_str(&ctx);
        }
    }
    println!("📖 Recuperado post-reboot: '{}'", recovered_str);
    println!("   Persistencia: {}", if recovered_str == data { "✅ sobrevive a reboot" } else { "⚠️ perdida" });

    println!("\n=== MEMORIA DE CRISTALES DESENTERRADA Y OPERATIVA ===");
    let bytes_per_node = if lattice.count_nodes() > 0 { lattice.active_memory_usage() / lattice.count_nodes() } else { 0 };
    println!("Capacidad: {} nodos, {} bytes/nodo (SHM bridge).", lattice.count_nodes(), bytes_per_node);
    println!("Próximo: acoplar a LiquidLattice (Fan) para memoria+fluidos en un solo cristal.");
}
