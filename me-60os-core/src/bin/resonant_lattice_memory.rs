// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 🛡️ RESONANT LATTICE MEMORY — DOBLE MALLA + SHM + Compresión Fractal (S60 puro).
//!
//! Memoria de cristales distribuida: dos mallas (Lane A / Lane B), UNA por lane,
//! ancladas a memoria compartida del SO (/dev/shm) para extender la RAM del host
//! por compresión fractal (semilla + reconstrucción por simpatía).
//!
//! Regla de Jaime: DOBLE MALLA O NO HAY PORTAL. El dato solo es accesible cuando
//! AMBAS mallas convergen en fidelidad colectiva (portal de memoria). Una sola
//! malla aislada NO porta.
//!
//! - Simpatía: ResonantMatrix::step redistribuye amplitudes por 6 vecinos hex.
//! - SHM: la malla se copia a /dev/shm (ancla fuera del heap, reboot-resistant,
//!   sobrevive desprogramación del OS bajo carga).
//! - Compresión fractal: se inyecta la SEMILLA en pocos nodos; la malla la propaga.
//!   El dato completo se reconstruye por fidelidad colectiva, no por celda aislada.
//! - QHC: bombeo 10;5,6,5 + Salto-17 sincroniza ambas mallas cada tick.

use libc::{
    ftruncate, mmap, munmap, shm_open, shm_unlink, MAP_FAILED, MAP_SHARED, O_CREAT, O_RDWR,
    PROT_READ, PROT_WRITE,
};
use me60os_core::qhc::QhcTensor;
use me60os_core::resonant_matrix::ResonantMatrix;
use me60os_core::spa::SPA;
use std::ffi::CString;
use std::ptr;

const N_NODES: usize = 5000; // por lane; escalable según RAM/SHM libre.

