// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🌌 TEST E2E: RECONSTRUCCIÓN HOLOGRÁFICA EN MALLA (P0.1)
//!
//! Demuestra el ciclo integrado de extremo a extremo exigido por P0.1:
//! 1. Nodo A (Emisor Sentinel + QHC): Inyección PAI de datos y bombeo armónico.
//! 2. Sincronización SHM: Condensación del estado a semilla compacta de 32 bytes
//!    (HolographicSeedBinary) con invariante cúbica (q+r+s=0) y CRC16.
//! 3. Transporte Malla MyCNet: Encapsulación en datagrama FractalMeshPacket de 40B
//!    (8B header magic 0x4D594353 + 32B payload) y deserialización sin copia.
//! 4. Nodo B (Receptor Sentinel): Ingesta por simpatía, acoplamiento DTC/QHC,
//!    apertura de portal de convergencia dual y reconstrucción exacta al 100%.

use me60os_core::qhc::QhcTensor;
use me60os_core::shm_bridge::PySharedBuffer;
use me60os_core::spa::SPA;
use sentinel_cortex::memory::crystal_runtime::CrystalRuntime;
use std::sync::atomic::{AtomicU64, Ordering};

const FRACTAL_HEADER_BYTES: usize = 64;
const FRACTAL_SEED_BYTES: usize = 32;
const FRACTAL_SEEDS_CAPACITY: usize = 1024;
const MYCS_MAGIC: [u8; 4] = [0x4D, 0x59, 0x43, 0x53]; // "MYCS"

/// Layout binario de la semilla fractal holográfica (32 bytes exactos).
#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct HolographicSeedBinary {
    token_id: u32,
    coord_q: i32,
    coord_r: i32,
    coord_s: i32,
    amplitude_s60: i64,
    phase_sector: u8,
    yhwh_pulse: u8,
    flags: u16,
    crc16: u16,
    reserved: [u8; 2],
}

const _: () = assert!(
    std::mem::size_of::<HolographicSeedBinary>() == FRACTAL_SEED_BYTES,
    "HolographicSeedBinary debe medir exactamente 32 bytes"
);

impl HolographicSeedBinary {
    fn from_bytes(bytes: &[u8; 32]) -> Result<Self, &'static str> {
        let mut token_bytes = [0_u8; 4];
        token_bytes.copy_from_slice(&bytes[0..4]);
        let token_id = u32::from_le_bytes(token_bytes);

        let mut q_bytes = [0_u8; 4];
        q_bytes.copy_from_slice(&bytes[4..8]);
        let coord_q = i32::from_le_bytes(q_bytes);

        let mut r_bytes = [0_u8; 4];
        r_bytes.copy_from_slice(&bytes[8..12]);
        let coord_r = i32::from_le_bytes(r_bytes);

        let mut s_bytes = [0_u8; 4];
        s_bytes.copy_from_slice(&bytes[12..16]);
        let coord_s = i32::from_le_bytes(s_bytes);

        let mut amp_bytes = [0_u8; 8];
        amp_bytes.copy_from_slice(&bytes[16..24]);
        let amplitude_s60 = i64::from_le_bytes(amp_bytes);

        let phase_sector = bytes[24];
        let yhwh_pulse = bytes[25];

        let mut flags_bytes = [0_u8; 2];
        flags_bytes.copy_from_slice(&bytes[26..28]);
        let flags = u16::from_le_bytes(flags_bytes);

        let mut crc_bytes = [0_u8; 2];
        crc_bytes.copy_from_slice(&bytes[28..30]);
        let crc16 = u16::from_le_bytes(crc_bytes);

        // 1. Verificación de invariante cúbica hexagonal: q + r + s == 0
        if coord_q
            .checked_add(coord_r)
            .and_then(|sum| sum.checked_add(coord_s))
            != Some(0)
        {
            return Err("Invariante cúbica hexagonal violada (q + r + s != 0)");
        }

        // 2. Verificación de checksum CRC16-CCITT sobre los primeros 28 bytes
        let computed_crc = crc16_ccitt(&bytes[..28]);
        if computed_crc != crc16 {
            return Err("Checksum CRC16-CCITT inválido");
        }

