// AUDIT-360 Phase 7: Unit tests for sentinel-cortex/src/math/s60.rs (226 LOC, 0 tests)
use sentinel_cortex::math::s60::S60;

#[test]
fn test_s60_zero() {
    assert_eq!(S60::ZERO._value, 0);
}

#[test]
fn test_s60_one() {
    assert_eq!(S60::ONE._value, 12_960_000);
}

#[test]
fn test_s60_from_raw() {
    let v = S60::from_raw(42);
    assert_eq!(v._value, 42);
}

#[test]
fn test_s60_new_valid() {
    let v = S60::new(1, 0, 0, 0, 0).unwrap();
    assert_eq!(v._value, 12_960_000);
}

#[test]
fn test_s60_new_components() {
    let v = S60::new(0, 30, 0, 0, 0).unwrap();
    assert_eq!(v._value, 6_480_000); // 30/60 = 0.5 -> 6_480_000
}

#[test]
fn test_s60_new_invalid() {
    assert!(S60::new(0, 60, 0, 0, 0).is_err());
    assert!(S60::new(0, 0, 60, 0, 0).is_err());
    assert!(S60::new(0, 0, 0, 60, 0).is_err());
}

#[test]
fn test_s60_add() {
    let a = S60::from_raw(100);
    let b = S60::from_raw(200);
    let c = a + b;
    assert_eq!(c._value, 300);
}

#[test]
fn test_s60_sub() {
    let a = S60::from_raw(500);
    let b = S60::from_raw(200);
    let c = a - b;
    assert_eq!(c._value, 300);
}

#[test]
fn test_s60_mul() {
    let a = S60::from_raw(S60::SCALE_0); // 1.0
    let b = S60::from_raw(S60::SCALE_0 / 2); // 0.5
    let c = a * b;
    assert_eq!(c._value, S60::SCALE_0 / 2); // 1.0 * 0.5 = 0.5
}

#[test]
fn test_s60_div() {
    let a = S60::from_raw(S60::SCALE_0); // 1.0
    let b = S60::from_raw(2 * S60::SCALE_0); // 2.0
    let c = (a / b).unwrap();
    assert_eq!(c._value, S60::SCALE_0 / 2); // 1.0 / 2.0 = 0.5
}
