// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/quantum/quantum_scheduler.rs
//! Quantum Scheduler - Adiabatic Task Orchestration
//!
//! Implements portal-locked task execution for maximum energy efficiency.
//! Based on EXP-029-V2 optimizations achieving 94.4% portal-lock efficiency.
//
// Quantum task orchestration primitives. Currently exercised through the
// lib.rs integration harness; many methods are ready for future wiring.
#![allow(dead_code)]

use crate::math::s60::S60;
use crate::quantum::bio_resonator::BioResonator;
use crate::quantum::portal_detector::PortalDetector;
use std::collections::VecDeque;
use std::sync::{Arc, Mutex};

/// Task types for Sentinel operations
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum TaskType {
    /// ZPE Reactor tuning
    ZPETune,
    /// BCI synchronization
    BCISync,
    /// Lattice garbage collection
    LatticeGC,
    /// S60 state backup (critical)
    BackupS60,
    /// Phase alignment
    PhaseAlign,
}

/// A task to be scheduled
pub struct Task {
    /// Unique task identifier
    pub id: u64,
    /// Type of task
    pub task_type: TaskType,
    /// Energy cost in Joules
    pub cost: u32,
    /// Callback function pointer (C-compatible)
    pub callback: extern "C" fn(),
}

/// Scheduler statistics for telemetry
#[derive(Debug, Clone, Copy)]
pub struct SchedulerStats {
    /// Tasks executed during portals
    pub tasks_in_portal: u64,
    /// Tasks forced due to overflow
    pub tasks_forced: u64,
    /// Net energy saved (can be negative)
    pub energy_saved: i64,
    /// Portal-lock efficiency (S60)
    pub efficiency: S60,
}

/// Quantum Scheduler - Adiabatic task execution
pub struct QuantumScheduler {
    /// Task queue (FIFO)
    task_queue: VecDeque<Task>,
    /// Reference to BioResonator
    bio_resonator: Arc<Mutex<BioResonator>>,
    /// Portal detector instance
    portal_detector: PortalDetector,
    /// Maximum queue size before forced execution
    overflow_limit: usize,
    /// Counter: tasks executed in portal
    tasks_in_portal: u64,
    /// Counter: tasks forced (overflow)
    tasks_forced: u64,
    /// Net energy saved
    energy_saved: i64,
    /// Current time in S60 (updated each tick)
    current_time: S60,
    pub is_emergency_shutdown: bool,
}

impl QuantumScheduler {
    /// Create new scheduler with BioResonator reference
    pub fn new(bio_ref: Arc<Mutex<BioResonator>>) -> Self {
        QuantumScheduler {
            task_queue: VecDeque::new(),
            bio_resonator: bio_ref,
            portal_detector: PortalDetector::new(),
            overflow_limit: 20, // V2 optimized
            tasks_in_portal: 0,
            tasks_forced: 0,
            energy_saved: 0,
            current_time: S60::zero(),
            is_emergency_shutdown: false,
        }
    }

    /// Main tick - called by TimeCrystal @ 41.77 Hz
    pub fn tick(&mut self, current_time: S60) {
        self.current_time = current_time;

        // 1. Decay bio-resonance entropy
        {
            let mut bio = self.bio_resonator.lock().unwrap();
            bio.tick_entropy();
        }

        // 2. Check Dead Man's Switch
        let pilot_absent = {
            let bio = self.bio_resonator.lock().unwrap();
            !bio.is_pilot_present()
        };
        if pilot_absent {
            self.emergency_shutdown();
            return;
        }

        // 3. Check portals
        let penta_portal = self.portal_detector.is_portal_open(current_time);
        let bio_portal = {
            let bio = self.bio_resonator.lock().unwrap();
            bio.is_portal_open()
        };

        // 4. Execute if DUAL PORTAL (both conditions met)
        if penta_portal && bio_portal && !self.task_queue.is_empty() {
            let batch_size = self.adaptive_batch_size(current_time);
            self.execute_batch(batch_size);
        }
        // 5. Overflow handler
        else if self.task_queue.len() > self.overflow_limit {
            self.force_execute_one();
        }
    }

