//! Decimal contamination prevention tests

use sentinel_base60::S60;

#[test]
fn test_integer_creation_allowed() {
    // This should work fine - integers are allowed
    let val = S60::new(&[10, 30, 45]);
    assert_eq!(val.degrees(), 10);
}

#[test]
fn test_from_degrees_allowed() {
    // This should work fine - integers are allowed
    let val = S60::from_degrees(42);
    assert_eq!(val.degrees(), 42);
}

#[test]
fn test_legacy_import_function_exists() {
    // The legacy import function should exist for importing old data
    let val = S60::from_decimal_FOR_IMPORT_ONLY(10.5);
    
    // 10.5 degrees = 10 degrees 30 minutes
    assert_eq!(val.degrees(), 10);
    assert_eq!(val.minutes(), 30);
}

#[test]
fn test_legacy_import_precision() {
    // Test that legacy import maintains precision
    let val = S60::from_decimal_FOR_IMPORT_ONLY(1.0 / 3.0);
    
    // 1/3 degree ≈ 0 degrees 20 minutes
    assert_eq!(val.degrees(), 0);
    assert_eq!(val.minutes(), 20);
}

#[test]
fn test_no_direct_float_in_new() {
    // Note: Rust's type system prevents passing f64 to new(&[i64])
    // This test documents that the type system itself provides protection
    
    // The following would not compile:
    // let val = S60::new(&[10.5, 20.3]);  // Compile error!
    
    // This is GOOD - the type system enforces purity
    assert!(true);
}

#[test]
fn test_arithmetic_preserves_exactness() {
    // Verify that Base-60 arithmetic is exact (no floating-point errors)
    let one_third = S60::new(&[0, 20, 0]);  // 1/3 degree = 20 minutes
    let result = one_third.clone() * 3;
    
    // Should be exactly 1 degree, not 0.999999...
    assert_eq!(result.degrees(), 1);
    assert_eq!(result.minutes(), 0);
}

#[test]
fn test_division_exactness() {
    // Test that division maintains exactness for Base-60 friendly fractions
    let one_degree = S60::new(&[1, 0, 0]);
    
    // 1/2
    let half = one_degree.clone() / 2;
    assert_eq!(half, S60::new(&[0, 30, 0]));
    
    // 1/3
    let third = one_degree.clone() / 3;
    assert_eq!(third, S60::new(&[0, 20, 0]));
    
    // 1/4
    let quarter = one_degree.clone() / 4;
    assert_eq!(quarter, S60::new(&[0, 15, 0]));
    
    // 1/5
    let fifth = one_degree.clone() / 5;
    assert_eq!(fifth, S60::new(&[0, 12, 0]));
    
    // 1/6
    let sixth = one_degree.clone() / 6;
    assert_eq!(sixth, S60::new(&[0, 10, 0]));
}

#[test]
fn test_no_floating_point_drift() {
    // Perform many operations and verify no drift
    let mut val = S60::new(&[1, 0, 0]);
    
    // Divide by 3, multiply by 3, repeat 100 times
    for _ in 0..100 {
        val = val.clone() / 3;
        val = val * 3;
    }
    
    // Should still be exactly 1 degree
    assert_eq!(val.degrees(), 1);
    assert_eq!(val.minutes(), 0);
}

#[test]
#[should_panic(expected = "Division by zero")]
fn test_division_by_zero_panics() {
    let val = S60::new(&[1, 0, 0]);
    let _ = val / 0;  // Should panic
}
