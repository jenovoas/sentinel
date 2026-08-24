// AUDIT-360 Phase 7: Tests for portal_detector.rs
use sentinel_cortex::math::s60::S60;
use sentinel_cortex::quantum::portal_detector::PortalDetector;

#[test]
fn test_portal_detector_creation() {
    let _pd = PortalDetector::new();
}

#[test]
fn test_portal_resonance_at_zero() {
    let pd = PortalDetector::new();
    let res = pd.calculate_resonance(S60::ZERO);
    // At t=0, all sin(0) = 0, so resonance should be 0 or very close
    let _ = res; // just verify it doesn't panic
}

#[test]
fn test_portal_open_threshold() {
    let pd = PortalDetector::new();
    // At t=0, resonance should be low, portal likely closed
    let _open = pd.is_portal_open(S60::ZERO);
    // Just verify it doesn't panic
}

#[test]
fn test_portal_intensity() {
    let pd = PortalDetector::new();
    let intensity = pd.get_portal_intensity(S60::ZERO);
    // At t=0, intensity should be zero (below threshold)
    assert_eq!(intensity._value, 0); // sin(0) = 0 -> below threshold -> zero
}

#[test]
fn test_portal_resonance_nonzero_time() {
    let pd = PortalDetector::new();
    let t = S60::from_raw(S60::SCALE_0); // t = 1.0
    let _res = pd.calculate_resonance(t);
    // Just verify it doesn't panic
}