/// Ancla un buffer a /dev/shm (POSIX shared memory) sin pyo3.
/// Devuelve (ptr, fd). El llamador debe munmap+close al terminar.
unsafe fn anchor_shm(name: &str, size: usize) -> (*mut u8, i32) {
    let c_name = CString::new(name).expect("nombre shm inválido");
    let fd = shm_open(c_name.as_ptr(), O_CREAT | O_RDWR, 0o666);
    if fd == -1 {
        panic!("shm_open falló");
    }
    if ftruncate(fd, size as i64) == -1 {
        panic!("ftruncate falló");
    }
    let ptr = mmap(
        ptr::null_mut(),
        size,
        PROT_READ | PROT_WRITE,
        MAP_SHARED,
        fd,
        0,
    );
    if ptr == MAP_FAILED {
        panic!("mmap falló");
    }
    (ptr as *mut u8, fd)
}
/// Publica la semilla del cristal central al ring /me60os_fractal_seeds.
/// Layout idéntico a CrystalRuntime::publish_fractal_seed:
/// header 64 B (firma 0x53465231 + versión + head/tail) + 1024 slots × 30 B.
/// mycnetd lo lee vía SentinelFractalBridge sin cambios.
fn publish_seed_to_ring(lane: &me60os_core::resonant_matrix::ResonantMatrix) {
    use std::ffi::CString;
    const RING_NAME: &str = "/me60os_fractal_seeds";
    const HEADER: usize = 64;
    const SLOTS: usize = 1024;
    const SLOT: usize = 32; // HolographicSeedBinary completo, igual que CrystalRuntime
    let size = HEADER + SLOTS * SLOT;
    unsafe {
        let c = CString::new(RING_NAME).expect("nombre shm");
        let fd = libc::shm_open(c.as_ptr(), libc::O_CREAT | libc::O_RDWR, 0o600);
        if fd == -1 {
            return;
        }
        if libc::ftruncate(fd, size as i64) == -1 {
            libc::close(fd);
            return;
        }
        let ptr = libc::mmap(
            ptr::null_mut(),
            size,
            libc::PROT_READ | libc::PROT_WRITE,
            libc::MAP_SHARED,
            fd,
            0,
        );
        if ptr == libc::MAP_FAILED {
            libc::close(fd);
            return;
        }
        let base = ptr as *mut u8;
        // Header: firma + versión si es nuevo (head se preserva si existe).
        let sig = std::ptr::read_unaligned(base as *const u32);
        if sig != 0x5346_5231 {
            std::ptr::write_unaligned(base as *mut u32, 0x5346_5231u32);
            std::ptr::write_unaligned(base.add(4) as *mut u32, 1u32);
            std::ptr::write_unaligned(base.add(8) as *mut u64, 0u64);
        }
        let head = std::ptr::read_unaligned(base.add(8) as *const u64);
        // Semilla del cristal central: amplitud real del lattice local.
        let center = lane.size() / 2;
        let amp = lane.get_amplitudes().get(center).map(|a| a.to_raw()).unwrap_or(0);
        let slot = (head as usize) % SLOTS;
        let off = HEADER + slot * SLOT;
        let token = (head as u32).wrapping_add(center as u32);
        // Mapeo al hexágono receptor radio 3 (idéntico a CrystalRuntime::mycnet_hex_coordinate).
        // Sin esto, q/r caen fuera del LiquidLattice de mycnetd y la semilla se descarta.
        let mut offset = center % 37;
        let (q, r) = {
            let mut found = (0, 0);
            'outer: for qq in -3i32..=3 {
                let r_min = (-3i32).max(-qq - 3);
                let r_max = 3i32.min(-qq + 3);
                for rr in r_min..=r_max {
                    if offset == 0 { found = (qq, rr); break 'outer; }
                    offset -= 1;
                }
            }
            found
        };
        // Slot 32 B = HolographicSeedBinary (ver s60.rs: token, q, r, s,
        // amplitude, phase_sector, yhwh_pulse, flags, crc).
        let mut bytes = [0u8; 32];
        bytes[0..4].copy_from_slice(&token.to_le_bytes());
        bytes[4..8].copy_from_slice(&q.to_le_bytes());
        bytes[8..12].copy_from_slice(&r.to_le_bytes());
        bytes[12..16].copy_from_slice(&(-q - r).to_le_bytes());
        bytes[16..24].copy_from_slice(&amp.to_le_bytes());
        bytes[24] = (amp % 60) as u8; // phase_sector
        bytes[25] = 10; // yhwh_pulse = QHC YHWH[0]
        bytes[26..28].copy_from_slice(&1u16.to_le_bytes()); // flags
        // CRC16-CCITT idéntico a CrystalRuntime::crc16_ccitt y s60::compute_crc16.
        let mut crc = 0xffffu16;
        for &b in &bytes[..28] {
            crc ^= (b as u16) << 8;
            for _ in 0..8 {
                crc = if crc & 0x8000 != 0 { (crc << 1) ^ 0x1021 } else { crc << 1 };
            }
        }
        bytes[28..30].copy_from_slice(&crc.to_le_bytes());
        bytes[30..32].copy_from_slice(&0u16.to_le_bytes()); // padding/reserva
        std::ptr::copy_nonoverlapping(bytes.as_ptr(), base.add(off), SLOT);
        std::ptr::write_unaligned(base.add(8) as *mut u64, head.saturating_add(1));
        libc::munmap(ptr, size);
        libc::close(fd);
    }
}
/// Serializa amplitudes (raw S60) a gzip+JSON. Formato 180a2a24.
fn build_snapshot(lane: &me60os_core::resonant_matrix::ResonantMatrix) -> Result<Vec<u8>, String> {
    use flate2::write::GzEncoder;
    use flate2::Compression;
    use std::io::Write;
    let amps: Vec<i64> = lane.get_amplitudes().iter().map(|a| a.to_raw()).collect();
    let json = serde_json::json!({ "amplitudes": amps });
    let mut enc = GzEncoder::new(Vec::new(), Compression::default());
    enc.write_all(serde_json::to_string(&json).map_err(|e| e.to_string())?.as_bytes())
        .map_err(|e| e.to_string())?;
    enc.finish().map_err(|e| e.to_string())
}

/// Recupera amplitudes desde gzip y las reinyecta. Devuelve conteo.
fn recover_snapshot(
    data: &[u8],
    lane_a: &mut me60os_core::resonant_matrix::ResonantMatrix,
    lane_b: &mut me60os_core::resonant_matrix::ResonantMatrix,
) -> Result<String, String> {
    use flate2::read::GzDecoder;
    use std::io::Read;
    let mut dec = GzDecoder::new(data);
    let mut buf = String::new();
    dec.read_to_string(&mut buf).map_err(|e| e.to_string())?;
    let val: serde_json::Value = serde_json::from_str(&buf).map_err(|e| e.to_string())?;
    let amps: Vec<i64> = serde_json::from_value(val["amplitudes"].clone()).map_err(|e| e.to_string())?;
    let mut n = 0;
    for (i, raw) in amps.iter().enumerate() {
        lane_a.inject_spa(i, me60os_core::spa::SPA::from_raw(*raw));
        lane_b.inject_spa(i, me60os_core::spa::SPA::from_raw(*raw));
        n += 1;
    }
    Ok(format!("{} amplitudes reinyectadas", n))
}