        Ok(Self {
            token_id,
            coord_q,
            coord_r,
            coord_s,
            amplitude_s60,
            phase_sector,
            yhwh_pulse,
            flags,
            crc16,
            reserved: [bytes[30], bytes[31]],
        })
    }

    fn to_bytes(self) -> [u8; 32] {
        let mut bytes = [0_u8; 32];
        bytes[0..4].copy_from_slice(&self.token_id.to_le_bytes());
        bytes[4..8].copy_from_slice(&self.coord_q.to_le_bytes());
        bytes[8..12].copy_from_slice(&self.coord_r.to_le_bytes());
        bytes[12..16].copy_from_slice(&self.coord_s.to_le_bytes());
        bytes[16..24].copy_from_slice(&self.amplitude_s60.to_le_bytes());
        bytes[24] = self.phase_sector;
        bytes[25] = self.yhwh_pulse;
        bytes[26..28].copy_from_slice(&self.flags.to_le_bytes());
        bytes[28..30].copy_from_slice(&self.crc16.to_le_bytes());
        bytes[30..32].copy_from_slice(&self.reserved);
        bytes
    }
}

/// Datagrama de transporte UDP en malla MyCNet (40 bytes exactos).
struct FractalMeshPacket {
    sequence_id: u16,
    seed: HolographicSeedBinary,
}

impl FractalMeshPacket {
    fn new(sequence_id: u16, seed: HolographicSeedBinary) -> Self {
        Self { sequence_id, seed }
    }

    fn to_bytes(&self) -> [u8; 40] {
        let mut packet = [0_u8; 40];
        packet[0..4].copy_from_slice(&MYCS_MAGIC);
        packet[4..6].copy_from_slice(&1_u16.to_le_bytes()); // version = 1
        packet[6..8].copy_from_slice(&self.sequence_id.to_le_bytes());
        packet[8..40].copy_from_slice(&self.seed.to_bytes());
        packet
    }

    fn from_bytes(bytes: &[u8; 40]) -> Result<Self, &'static str> {
        if bytes[0..4] != MYCS_MAGIC {
            return Err("Magic inválido: no es paquete FractalMeshPacket (MYCS)");
        }
        let mut ver_bytes = [0_u8; 2];
        ver_bytes.copy_from_slice(&bytes[4..6]);
        let version = u16::from_le_bytes(ver_bytes);
        if version != 1 {
            return Err("Versión de protocolo no soportada");
        }
        let mut seq_bytes = [0_u8; 2];
        seq_bytes.copy_from_slice(&bytes[6..8]);
        let sequence_id = u16::from_le_bytes(seq_bytes);

        let mut seed_bytes = [0_u8; 32];
        seed_bytes.copy_from_slice(&bytes[8..40]);
        let seed = HolographicSeedBinary::from_bytes(&seed_bytes)?;

        Ok(Self { sequence_id, seed })
    }
}

fn crc16_ccitt(bytes: &[u8]) -> u16 {
    let mut crc = 0xFFFF_u16;
    for &byte in bytes {
        crc ^= u16::from(byte) << 8;
        for _ in 0..8 {
            crc = if crc & 0x8000 != 0 {
                (crc << 1) ^ 0x1021
            } else {
                crc << 1
            };
        }
    }
    crc
}

/// Buffer circular SHM aislado para tests de integración.
struct IsolatedFractalRing {
    #[allow(dead_code)]
    name: String,
    buffer: PySharedBuffer,
}

impl IsolatedFractalRing {
    fn new() -> Self {
        static COUNTER: AtomicU64 = AtomicU64::new(0);
        let id = COUNTER.fetch_add(1, Ordering::Relaxed);
        let name = format!("/sentinel-e2e-fractal-{}-{id}", std::process::id());
        let total_size = FRACTAL_HEADER_BYTES + FRACTAL_SEEDS_CAPACITY * FRACTAL_SEED_BYTES;
        let buffer = PySharedBuffer::new(name.clone(), total_size, true)
            .expect("creación de PySharedBuffer para test");

        // Inicializar header canónico SFR1 (64 bytes)
        let _ = buffer.write_native(0, &0x5346_5231_u32.to_le_bytes()); // "SFR1"
        let _ = buffer.write_native(4, &1_u32.to_le_bytes()); // version = 1
        let _ = buffer.store_u64_release(8, 0); // head = 0
        let _ = buffer.store_u64_release(16, 0); // tail = 0
        let _ = buffer.write_native(24, &[0_u8; 40]); // reserved

        Self { name, buffer }
    }

