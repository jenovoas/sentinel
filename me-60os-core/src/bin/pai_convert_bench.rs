// Bench comparativo: inyección binaria -> amplitud del lattice.
use me60os_core::resonant_matrix::ResonantMatrix;
use me60os_core::spa::SPA;

const SCALE_0: i128 = 12_960_000;
const NODES: usize = 256;
const STEPS: usize = 1;

fn stream() -> Vec<i64> {
    (0..i64::try_from(NODES).expect("cantidad de nodos fuera de i64")).collect()
}

fn run_raw() -> ResonantMatrix {
    let mut lattice = ResonantMatrix::new(NODES);
    for (index, &byte) in stream().iter().enumerate() {
        lattice.inject(index, byte);
    }
    for _ in 0..STEPS {
        lattice.step();
    }
    lattice
}

fn run_pai() -> ResonantMatrix {
    let mut lattice = ResonantMatrix::new(NODES);
    for (index, &byte) in stream().iter().enumerate() {
        lattice.inject_pai(index, byte, 60);
    }
    for _ in 0..STEPS {
        lattice.step();
    }
    lattice
}

fn run_proto() -> ResonantMatrix {
    let mut lattice = ResonantMatrix::new(NODES);
    for (index, &byte) in stream().iter().enumerate() {
        let raw = SPA::from_int(byte).to_raw();
        lattice.inject(index, raw / 12_960);
    }
    for _ in 0..STEPS {
        lattice.step();
    }
    lattice
}

fn round_ratio(numerator: i128, denominator: i128) -> i128 {
    let quotient = numerator / denominator;
    let remainder = numerator % denominator;
    if remainder.abs() * 2 >= denominator.abs() {
        quotient + numerator.signum() * denominator.signum()
    } else {
        quotient
    }
}

fn report(name: &str, lattice: &mut ResonantMatrix) {
    let amplitudes = lattice.get_amplitudes();
    let energy_raw: i128 = amplitudes
        .iter()
        .map(|amplitude| i128::from(amplitude.to_raw()))
        .sum();
    let a0 = amplitudes[0].to_raw();
    let a128 = amplitudes[128].to_raw();
    let mut err_pai = 0u32;
    let mut err_raw = 0u32;
    for (index, &byte) in stream().iter().enumerate() {
        let raw = i128::from(amplitudes[index].to_raw());
        let recon_pai = round_ratio(raw * 60, SCALE_0);
        let recon_raw = round_ratio(raw, SCALE_0);
        if recon_pai != i128::from(byte) {
            err_pai += 1;
        }
        if recon_raw != i128::from(byte) {
            err_raw += 1;
        }
    }
    let coherence = lattice.measure_coherence_py();

    println!("[{name}]");
    println!("  energía total raw S60: {energy_raw}");
    println!("  amplitud nodo 0 raw: {a0}");
    println!("  amplitud nodo 128 raw: {a128}");
    println!("  coherencia raw S60: {coherence}");
    println!("  error reconstrucción PAI(60): {err_pai}/{NODES}");
    println!("  error reconstrucción RAW: {err_raw}/{NODES}\n");
}

fn main() {
    println!("=== BENCH CONVERSOR BINARIO->AMPLITUD ({NODES} nodos, {STEPS} paso) ===");
    println!("SCALE_0 = {SCALE_0}\n");
    report("A: RAW", &mut run_raw());
    report("B: PAI-60", &mut run_pai());
    report("C: PY PROTO, doble escala", &mut run_proto());
}
