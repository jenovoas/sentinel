//! Publica metadatos KV por UDP MYKV v1, sin escribir el ring de Cortex.
//! Uso: kv_publish <crystal-clave|portal-metrics-clave> <valor-local>.
//! Éxito solo tras Committed de mycnetd. No transporta ni recupera payload remoto.
use me60os_core::liquid_memory::{LiquidMemory, ReplicableSeed};

fn main() -> Result<(), String> {
    let usage = "uso: kv_publish <crystal-clave|portal-metrics-clave> <valor-local>";
    let mut args = std::env::args().skip(1);
    let key = args.next().ok_or_else(|| usage.to_string())?;
    let value = args.next().ok_or_else(|| usage.to_string())?;
    if args.next().is_some() {
        return Err(usage.to_string());
    }
    let mut mem = LiquidMemory::new(64);
    mem.store(&key, value.as_bytes())?;
    let seed: ReplicableSeed = mem.replicate(&key)?;
    mem.publish(&seed)?;
    let key_hash = blake3::hash(key.as_bytes());
    let digest = key_hash.as_bytes();
    let token = u32::from_le_bytes([digest[0], digest[1], digest[2], digest[3]]);
    println!(
        "Committed metadatos clave='{key}' token_id={token} timestamp_ns={} amplitude_raw={} payload_hash={} (payload remoto no transferido)",
        seed.timestamp_ns,
        seed.amplitude_raw,
        blake3::Hash::from(seed.hash).to_hex()
    );
    Ok(())
}
