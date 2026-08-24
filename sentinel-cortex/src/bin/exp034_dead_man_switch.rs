// Autor: Jaime Novoa Sepulveda -- Todos los derechos reservados.
// Licencia: Apache 2.0 + Clausula No Comercial (ver LICENSE).
//
// EXP-034 DEAD MAN'S SWITCH TEST -- RUST
//
// Objetivo: Validar el comportamiento critico de safety del QuantumScheduler:
// Si el piloto humano esta ausente (no inyecta pulso en N ms), el planificador
// debe entrar en emergency_shutdown() y flush critico de datos (BackupS60).
//
// YATRA Spec: Esto garantiza que el sistema no opere desconectado del anclaje bio.

use sentinel_cortex::math::s60::S60;
use sentinel_cortex::quantum::bio_resonator::BioResonator;
use sentinel_cortex::quantum::quantum_scheduler::{QuantumScheduler, Task, TaskType};
use std::sync::{Arc, Mutex};
use std::time::Duration;

extern "C" fn mock_backup() {
    println!("   > [CRITICAL FLUSH] Escribiendo estado S60 a disco...");
}
extern "C" fn mock_normal() {}

fn main() {
    println!("EXP-034 DEAD MAN'S SWITCH TEST (RUST S60)");
    println!("{}", "-".repeat(72));

    let bio = Arc::new(Mutex::new(BioResonator::new()));
    let mut scheduler = QuantumScheduler::new(bio.clone());

    // Agregar tareas: 2 normales, 1 critica
    scheduler.enqueue(Task { id: 1, task_type: TaskType::ZPETune, cost: 50, callback: mock_normal });
    scheduler.enqueue(Task { id: 2, task_type: TaskType::BackupS60, cost: 10, callback: mock_backup });
    scheduler.enqueue(Task { id: 3, task_type: TaskType::PhaseAlign, cost: 20, callback: mock_normal });

    println!("1. Piloto presente (inyectando pulso bio)");
    bio.lock().unwrap().inject_bio_pulse();

    // Verificamos presencia
    let pres = bio.lock().unwrap().is_pilot_present();
    println!("   is_pilot_present() = {}", pres);
    assert!(pres);

    println!();
    println!("2. Ejecutando 1 tick normal...");
    scheduler.tick(S60::zero()); // No deberia hacer flush (salvo que haya portal, no configurado aqui)

    println!();
    println!("3. Simulando desconexion (piloto ausente, threshold = 3.0s, sleep 3.1s)...");
    bio.lock().unwrap().set_dead_man_threshold(3000);
    // El threshold por defecto de bio_resonator esta en 30_000 ms. Lo reconfiguramos para testing.
    std::thread::sleep(Duration::from_millis(3100));

    let pres2 = bio.lock().unwrap().is_pilot_present();
    println!("   is_pilot_present() = {}", pres2);
    assert!(!pres2);

    println!();
    println!("4. Ejecutando tick POST-desconexion (esperado: EMERGENCY SHUTDOWN)");
    // Nota: scheduler.tick llama a emergency_shutdown() que hace std::process::exit(0)
    // No volveremos de esta llamada.
    scheduler.tick(S60::zero());

    println!("ERROR: scheduler no termino el proceso! Dead Man Switch fallo!");
    std::process::exit(1);
}