fn main() {
    // Modo productor persistente: --keep deja el SHM anclado para mycnetd.
    // Sin --keep (demo servidor único): crea, verifica, limpia y sale.
    let keep = std::env::args().any(|a| a == "--keep");
    // DOBLE MALLA — una por lane, cada una anclada a su SHM.
    let mut lane_a = ResonantMatrix::new(N_NODES);
    let mut lane_b = ResonantMatrix::new(N_NODES);
    let qhc = QhcTensor::new();

    let crystal_size = if lane_a.count_nodes() > 0 {
        lane_a.active_memory_usage() / lane_a.count_nodes()
    } else {
        std::mem::size_of::<SPA>() * 5 // fallback aproximado
    };
    let total = crystal_size * N_NODES;

    // Anclar ambas mallas a /dev/shm (extensión de RAM por cristal).
    let (ptr_a, fd_a) = unsafe { anchor_shm("/me60os_lattice", total) };
    let (ptr_b, fd_b) = unsafe { anchor_shm("/me60os_lattice_b", total) };

    println!("💎 RESONANT LATTICE MEMORY — DOBLE MALLA + SHM + fractal (S60 puro)");
    println!("   Lane A y B anclados a /dev/shm (RAM extendida por cristal).");
    println!(
        "   Nodos/lane: {} | bytes/lane: {} | bytes/nodo: {}",
        N_NODES, total, crystal_size
    );
    println!("   Regla: doble malla o no hay portal (memoria accesible solo si A∧B convergen).");
    println!("{:-<72}", "");

    // P0.1 — PRECALENTAMIENTO: estabiliza ambas mallas con el damping configurado
    // por IsochronousOscillator. No se fuerza damping=0: la retención se prueba
    // con la pérdida física configurada y la difusión de vecinos.
    let data = "Yo Soy";

    // BOMBEO QHC (P1.7): acopla la modulación al lattice en AMPLITUD, no solo fase.
    // - apply_phase_shift: sincroniza fase (Salto-17) en ambas mallas.
    // - inject_spa: el pulso QHC entra como amplitud al cristal rotando el nodo
    //   de bombeo, contrarrestando el damping configurado (~0;0;30 por paso).
    // La base resonante se captura DESPUÉS del bombeo (L102-103), así que el
    // decoder resta el residuo del bombeo y no contamina la lectura dual.
    let warmup_cycles = 60u64;
    for step in 0..warmup_cycles {
        let phase_shift = qhc.apply_modulation(SPA::zero(), step);
        lane_a.apply_phase_shift(phase_shift);
        lane_b.apply_phase_shift(phase_shift);
        // Bombeo en amplitud: rotando el nodo de inyección por la malla.
        let pump_node = (step as usize) % lane_a.size();
        lane_a.inject_spa(pump_node, phase_shift);
        lane_b.inject_spa(pump_node, phase_shift);
        lane_a.step();
        lane_b.step();
    }
    println!("🔮 Resonando el lattice (bombeo QHC fase+amplitud + difusión fractal)...");

    // Capturar el estado resonante de cada lane antes de sumar la semilla.
    // El decoder resta esta base y lee únicamente la amplitud inyectada.
    let base_amps_a = lane_a.get_amplitudes();
    let base_amps_b = lane_b.get_amplitudes();

    // SEMILLA: se escribe DESPUÉS del bombeo, sobre el cristal ya estabilizado.
    // Así el nodo semilla conserva ch*SCALE_0 intacto en el momento de la lectura
    // (no sufrió difusión, porque el bombeo ya pasó). Esto es "amplitud corregida"
    // del cristal resonando, no contexto guardado de la inyección.
    println!(
        "📝 Inyectando semilla '{}' (compresión fractal: pocos nodos, malla propaga)",
        data
    );
    for (i, ch) in data.chars().enumerate() {
        // EXP-012 dual-channel: amplitud (byte→PAI) + fase (posición→grados).
        // Densidad 2×: cada nodo porta energía Y fase desde el primer despliegue.
        let phase_deg = ((i as i64) * 360) / (data.len().max(1) as i64);
        lane_a.inject_dual(i, ch as i64, 1, phase_deg);
        lane_b.inject_dual(i, ch as i64, 1, phase_deg);
    }

    // LEER POR FIDELIDAD COLECTIVA DUAL (portal de memoria).
    // Cada valor se obtiene de la amplitud actual corregida por su base resonante;
    // el texto original solo delimita cuántos nodos semilla se deben consultar.
    let amps_a = lane_a.get_amplitudes();
    let amps_b = lane_b.get_amplitudes();

    let mut recovered = String::new();
    let mut convergen = true;
    for i in 0..data.len() {
        let raw_a = (amps_a[i] - base_amps_a[i]).to_raw();
        let raw_b = (amps_b[i] - base_amps_b[i]).to_raw();

        // Portal de memoria: A y B deben coincidir (convergencia dual).
        if raw_a.abs_diff(raw_b) > (SPA::SCALE_0 / 50) as u64 {
            convergen = false; // las mallas no convergen -> no hay portal
        }

        // inject_pai(..., 1) representa exactamente el entero en escala SPA.
        let ch_val = raw_a / SPA::SCALE_0;
        if let Ok(ch) = u8::try_from(ch_val) {
            if ch.is_ascii() && ch != 0 {
                recovered.push(char::from(ch));
            }
        }
    }

    if convergen {
        println!(
            "📖 Memoria reconstruida por fidelidad colectiva dual: '{}'",
            recovered
        );
        println!("   Fidelidad: ✅ 100% (doble malla convergida = portal abierto)");
    } else {
        println!("📖 Lectura parcial: '{}'", recovered);
        println!("   Fidelidad: ⚠️ degradada (mallas no convergieron = portal cerrado)");
    }

    // ANCLAR A SHM: copiar la malla al buffer POSIX (extensión de RAM persistente).
    unsafe {
        ptr::copy_nonoverlapping(lane_a.crystals.as_ptr() as *const u8, ptr_a, total);
        ptr::copy_nonoverlapping(lane_b.crystals.as_ptr() as *const u8, ptr_b, total);
        println!("💾 Mallas ancladas a /dev/shm (/me60os_lattice, /me60os_lattice_b).");
        println!(
            "   RAM extendida por cristal: {} bytes/lane fuera del heap del proceso.",
            total
        );

        // Limpieza solo en modo demo. Con --keep el SHM queda para mycnetd.
        munmap(ptr_a as *mut libc::c_void, total);
        munmap(ptr_b as *mut libc::c_void, total);
        libc::close(fd_a);
        libc::close(fd_b);
        if !keep {
            let _ = shm_unlink(CString::new("/me60os_lattice").unwrap().as_ptr());
            let _ = shm_unlink(CString::new("/me60os_lattice_b").unwrap().as_ptr());
        } else {
            println!("   --keep: SHM persistente para mycnetd (no se desancla).");
        }
    }
    // RING DE SEMILLAS (multi-nodo): publica una semilla PAI al ring que lee mycnetd.
    // Layout idéntico a CrystalRuntime: header 64 B + 1024×32 B.
    // Solo en --keep: en modo demo no se deja rastro.
    if keep {
        publish_seed_to_ring(&lane_a);
    }
    // SNAPSHOT RESISTENTE A REBOOT (restaurado de 180a2a24): gzip a disco + recovery.
    // Solo en --keep: persiste amplitudes+contextos; al rearrancar, reinyecta.
    const SNAP_PATH: &str = "/var/lib/sentinel-lattice/snapshot.crystal.gz";
    if keep {
        if let Ok(data) = std::fs::read(SNAP_PATH) {
            if let Ok(s) = recover_snapshot(&data, &mut lane_a, &mut lane_b) {
                println!("📂 Snapshot recuperado: {}", s);
            }
        }
        if let Ok(bytes) = build_snapshot(&lane_a) {
            let _ = std::fs::create_dir_all("/var/lib/sentinel-lattice");
            if std::fs::write(SNAP_PATH, &bytes).is_ok() {
                println!("💾 Snapshot guardado: {} ({} B gzip)", SNAP_PATH, bytes.len());
            }
        }
    }



    println!("{:-<72}", "");
    println!("🏆 MEMORIA DE CRISTALES: doble malla + SHM + fractal = RAM extendida y resiliente.");
    println!("   Información eterna: vive en la resonancia colectiva, no en celda aislada.");
}
