//! # S60 Math Module
//!
//! S60 base-60 arithmetic for the swarm.

pub mod s60;
pub mod s60_legacy;
pub mod s60_math;
pub mod harmonic_logic;

pub use s60::{S60, S60Error};

// SPA and SPAMath available for modules that need me60os SPA directly
pub use me60os_core::SPA;
pub use me60os_core::spa_math::SPAMath;
