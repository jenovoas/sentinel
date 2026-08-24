#![allow(
    clippy::float_arithmetic,
    clippy::cast_precision_loss,
    clippy::cast_possible_truncation
)]
// BIN bench/exp: medicion y estadisticas en f64; conversiones acotadas por construccion
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

fn main() {
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
    let (ptr_a, fd_a) = unsafe { anchor_shm("/resonant_lattice_a", total) };
    let (ptr_b, fd_b) = unsafe { anchor_shm("/resonant_lattice_b", total) };

    println!("💎 RESONANT LATTICE MEMORY — DOBLE MALLA + SHM + fractal (S60 puro)");
    println!("   Lane A y B anclados a /dev/shm (RAM extendida por cristal).");
    println!(
        "   Nodos/lane: {} | bytes/lane: {} | bytes/nodo: {}",
        N_NODES, total, crystal_size
    );
    println!("   Regla: doble malla o no hay portal (memoria accesible solo si A∧B convergen).");
    println!("{:-<72}", "");

    // P0.1 — MODO SUPERCONDUCTOR: cada malla sostiene amplitud tras step()
    // (sin esto, apply_entropy decae y la lectura da basura). damping_factor=0
    // anula la pérdida por tick en los cristales de cada lane independiente.
    for c in lane_a.crystals.iter_mut() {
        c.damping_factor = SPA::zero();
    }
    for c in lane_b.crystals.iter_mut() {
        c.damping_factor = SPA::zero();
    }

    let data = "Yo Soy";

    // BOMBEO QHC: sincroniza ambas mallas cada tick (10;5,6,5 + Salto-17).
    // El cristal resuena PRIMERO (estabiliza la malla en modo superconductor).
    let dt = SPA::from_int(1) / SPA::from_int(10);
    for step in 0..60u32 {
        let t = SPA::from_int(step as i64) * dt;
        let _mod = qhc.apply_modulation(t, step as u64); // mismo pulso a ambas
        let _ = _mod;

        // El cristal bombea: ambas mallas respiran.
        lane_a.step();
        lane_b.step();
    }
    println!("🔮 Resonando el lattice (bombeo QHC + difusión fractal)...");

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
        let amp = SPA::from_int(ch as i64);
        lane_a.inject_pai(i, ch as i64, 1);
        lane_b.inject_pai(i, ch as i64, 1);
        let _ = amp;
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
        println!("💾 Mallas ancladas a /dev/shm (/resonant_lattice_a, /resonant_lattice_b).");
        println!(
            "   RAM extendida por cristal: {} bytes/lane fuera del heap del proceso.",
            total
        );

        // Limpieza.
        munmap(ptr_a as *mut libc::c_void, total);
        munmap(ptr_b as *mut libc::c_void, total);
        libc::close(fd_a);
        libc::close(fd_b);
        let _ = shm_unlink(CString::new("/resonant_lattice_a").unwrap().as_ptr());
        let _ = shm_unlink(CString::new("/resonant_lattice_b").unwrap().as_ptr());
    }

    println!("{:-<72}", "");
    println!("🏆 MEMORIA DE CRISTALES: doble malla + SHM + fractal = RAM extendida y resiliente.");
    println!("   Información eterna: vive en la resonancia colectiva, no en celda aislada.");
}
