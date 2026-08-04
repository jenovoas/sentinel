// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// 💾 RAM METER — migración de quantum_lite.get_available_memory_gb (psutil -> sysinfo)
//
// Lee la RAM disponible y dimensiona el lattice hexagonal según capacidad,
// en aritmética S60 pura (sin float).

use crate::spa::SPA;
use sysinfo::System;

/// RAM disponible en GB (S60). Semántica idéntica a `quantum_lite`:
/// `psutil.virtual_memory().available // (1024**3)`.
pub fn available_memory_gb_s60() -> SPA {
    let mut sys = System::new_all();
    sys.refresh_memory();
    let gb = sys.available_memory() / (1024u64 * 1024 * 1024);
    SPA::from_int(gb as i64)
}

/// RAM disponible en bytes.
pub fn available_memory_bytes() -> u64 {
    let mut sys = System::new_all();
    sys.refresh_memory();
    sys.available_memory()
}

/// Nodos en un anillo hexagonal de orden n: H_n = 3n(n+1)+1.
/// n=150 ≈ 67.951 nodos (rejilla de producción).
pub fn hexagonal_ring_nodes(ring: usize) -> usize {
    3 * ring * (ring + 1) + 1
}

/// Mayor orden de anillo `n` cuyo lattice cabe en `avail_bytes`,
/// dado `bytes_per_node`, acotado por `max_ring`. Busqueda binaria.
pub fn recommend_lattice_ring(avail_bytes: u64, bytes_per_node: usize, max_ring: usize) -> usize {
    if bytes_per_node == 0 {
        return 0;
    }
    let mut lo = 0usize;
    let mut hi = max_ring;
    let mut best = 0usize;
    while lo <= hi {
        let mid = lo + (hi - lo) / 2;
        let nodes = hexagonal_ring_nodes(mid) as u64;
        let needed = nodes * bytes_per_node as u64;
        if needed <= avail_bytes {
            best = mid;
            lo = mid + 1;
        } else {
            hi = mid.saturating_sub(1);
        }
    }
    best
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hex_ring_150_is_67951() {
        // Ring 150 => 3*150*151 + 1 = 67951 (~67.9k nodos de producción)
        assert_eq!(hexagonal_ring_nodes(150), 67951);
        assert_eq!(hexagonal_ring_nodes(1), 7);
    }

    #[test]
    fn test_recommend_ring_respects_budget() {
        // Nodo de 100 bytes. Con 1 MB => pocos anillos. Con presupuesto enorme => tope en max_ring.
        let bp = 100usize;
        let small = recommend_lattice_ring(1_000_000, bp, 400);
        assert!(hexagonal_ring_nodes(small) * bp <= 1_000_000);
        let huge = recommend_lattice_ring(u64::MAX, bp, 400);
        assert_eq!(huge, 400);
    }

    #[test]
    fn test_available_memory_positive() {
        // No podemos predecir el valor, pero en una laptop viva debe ser > 0.
        assert!(available_memory_bytes() > 0);
        assert!(available_memory_gb_s60().to_raw() >= 0);
    }
}