    fn poll_seed(&self, slot: usize) -> Result<HolographicSeedBinary, &'static str> {
        let offset = FRACTAL_HEADER_BYTES + (slot % FRACTAL_SEEDS_CAPACITY) * FRACTAL_SEED_BYTES;
        let bytes = self
            .buffer
            .read_native(offset, FRACTAL_SEED_BYTES)
            .map_err(|_| "Error leyendo SHM")?;
        let mut arr = [0_u8; 32];
        arr.copy_from_slice(&bytes);
        HolographicSeedBinary::from_bytes(&arr)
    }
}

impl Drop for IsolatedFractalRing {
    fn drop(&mut self) {
        self.buffer.unlink();
    }
}

#[test]
fn test_holographic_seed_binary_cubic_invariant_and_crc() {
    let q = 1_i32;
    let r = -2_i32;
    let s = -q - r; // 1 + (-2) + 1 = 0
    assert_eq!(q + r + s, 0);

    let mut raw = [0_u8; 32];
    raw[0..4].copy_from_slice(&77_u32.to_le_bytes());
    raw[4..8].copy_from_slice(&q.to_le_bytes());
    raw[8..12].copy_from_slice(&r.to_le_bytes());
    raw[12..16].copy_from_slice(&s.to_le_bytes());
    let amp = 65 * SPA::SCALE_0; // 'A'
    raw[16..24].copy_from_slice(&amp.to_le_bytes());
    raw[24] = 10; // phase_sector
    raw[25] = 10; // yhwh_pulse
    raw[26..28].copy_from_slice(&1_u16.to_le_bytes());
    let crc = crc16_ccitt(&raw[..28]);
    raw[28..30].copy_from_slice(&crc.to_le_bytes());

    let seed = HolographicSeedBinary::from_bytes(&raw).expect("Semilla válida");
    assert_eq!(seed.token_id, 77);
    assert_eq!(seed.coord_q, 1);
    assert_eq!(seed.coord_r, -2);
    assert_eq!(seed.coord_s, 1);
    assert_eq!(seed.amplitude_s60, amp);
    assert_eq!(seed.to_bytes(), raw);
}

#[test]
fn test_fractal_mesh_packet_roundtrip_40_bytes() {
    let q = 2_i32;
    let r = -1_i32;
    let s = -q - r;
    let mut raw = [0_u8; 32];
    raw[0..4].copy_from_slice(&123_u32.to_le_bytes());
    raw[4..8].copy_from_slice(&q.to_le_bytes());
    raw[8..12].copy_from_slice(&r.to_le_bytes());
    raw[12..16].copy_from_slice(&s.to_le_bytes());
    raw[16..24].copy_from_slice(&(89 * SPA::SCALE_0).to_le_bytes()); // 'Y'
    raw[24] = 5;
    raw[25] = 10;
    raw[26..28].copy_from_slice(&1_u16.to_le_bytes());
    let crc = crc16_ccitt(&raw[..28]);
    raw[28..30].copy_from_slice(&crc.to_le_bytes());

    let seed = HolographicSeedBinary::from_bytes(&raw).expect("Semilla válida");
    let packet = FractalMeshPacket::new(42, seed);
    let bytes = packet.to_bytes();
    assert_eq!(bytes.len(), 40);

    let decoded = FractalMeshPacket::from_bytes(&bytes).expect("Decodificación de paquete");
    assert_eq!(decoded.sequence_id, 42);
    assert_eq!(decoded.seed, seed);
}

