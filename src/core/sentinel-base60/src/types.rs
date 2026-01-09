//! Type aliases and zone calculation functions

use crate::S60;

/// Unsigned Base-60 integer (non-negative S60)
pub type U60 = S60;

/// Signed Base-60 integer (alias for S60)
pub type I60 = S60;

/// Calculate the zone (0-11) for a given residue modulo 60.
/// 
/// Based on the 12 divisors of 60: {1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60}
/// 
/// # Arguments
/// 
/// * `residue` - Value modulo 60 (0-59)
/// 
/// # Returns
/// 
/// Zone ID (0-11) or None if residue is invalid
/// 
/// # Example
/// 
/// ```
/// use sentinel_base60::types::get_zone;
/// 
/// assert_eq!(get_zone(0), Some(0));   // Perfect divisibility
/// assert_eq!(get_zone(30), Some(11)); // Divisible by 30
/// assert_eq!(get_zone(7), Some(1));   // Prime
/// ```
pub fn get_zone(residue: i64) -> Option<usize> {
    let r = residue.rem_euclid(60);
    
    match r {
        0 => Some(0),  // Perfect divisibility
        _ if is_prime_residue(r) => Some(1),  // Primes
        _ if r % 30 == 0 => Some(11), // Divisible by 30
        _ if r % 20 == 0 => Some(10), // Divisible by 20
        _ if r % 15 == 0 => Some(9),  // Divisible by 15
        _ if r % 12 == 0 => Some(8),  // Divisible by 12
        _ if r % 10 == 0 => Some(7),  // Divisible by 10
        _ if r % 6 == 0 => Some(6),   // Divisible by 6
        _ if r % 5 == 0 => Some(5),   // Divisible by 5
        _ if r % 4 == 0 => Some(4),   // Divisible by 4
        _ if r % 3 == 0 => Some(3),   // Divisible by 3
        _ if r % 2 == 0 => Some(2),   // Even
        _ => None,  // Composite non-divisor
    }
}

/// Check if a residue (mod 60) is prime within the 0-59 range.
fn is_prime_residue(r: i64) -> bool {
    matches!(r, 1 | 7 | 11 | 13 | 17 | 19 | 23 | 29 | 31 | 37 | 41 | 43 | 47 | 53 | 59)
}

/// Calculate threat score based on residue (0-100 scale).
/// 
/// - Primes: 95 (HIGH THREAT)
/// - Highly composite (6, 12, 30, 60): 10 (BENIGN)
/// - Others: Calculated via divisor density
/// 
/// # Example
/// 
/// ```
/// use sentinel_base60::types::calculate_threat_score;
/// 
/// assert_eq!(calculate_threat_score(7), 95);   // Prime - high threat
/// assert_eq!(calculate_threat_score(30), 10);  // Highly composite - benign
/// ```
pub fn calculate_threat_score(residue: i64) -> u8 {
    let r = residue.rem_euclid(60);
    
    if is_prime_residue(r) {
        return 95;
    }
    
    if matches!(r, 6 | 12 | 30 | 60) {
        return 10;
    }
    
    // Calculate based on divisor density
    let divisors_of_60 = [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60];
    let divisor_count = divisors_of_60.iter().filter(|&&d| r % d == 0).count();
    
    let score = 100 - (divisor_count * 10);
    score.max(0).min(100) as u8
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_zone_perfect_divisibility() {
        assert_eq!(get_zone(0), Some(0));
        assert_eq!(get_zone(60), Some(0));
    }

    #[test]
    fn test_zone_primes() {
        assert_eq!(get_zone(7), Some(1));
        assert_eq!(get_zone(13), Some(1));
        assert_eq!(get_zone(59), Some(1));
    }

    #[test]
    fn test_zone_divisors() {
        assert_eq!(get_zone(30), Some(11)); // Divisible by 30
        assert_eq!(get_zone(20), Some(10)); // Divisible by 20
        assert_eq!(get_zone(15), Some(9));  // Divisible by 15
    }

    #[test]
    fn test_threat_score_prime() {
        assert_eq!(calculate_threat_score(7), 95);
        assert_eq!(calculate_threat_score(13), 95);
    }

    #[test]
    fn test_threat_score_benign() {
        assert_eq!(calculate_threat_score(6), 10);
        assert_eq!(calculate_threat_score(12), 10);
        assert_eq!(calculate_threat_score(30), 10);
    }
}
