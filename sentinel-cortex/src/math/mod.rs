//! # 🛡️ S60 MATH CONSOLIDATION - SENTINEL CORTEX 🛡️
//!
//! Unified math bridge via me60os_core/SPA (60^4 accuracy).
//! Compliant with YATRA Protocol: ZERO DECIMAL CONTAMINATION.

pub mod harmonic_logic;

/// Legacy S60 module bridge
pub mod s60 {
    pub use me60os_core::spa::SPA as S60;
}

/// S60 Math function bridge
pub mod s60_math {
    pub use me60os_core::spa_math::SPAMath;
    pub use me60os_core::spa_math::SPAMath as S60Math;
}

// Global re-exports for the Cortex
pub use me60os_core::spa::SPA as S60;
pub use me60os_core::spa_math::SPAMath;