#[test]
fn test_e2e_holographic_reconstruction_pipeline() {
    // -------------------------------------------------------------------------
    // 1. INICIALIZACIÓN DEL NODO A (Emisor) Y NODO B (Receptor)
    // -------------------------------------------------------------------------
    const NODES: usize = 37; // Topología hexagonal estándar 3-ring
    let mut node_a = CrystalRuntime::in_memory(NODES);
    let mut node_b = CrystalRuntime::in_memory(NODES);

    let qhc = QhcTensor::new();

    // -------------------------------------------------------------------------
    // 2. PRE-ACONDICIONAMIENTO ARMÓNICO (Bombeo QHC 10;5,6,5 + Salto-17)
    // -------------------------------------------------------------------------
    // Ambos nodos corren su director de orquesta DTC para estabilizar el vacío fonónico
    for _ in 0..4 {
        let _ = node_a.tick_dtc();
        let _ = node_b.tick_dtc();
    }

    // -------------------------------------------------------------------------
    // 3. INYECCIÓN PAI DE DATOS EN NODO A
    // -------------------------------------------------------------------------
    // Payload canónico de prueba: 'Yo Soy' (bytes: [89, 111, 32, 83, 111, 121])
    let payload = b"Yo Soy";
    let target_node = 0_usize;

    // Inyectamos el primer carácter 'Y' (ASCII 89) vía PAI sexagesimal en el nodo A
    let char_val = i64::from(payload[0]); // 89
    node_a.inject_security_pai(target_node, char_val, 1);

    // Verificamos que la amplitud en Lane A del nodo A se inyectó con la escala exacta
    let amplitudes_a = node_a.amplitudes_raw();
    assert_eq!(
        amplitudes_a[target_node],
        char_val * SPA::SCALE_0,
        "La escala SPA debe ser exacta: char * SCALE_0"
    );

    // -------------------------------------------------------------------------
    // 4. PUBLICACIÓN Y EXTRACCIÓN DE SEMILLA EN SHM (Contrato FFI 32B)
    // -------------------------------------------------------------------------
    let ring = IsolatedFractalRing::new();

    // Simulamos la condensación del estado de Nodo A a semilla fractal en SHM
    let token_id = 1001_u32;
    let (coord_q, coord_r) = (0_i32, 0_i32);
    let coord_s = -coord_q - coord_r;
    let phase_mod = qhc.get_phase_modulation(node_a.status().qhc_tick);

    let mut seed_raw = [0_u8; 32];
    seed_raw[0..4].copy_from_slice(&token_id.to_le_bytes());
    seed_raw[4..8].copy_from_slice(&coord_q.to_le_bytes());
    seed_raw[8..12].copy_from_slice(&coord_r.to_le_bytes());
    seed_raw[12..16].copy_from_slice(&coord_s.to_le_bytes());
    seed_raw[16..24].copy_from_slice(&amplitudes_a[target_node].to_le_bytes());
    seed_raw[24] = 0; // phase sector
    seed_raw[25] = phase_mod; // YHWH pulse (10, 5, 6, o 5)
    seed_raw[26..28].copy_from_slice(&1_u16.to_le_bytes()); // flags: snapped
    let crc = crc16_ccitt(&seed_raw[..28]);
    seed_raw[28..30].copy_from_slice(&crc.to_le_bytes());

    // Escribir en el ring buffer SHM
    let slot = 0_usize;
    let offset = FRACTAL_HEADER_BYTES + slot * FRACTAL_SEED_BYTES;
    ring.buffer
        .write_native(offset, &seed_raw)
        .expect("Escritura en SHM");
    ring.buffer
        .store_u64_release(8, 1)
        .expect("Avance del puntero head");

    // -------------------------------------------------------------------------
    // 5. TRANSPORTE EN MALLA MYCNET (FractalMeshPacket UDP 40B)
    // -------------------------------------------------------------------------
    // El SentinelFractalBridge de MyCNet lee del ring SHM
    let extracted_seed = ring.poll_seed(slot).expect("Lectura válida de SHM");
    assert_eq!(extracted_seed.amplitude_s60, char_val * SPA::SCALE_0);
    assert_eq!(
        extracted_seed.coord_q + extracted_seed.coord_r + extracted_seed.coord_s,
        0
    );

    // Empaquetar en datagrama UDP de 40B
    let mesh_packet = FractalMeshPacket::new(1, extracted_seed);
    let udp_datagram = mesh_packet.to_bytes();
    assert_eq!(udp_datagram.len(), 40);

    // Simulación del tránsito de red: recepción y desempaquetado en Nodo B
    let received_packet =
        FractalMeshPacket::from_bytes(&udp_datagram).expect("Recepción íntegra de datagrama");
    assert_eq!(
        received_packet.seed.amplitude_s60,
        extracted_seed.amplitude_s60
    );

    // -------------------------------------------------------------------------
    // 6. INGESTA EN NODO B Y ACOPLAMIENTO ARMÓNICO
    // -------------------------------------------------------------------------
    // Nodo B recibe la semilla y la proyecta a su carril de seguridad
    let remote_amp = SPA::from_raw(received_packet.seed.amplitude_s60);
    let inject_res = node_b.inject_remote_security_spa(target_node, remote_amp);
    assert!(inject_res.is_ok(), "Inyección en Nodo B debe tener éxito");

    // También inyectamos al carril de observabilidad para probar convergencia dual
    node_b.inject_observability_spa(target_node, remote_amp);

    // -------------------------------------------------------------------------
    // 7. COMPROBACIÓN DE CONVERGENCIA DUAL Y RECONSTRUCCIÓN EXACTA
    // -------------------------------------------------------------------------
    // Comprobar que ambas lanes en el nodo destino convergen armónicamente
    assert!(
        node_b.dual_lane_portal_open(),
        "El portal de convergencia dual debe abrir al coincidir amplitudes y fases"
    );

    // Extracción y decodificación exacta del dato reconstruido en Nodo B
    let reconstructed_raw = node_b.amplitudes_raw()[target_node];
    assert_eq!(
        reconstructed_raw,
        char_val * SPA::SCALE_0,
        "La amplitud reconstruida en Nodo B debe coincidir exactamente con el valor original"
    );

    let recovered_char_code = reconstructed_raw / SPA::SCALE_0;
    let recovered_char = u8::try_from(recovered_char_code).expect("Código ASCII válido");
    assert_eq!(
        recovered_char, payload[0],
        "El carácter reconstruido 'Y' debe ser 100% idéntico"
    );

    // -------------------------------------------------------------------------
    // 8. PROPAGACIÓN MULTI-BYTE ('Yo Soy') POR SIMPATÍA SEXAGESIMAL
    // -------------------------------------------------------------------------
    let mut node_e2e_src = CrystalRuntime::in_memory(NODES);
    let mut node_e2e_dst = CrystalRuntime::in_memory(NODES);

    let mut recovered_string = String::new();

    for (idx, &byte) in payload.iter().enumerate() {
        let val = i64::from(byte);
        let node_idx = idx % NODES;

        // Inyectar en origen
        node_e2e_src.inject_security_pai(node_idx, val, 1);

        // Generar semilla de 32B
        let mut s_raw = [0_u8; 32];
        s_raw[0..4].copy_from_slice(&(u32::try_from(idx).unwrap()).to_le_bytes());
        s_raw[4..8].copy_from_slice(&0_i32.to_le_bytes());
        s_raw[8..12].copy_from_slice(&0_i32.to_le_bytes());
        s_raw[12..16].copy_from_slice(&0_i32.to_le_bytes());
        let amp = val * SPA::SCALE_0;
        s_raw[16..24].copy_from_slice(&amp.to_le_bytes());
        s_raw[24] = 0;
        s_raw[25] = 10;
        s_raw[26..28].copy_from_slice(&1_u16.to_le_bytes());
        let c = crc16_ccitt(&s_raw[..28]);
        s_raw[28..30].copy_from_slice(&c.to_le_bytes());

        // Transferir vía paquete de red de 40B
        let s = HolographicSeedBinary::from_bytes(&s_raw).unwrap();
        let p = FractalMeshPacket::new(u16::try_from(idx).unwrap(), s);
        let net_bytes = p.to_bytes();

        // Recibir en destino
        let r_packet = FractalMeshPacket::from_bytes(&net_bytes).unwrap();
        node_e2e_dst
            .inject_remote_security_spa(node_idx, SPA::from_raw(r_packet.seed.amplitude_s60))
            .unwrap();

        // Reconstrucción determinista en destino
        let dst_raw = node_e2e_dst.amplitudes_raw()[node_idx];
        let ch = u8::try_from(dst_raw / SPA::SCALE_0).unwrap();
        recovered_string.push(char::from(ch));
    }

    assert_eq!(
        recovered_string, "Yo Soy",
        "Reconstrucción completa de la semilla 'Yo Soy' debe tener fidelidad idéntica al 100%"
    );
}
