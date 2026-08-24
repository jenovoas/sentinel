// Bench comparativo: inyeccion binaria -> amplitud del lattice.
// Compara 3 caminos sobre el MISMO stream de datos:
//   A) raw:        inject(i, byte)                 -> amplitud = byte.0
//   B) pai60:      inject_pai(i, byte, 60)         -> amplitud = byte/60 (reciproco exacto)
//   C) py_proto:   byte/1000 -> transduce_pulse     -> fiel a resonant_lattice_memory.py
// Mide: energia total, amplitud en nodos clave, coherencia, y error de reconstruccion
// (round-trip amp*denom -> byte) para ver si el dato binario es recuperable.
//
// ETIQUETA DE ESTUDIO:
//   [exp fallido para estudio] = camino C marcado como ERRONEO, NO como implementacion valida.
//   El camino C (py_proto) sufre doble-escala: pasa `SPA::from_int(b).to_raw()/12960`
//   a `inject`->`transduce_pulse`, que RE-ESCALA por SCALE_0. Resultado: 256/256
//   irrecuperable (ver salida). Se deja INTENCIONALMENTE como evidencia del fallo
//   de doble-escala. No borrar: es material de estudio para no repetir el error.
#![allow(
    clippy::float_arithmetic,
    clippy::cast_precision_loss,
    clippy::cast_possible_truncation
)] // BIN bench/exp: medicion y estadisticas en f64; conversiones acotadas por construccion
use me60os_core::resonant_matrix::ResonantMatrix;
use me60os_core::spa::SPA;

const SCALE_0: f64 = 12_960_000.0;
const NODES: usize = 256;
const STEPS: usize = 1; // paso minimo para que acople vecinos sin dissipar todo

fn stream() -> Vec<i64> {
    // Stream deterministico tipo "entropia binaria" 0..255
    (0..NODES as i64).collect()
}

fn run_raw() -> ResonantMatrix {
    let mut l = ResonantMatrix::new(NODES);
    for (i, &b) in stream().iter().enumerate() {
        l.inject(i, b);
    }
    for _ in 0..STEPS {
        l.step();
    }
    l
}

fn run_pai() -> ResonantMatrix {
    let mut l = ResonantMatrix::new(NODES);
    for (i, &b) in stream().iter().enumerate() {
        l.inject_pai(i, b, 60);
    }
    for _ in 0..STEPS {
        l.step();
    }
    l
}

// [exp fallido para estudio] camino C: fiel a resonant_lattice_memory.py pero con
// doble-escala (ver ETIQUETA DE ESTUDIO arriba). Se deja para no repetir el error.
fn run_proto() -> ResonantMatrix {
    let mut l = ResonantMatrix::new(NODES);
    for (i, &b) in stream().iter().enumerate() {
        // fiel a python: pulse_val = to_raw()//12960 ; transduce_pulse re-escala
        let raw = SPA::from_int(b).to_raw();
        let pulse = raw / 12960; // SCALE_0/1000
        l.inject(i, pulse);
    }
    for _ in 0..STEPS {
        l.step();
    }
    l
}

fn report(name: &str, l: &mut ResonantMatrix) {
    let amps = l.get_amplitudes();
    let energy_raw: i128 = amps.iter().map(|a| a.to_raw() as i128).sum();
    let energy_abs = energy_raw as f64 / SCALE_0;
    let a0 = amps[0].to_raw() as f64 / SCALE_0;
    let a128 = amps[128].to_raw() as f64 / SCALE_0;

    // reconstruccion (round-trip) para PAI(60): amp*60 -> byte
    let mut err_pai = 0u32;
    let mut err_raw = 0u32;
    for (i, &b) in stream().iter().enumerate() {
        let recon_pai = (amps[i].to_raw() as f64 / SCALE_0 * 60.0).round() as i64;
        if recon_pai != b {
            err_pai += 1;
        }
        let recon_raw = (amps[i].to_raw() as f64 / SCALE_0).round() as i64;
        if recon_raw != b {
            err_raw += 1;
        }
    }

    // coherencia (desviacion de fase media, de measure_coherence_py)
    let coh = l.measure_coherence_py();

    println!("[{name}]");
    println!("  energia total (abstracto): {energy_abs:.4}");
    println!("  amplitud nodo0 : {a0:.6}");
    println!("  amplitud nodo128: {a128:.6}");
    println!("  coherencia (raw S60): {coh}");
    println!("  error reconstruccion PAI(60): {err_pai}/{NODES}");
    println!("  error reconstruccion RAW    : {err_raw}/{NODES}");
    println!();
}

fn main() {
    println!(
        "=== BENCH CONVERSOR BINARIO->AMPLITUD (stream 0..255, {NODES} nodos, {STEPS} step) ==="
    );
    println!("SCALE_0 = {SCALE_0}\n");
    let mut a = run_raw();
    report("A: RAW (produccion actual)", &mut a);
    let mut b = run_pai();
    report("B: PAI-60 exacto (inject_pai /60)", &mut b);
    let mut c = run_proto();
    report(
        "C: [exp fallido para estudio] PY PROTO (byte/1000 -> transduce, doble-escala)",
        &mut c,
    );
}
