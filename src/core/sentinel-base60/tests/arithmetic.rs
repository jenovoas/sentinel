//! Arithmetic operation tests for S60

use sentinel_base60::{S60, s60};

#[test]
fn test_addition_simple() {
    let a = s60![0; 30];  // 30 minutes
    let b = s60![0; 45];  // 45 minutes
    let sum = a + b;
    
    assert_eq!(sum, s60![1; 15]);  // 1 degree 15 minutes
}

#[test]
fn test_addition_with_carry() {
    let a = s60![0; 40, 50];  // 40 minutes 50 seconds
    let b = s60![0; 30, 20];  // 30 minutes 20 seconds
    let sum = a + b;
    
    // 40m50s + 30m20s = 70m70s = 71m10s = 1d11m10s
    assert_eq!(sum.degrees(), 1);
    assert_eq!(sum.minutes(), 11);
    assert_eq!(sum.seconds(), 10);
}

#[test]
fn test_subtraction_simple() {
    let a = s60![1; 15];  // 1 degree 15 minutes
    let b = s60![0; 30];  // 30 minutes
    let diff = a - b;
    
    assert_eq!(diff, s60![0; 45]);  // 45 minutes
}

#[test]
fn test_subtraction_with_borrow() {
    let a = s60![2; 10, 20];  // 2 degrees 10 minutes 20 seconds
    let b = s60![0; 30, 40];  // 30 minutes 40 seconds
    let diff = a - b;
    
    // 2d10m20s - 0d30m40s = 1d39m40s (after normalization)
    assert_eq!(diff.degrees(), 1);
    assert_eq!(diff.minutes(), 39);
    assert_eq!(diff.seconds(), 40);
}

#[test]
fn test_scalar_multiplication() {
    let val = s60![0; 10];  // 10 minutes
    let result = val * 6;    // 60 minutes = 1 degree
    
    assert_eq!(result, s60![1; 0]);
}

#[test]
fn test_scalar_multiplication_with_carry() {
    let val = s60![0; 15, 30];  // 15 minutes 30 seconds
    let result = val * 4;        // 60m 120s = 62m = 1d2m
    
    assert_eq!(result.degrees(), 1);
    assert_eq!(result.minutes(), 2);
    assert_eq!(result.seconds(), 0);
}

#[test]
fn test_floor_division_simple() {
    let val = s60![1; 0];  // 1 degree
    let result = val / 2;   // 0.5 degrees = 30 minutes
    
    assert_eq!(result, s60![0; 30]);
}

#[test]
fn test_floor_division_complex() {
    let val = s60![1; 0, 0];  // 1 degree
    let result = val / 3;      // 1/3 degree = 20 minutes exactly
    
    assert_eq!(result.degrees(), 0);
    assert_eq!(result.minutes(), 20);
    assert_eq!(result.seconds(), 0);
}

#[test]
fn test_multiplication_then_division_identity() {
    let original = s60![5; 30, 45];
    let scaled = original.clone() * 7;
    let restored = scaled / 7;
    
    assert_eq!(restored, original);
}

#[test]
fn test_python_parity_addition() {
    // Matches Python: S60(0, 30) + S60(0, 45) = S60(1, 15)
    let a = S60::new(&[0, 30, 0]);
    let b = S60::new(&[0, 45, 0]);
    let sum = a + b;
    
    assert_eq!(sum.degrees(), 1);
    assert_eq!(sum.minutes(), 15);
}

#[test]
fn test_python_parity_multiplication() {
    // Matches Python: S60(0, 3, 31, 45, 52) * 17 ≈ S60(1, 0, 0, 0, 0)
    let salto_17 = S60::new(&[0, 3, 31, 45, 52]);
    let result = salto_17 * 17;
    
    // Should be very close to 1 degree
    // 1/17 * 17 has minor residual due to precision truncation
    assert!(result.degrees() >= 0 && result.degrees() <= 1);
    // The result should be close to 1 degree with some residual in minutes
    if result.degrees() == 0 {
        // If it's 0 degrees, minutes should be close to 60
        assert!(result.minutes() >= 59);
    } else {
        // If it's 1 degree, that's also acceptable
        assert_eq!(result.degrees(), 1);
    }
}

#[test]
fn test_reference_arithmetic() {
    let a = s60![0; 30];
    let b = s60![0; 20];
    
    // Test that reference arithmetic works
    let sum = &a + &b;
    let diff = &a - &b;
    let scaled = &a * 2;
    let divided = &a / 2;
    
    assert_eq!(sum, s60![0; 50]);
    assert_eq!(diff, s60![0; 10]);
    assert_eq!(scaled, s60![1; 0]);
    assert_eq!(divided, s60![0; 15]);
}
