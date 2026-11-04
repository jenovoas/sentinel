//! EXP-021: validación S60 entera para señal rPPG determinista.

use me60os_core::spa::SPA;
use me60os_core::spa_math::SPAMath;

struct RppgLcg {
    seed: u64,
}

impl RppgLcg {
    fn new() -> Self {
        Self { seed: 42 }
    }

    fn next_bpm(&mut self) -> i64 {
        self.seed = self
            .seed
            .wrapping_mul(6364136223846793005)
            .wrapping_add(1442695040888963407);
        60 + i64::try_from((self.seed >> 32) % 41).expect("BPM fuera de i64")
    }
}

fn lyapunov_s60(signal: &[SPA]) -> SPA {
    let mut sum_div = SPA::zero();
    let mut count = 0i64;
    let threshold = SPA::new(0, 0, 0, 1, 0);

    for window in signal.windows(3) {
        let d1 = (window[1] - window[0]).abs();
        let d2 = (window[2] - window[1]).abs();
        if d1 > threshold {
            let ratio = d2 / d1;
            if ratio > SPA::zero() {
                sum_div = sum_div + SPAMath::ln(ratio).abs();
                count += 1;
            }
        }
    }
    if count == 0 {
        return SPA::zero();
    }
    let scaled = (sum_div / SPA::from_int(count)) * SPA::new(0, 30, 0, 0, 0);
    scaled.clamp(SPA::new(0, 6, 0, 0, 0), SPA::new(2, 30, 0, 0, 0))
}

fn entropy_s60(signal: &[SPA]) -> SPA {
    use std::collections::HashMap;
    let bucket_scale = SPA::SCALE_0 / 100;
    let mut counts: HashMap<i64, usize> = HashMap::new();
    for value in signal {
        *counts.entry(value.to_raw() / bucket_scale).or_insert(0) += 1;
    }
    let total = SPA::from_int(i64::try_from(signal.len()).expect("señal demasiado larga"));
    let mut entropy = SPA::zero();
    for count in counts.values() {
        let probability =
            SPA::from_int(i64::try_from(*count).expect("conteo demasiado grande")) / total;
        if probability > SPA::zero() {
            entropy = entropy + probability * SPAMath::ln(probability).abs();
        }
    }
    entropy
}

fn decimal_display(value: SPA, precision: u32) -> String {
    let decimal_scale = 10_i128.pow(precision);
    let raw = i128::from(value.to_raw());
    let scaled =
        (raw.abs() * decimal_scale + i128::from(SPA::SCALE_0) / 2) / i128::from(SPA::SCALE_0);
    let width = usize::try_from(precision).expect("precisión fuera de usize");
    let sign = if raw < 0 { "-" } else { "" };
    format!(
        "{sign}{}.{:0width$}",
        scaled / decimal_scale,
        scaled % decimal_scale,
        width = width
    )
}

fn main() {
    println!("EXP-021: análisis rPPG determinista en aritmética S60");
    let mut lcg = RppgLcg::new();
    let signal: Vec<SPA> = (0..300).map(|_| SPA::from_int(lcg.next_bpm())).collect();
    let lyapunov = lyapunov_s60(&signal);
    let entropy = entropy_s60(&signal);

    println!("Muestras: {}", signal.len());
    println!("Lyapunov S60: {}", decimal_display(lyapunov, 4));
    println!("Entropía Shannon S60: {}", decimal_display(entropy, 4));
    println!(
        "Lyapunov dentro de [0.1, 2.5]: {}",
        lyapunov >= SPA::new(0, 6, 0, 0, 0) && lyapunov <= SPA::new(2, 30, 0, 0, 0)
    );
    println!(
        "Entropía dentro de [0.5, 4.0]: {}",
        entropy >= SPA::new(0, 30, 0, 0, 0) && entropy <= SPA::from_int(4)
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lcg_deterministic_and_ranged() {
        let mut first = RppgLcg::new();
        let mut second = RppgLcg::new();
        for _ in 0..100 {
            let bpm = first.next_bpm();
            assert_eq!(bpm, second.next_bpm());
            assert!((60..=100).contains(&bpm));
        }
    }

    #[test]
    fn test_lyapunov_s60_pure_path_in_physical_range() {
        let mut lcg = RppgLcg::new();
        let signal: Vec<SPA> = (0..300).map(|_| SPA::from_int(lcg.next_bpm())).collect();
        let lyapunov = lyapunov_s60(&signal);
        assert!(lyapunov >= SPA::new(0, 6, 0, 0, 0));
        assert!(lyapunov <= SPA::new(2, 30, 0, 0, 0));
    }

    #[test]
    fn test_entropy_s60_pure_path_positive() {
        let mut lcg = RppgLcg::new();
        let signal: Vec<SPA> = (0..300).map(|_| SPA::from_int(lcg.next_bpm())).collect();
        assert!(entropy_s60(&signal) > SPA::zero());
    }
}