    /// Add task to queue
    pub fn enqueue(&mut self, task: Task) {
        self.task_queue.push_back(task);
    }

    /// Adaptive batch sizing based on resonance intensity
    fn adaptive_batch_size(&self, t: S60) -> usize {
        let resonance = self.portal_detector.calculate_resonance(t);

        // Thresholds in S60:
        let t90 = S60::from_raw(54 * S60::SCALE_1);
        let t85 = S60::from_raw(51 * S60::SCALE_1);
        let t80 = S60::from_raw(48 * S60::SCALE_1);

        if resonance > t90 {
            5 // Strong resonance
        } else if resonance > t85 {
            4
        } else if resonance > t80 {
            3
        } else {
            2 // Minimum batch
        }
    }

    /// Execute batch of tasks (portal-locked)
    fn execute_batch(&mut self, max_tasks: usize) {
        let actual = std::cmp::min(max_tasks, self.task_queue.len());

        for _ in 0..actual {
            if let Some(task) = self.task_queue.pop_front() {
                // Execute callback
                (task.callback)();

                // Update metrics
                self.tasks_in_portal += 1;
                self.energy_saved += (task.cost as i64) * 2; // Adiabatic bonus
            }
        }
    }

    /// Force execute one task (overflow)
    fn force_execute_one(&mut self) {
        if let Some(task) = self.task_queue.pop_front() {
            (task.callback)();

            self.tasks_forced += 1;
            self.energy_saved -= (task.cost as i64) * 2; // Entropy penalty
        }
    }

    /// Emergency shutdown - Dead Man's Switch activated
    fn emergency_shutdown(&mut self) {
        eprintln!("⚠️  DEAD MAN SWITCH ACTIVATED - PILOT ABSENT");
        eprintln!("🛑 INITIATING EMERGENCY SHUTDOWN...");

        self.is_emergency_shutdown = true;
        self.flush_critical_tasks();
    }

    pub fn is_emergency_shutdown(&self) -> bool {
        self.is_emergency_shutdown
    }

    /// Flush only critical tasks (BackupS60)
    fn flush_critical_tasks(&mut self) {
        let tasks: Vec<Task> = self.task_queue.drain(..).collect();
        for task in tasks {
            if task.task_type == TaskType::BackupS60 {
                (task.callback)();
            }
        }
    }

    /// Get current statistics
    pub fn get_stats(&self) -> SchedulerStats {
        let total = self.tasks_in_portal + self.tasks_forced;
        let efficiency = if total > 0 {
            let num = S60::from_int(self.tasks_in_portal as i32);
            let den = S60::from_int(total as i32);
            match num / den {
                Ok(val) => val,
                Err(_) => S60::zero(),
            }
        } else {
            S60::zero()
        };

        SchedulerStats {
            tasks_in_portal: self.tasks_in_portal,
            tasks_forced: self.tasks_forced,
            energy_saved: self.energy_saved,
            efficiency,
        }
    }

    pub fn queue_len(&self) -> usize {
        self.task_queue.len()
    }
    pub fn is_queue_empty(&self) -> bool {
        self.task_queue.is_empty()
    }
    pub fn reset_stats(&mut self) {
        self.tasks_in_portal = 0;
        self.tasks_forced = 0;
        self.energy_saved = 0;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    extern "C" fn dummy_callback() {}

    #[test]
    fn test_scheduler_creation() {
        let bio = Arc::new(Mutex::new(BioResonator::new()));
        let scheduler = QuantumScheduler::new(bio);
        assert!(scheduler.is_queue_empty());
    }

    #[test]
    fn test_get_stats_initial() {
        let bio = Arc::new(Mutex::new(BioResonator::new()));
        let scheduler = QuantumScheduler::new(bio);
        let stats = scheduler.get_stats();
        assert_eq!(stats.tasks_in_portal, 0);
        assert_eq!(stats.efficiency, S60::zero());
    }
}
