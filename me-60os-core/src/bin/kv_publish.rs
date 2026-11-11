//! Publica una clave KV de prueba en el anillo fractal SHM local.
//! Uso: kv_publish <clave> <valor>. Requiere el anillo publicado por
//! mycnetd/cortex (no lo crea). Fase 1 memoria-kv-distribuida.
use me60os_core::liquid_memory::{LiquidMemory, ReplicableSeed};

fn main() {
    let mut args = std::env::args().skip(1);
    let key = args.next().expect("uso: kv_publish <clave> <valor>");
    let value = args.next().expect("uso: kv_publish <clave> <valor>");
    let mut mem = LiquidMemory::new(64);
    mem.store(&key, value.as_bytes()).expect("store local");
    let seed: ReplicableSeed = mem.replicate(&key).expect("replicate");
    mem.publish(&seed).expect("publish al anillo");
    let key_hash = blake3::hash(key.as_bytes());
    let digest = key_hash.as_bytes();
    let token = u32::from_le_bytes([digest[0], digest[1], digest[2], digest[3]]);
    println!(
        "publicada clave '{key}' ({} B) al anillo fractal, token_id={token}",
        key.len()
    );
}
