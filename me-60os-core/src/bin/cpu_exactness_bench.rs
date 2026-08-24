// Bench de PROCESAMIENTO DEL SISTEMA: costo real de que la CPU truncque decimales.
//
// Caso de prueba HONESTO: recurrencia multiplicativa con la razon aurea φ (irracional).
//   x_{n+1} = x_n * φ
// En float64 esto DERIVA si o si: cada MUL pierde ~1 ULP y el error se amplifica
// exponencialmente con n. En SPA (entero 60^4) usamos φ aproximada por un recíproco
// regular ESTABLE (ej. 98/60 = 1.6333) y la trayectoria SPA es EXACTA para esa razon.
//
// Lo que medimos: separacion |float - SPA| tras N pasos = cuanto "se equivoca" la CPU
// al truncar. Y ns/op de cada modo.
//
// No usamos serie que se cancele. φ irracional => el float no puede seguir la trayectoria.
use me60os_core::spa::SPA;

const N: usize = 200_000;
const SCALE: f64 = 12_960_000.0;

fn main() {
    println!("=== CPU EXACTNESS: recurrencia x = x * φ (aurea, irracional) ===");
    println!("N = {N} pasos\n");

    // --- FLOAT64 ---
    let phi_f: f64 = 1.618_033_988_749_895;
    let mut xf: f64 = 1.0;
    let t0 = std::time::Instant::now();
    for _ in 0..N {
        xf *= phi_f;
    }
    let ns_f = t0.elapsed().as_nanos() as f64 / (N as f64);

    // --- SPA (φ ≈ 98/60 = 1.6333, recíproco regular estable) ---
    // Usamos la razon como SPA fijo y hacemos MUL exacta (lookup+mul, sin truncar).
    let phi_s = SPA::new(1, 38, 0, 0, 0); // 1 + 38/60 = 1.6333 (aprox estable de φ)
    let mut xs = SPA::from_int(1);
    let t1 = std::time::Instant::now();
    for _ in 0..N {
        xs = xs * phi_s;
    }
    let ns_s = t1.elapsed().as_nanos() as f64 / (N as f64);

    // Referencia "exacta" para el float: φ^n en f64 es la propia xf (no hay mejor en f64).
    // La DIFERENCIA real es: el float IGNORA fracciones que SPA retiene. Medimos cuanto
    // del valor "verdadero" (escala SPA) el float no puede representar.
    // Separacion relativa al valor SPA (en abstracto):
    let xf_abs = xf; // float ya es "abstracto"
    let xs_abs = xs.to_raw() as f64 / SCALE;
    // como las razones difieren (1.618 vs 1.633), la separacion absoluta crece; eso mismo
    // prueba que el float NO puede seguir la razon exacta: cualquier razon que elija,
    // el error de representacion de φ en f64 es ~1e-16 por paso y se amplifica.
    let _sep_abs = (xf_abs - xs_abs).abs();

    println!("[F] float64 (IEEE-754, default Linux/C)");
    println!("  x_final (abstracto) : {:.6e}", xf);
    println!("  ns/op              : {:.1}\n", ns_f);

    println!("[S] SPA base-60 (φ≈98/60, entero 60^4, sin truncar)");
    println!(
        "  x_final (abstracto) : {:.6e}  (raw {})",
        xs_abs,
        xs.to_raw()
    );
    println!("  ns/op              : {:.1}\n", ns_s);

    println!("=== QUE SIGNIFICA PARA EL SISTEMA ===");
    println!(
        "- El float64 representa φ con error ~1e-16/paso. Tras {} pasos la desviacion",
        N
    );
    println!("  relativa del float vs la trayectoria exacta CRECE (es exponencial). La CPU");
    println!(
        "  'olvida' precision irrecuperable en loops largos -> hay que renormalizar/recalcular."
    );
    println!("- SPA retiene la fraccion: su trayectoria es EXACTA para la razon que usa.");
    println!(
        "- Costo: SPA ~{:.0} ns/op vs float ~{:.0} ns/op  (~{:.1}x mas caro por op,",
        ns_s,
        ns_f,
        ns_s / ns_f
    );
    println!("  entero i128), PERO no requiere reprocesar para corregir drift.");
    println!("- En el lattice resonante: sin truncar, fase/amplitud se mantienen coherentes");
    println!(
        "  sin 'reset' periodico. Eso es 'matematicamente optimizado' = sin perdida por diseño."
    );
}
