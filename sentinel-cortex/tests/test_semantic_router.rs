// AUDIT-360 Phase 7: Tests for semantic_router.rs
use sentinel_cortex::quantum::semantic_router::{Intent, SemanticRouter};

#[test]
fn test_semantic_router_creation() {
    // This should not panic even without GOOGLE_API_KEY
    let _router = SemanticRouter::new();
}

#[tokio::test]
async fn test_classify_without_api_key() {
    let router = SemanticRouter::new();
    // Without GOOGLE_API_KEY, should return Unknown intent
    let (intent, msg) = router.classify("test query").await;
    assert_eq!(intent, Intent::Unknown);
    assert!(
        msg.contains("Missing GOOGLE_API_KEY")
            || msg.contains("API Request")
            || msg.contains("Failed")
    );
}

#[test]
fn test_intent_variants() {
    assert_ne!(Intent::Oracle, Intent::Unknown);
    assert_ne!(Intent::SystemAction, Intent::SafetyCheck);
    assert_eq!(Intent::Unknown.clone(), Intent::Unknown);
}
