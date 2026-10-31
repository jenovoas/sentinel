// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/quantum/quantum_scheduler.rs
//! Task execution gated by observed portals, with a separate temporal model.
//!
//! Native callers supply the live portal observation and confirm execution with
//! `Result`. The C-compatible `tick` retains the temporal model for experiments;
//! its energy score is not a measurement of energy saved in production.

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
pub struct Task<C = extern "C" fn()> {
    /// Unique task identifier
    pub id: u64,
    /// Type of task
    pub task_type: TaskType,
    /// Nominal cost used by the model's energy score
    pub cost: u32,
    /// Work owned by the executor; C callers use a function pointer
    pub callback: C,
}

/// Scheduler statistics for telemetry
#[derive(Debug, Clone, Copy)]
pub struct SchedulerStats {
    /// Tasks successfully executed during portals
    pub tasks_in_portal: u64,
    /// Tasks successfully forced due to overflow
    pub tasks_forced: u64,
    /// Critical tasks successfully executed outside a portal
    pub tasks_critical: u64,
    /// Failed execution attempts, excluded from successful task counters
    pub tasks_failed: u64,
    /// Model energy score (can be negative), not measured savings
    pub energy_saved: i64,
    /// Portal successes divided by all successful executions (S60)
    pub efficiency: S60,
}

/// FIFO scheduler with a latched dead-man gate for non-critical work.
pub struct QuantumScheduler<C = extern "C" fn()> {
    /// Task queue (FIFO)
    task_queue: VecDeque<Task<C>>,
    pending_critical: usize,
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
    /// Counter: critical tasks executed outside portals
    tasks_critical: u64,
    /// Counter: execution failures
    tasks_failed: u64,
    /// Model energy score
    energy_saved: i64,
    pub is_emergency_shutdown: bool,
}

enum PortalSource {
    Observed(bool),
    TemporalModel,
}

#[derive(Clone, Copy)]
enum ExecutionKind {
    Portal,
    Overflow,
    Critical,
}

impl<C> QuantumScheduler<C> {
    /// Create a scheduler with a shared dead-man sensor.
    pub fn new(bio_ref: Arc<Mutex<BioResonator>>) -> Self {
        QuantumScheduler {
            task_queue: VecDeque::new(),
            pending_critical: 0,
            bio_resonator: bio_ref,
            portal_detector: PortalDetector::new(),
            overflow_limit: 20,
            tasks_in_portal: 0,
            tasks_forced: 0,
            tasks_critical: 0,
            tasks_failed: 0,
            energy_saved: 0,
            is_emergency_shutdown: false,
        }
    }

    /// Execute against the live, binary portal observation.
    ///
    /// A failed callback consumes that attempt, logs its task identity/error,
    /// and does not block later queued work or critical checkpoint attempts.
    ///
    /// Observed portals admit at most five queued tasks. Biological coherence
    /// is not a portal gate here; the dead-man latch still blocks non-critical
    /// work. Pending backups run outside the portal if they were not in its
    /// batch, even after the dead-man latch has been activated.
    pub fn tick_observed(
        &mut self,
        current_time: S60,
        portal_open: bool,
        mut execute: impl FnMut(C) -> Result<(), String>,
    ) {
        self.tick_with_source(
            current_time,
            PortalSource::Observed(portal_open),
            &mut execute,
        );
    }

    fn tick_with_source(
        &mut self,
        current_time: S60,
        source: PortalSource,
        execute: &mut impl FnMut(C) -> Result<(), String>,
    ) {
        let mut portal_open = false;
        if !self.is_emergency_shutdown {
            let (pilot_present, bio_portal) = {
                let mut bio = self.bio_resonator.lock().unwrap();
                bio.tick_entropy();
                let modeled_bio_portal =
                    matches!(&source, PortalSource::TemporalModel) && bio.is_portal_open();
                (bio.is_pilot_present(), modeled_bio_portal)
            };

            if !pilot_present {
                self.emergency_shutdown();
            } else {
                let batch_size = match source {
                    PortalSource::Observed(true) => 5,
                    PortalSource::Observed(false) => 0,
                    PortalSource::TemporalModel if bio_portal => {
                        let intensity = self.portal_detector.get_portal_intensity(current_time);
                        if intensity > S60::zero() {
                            Self::adaptive_batch_size(intensity)
                        } else {
                            0
                        }
                    }
                    PortalSource::TemporalModel => 0,
                };
                portal_open = batch_size > 0;
                if portal_open {
                    self.execute_batch(batch_size, execute);
                }
            }
        }

        // A pending backup is critical work, never overflow. Flush before
        // overflow so a backup at the front cannot be misclassified.
        self.flush_critical_tasks(execute);
        if !self.is_emergency_shutdown
            && !portal_open
            && self.task_queue.len() > self.overflow_limit
        {
            if let Some(task) = self.task_queue.pop_front() {
                self.execute_task(task, ExecutionKind::Overflow, execute);
            }
        }
    }

    /// Add owned work to the FIFO queue.
    pub fn enqueue(&mut self, task: Task<C>) {
        if task.task_type == TaskType::BackupS60 {
            self.pending_critical += 1;
        }
        self.task_queue.push_back(task);
    }

    /// Temporal-model batch sizing; observed portals have no invented score.
    fn adaptive_batch_size(resonance: S60) -> usize {
        let t90 = S60::from_raw(54 * S60::SCALE_1);
        let t85 = S60::from_raw(51 * S60::SCALE_1);
        let t80 = S60::from_raw(48 * S60::SCALE_1);

        if resonance > t90 {
            5
        } else if resonance > t85 {
            4
        } else if resonance > t80 {
            3
        } else {
            2
        }
    }

    fn execute_batch(
        &mut self,
        max_tasks: usize,
        execute: &mut impl FnMut(C) -> Result<(), String>,
    ) {
        let actual = max_tasks.min(self.task_queue.len());
        for _ in 0..actual {
            if let Some(task) = self.task_queue.pop_front() {
                self.execute_task(task, ExecutionKind::Portal, execute);
            }
        }
    }

    fn execute_task(
        &mut self,
        task: Task<C>,
        kind: ExecutionKind,
        execute: &mut impl FnMut(C) -> Result<(), String>,
    ) {
        if task.task_type == TaskType::BackupS60 {
            self.pending_critical -= 1;
        }
        match execute(task.callback) {
            Ok(()) => match kind {
                ExecutionKind::Portal => {
                    self.tasks_in_portal += 1;
                    self.energy_saved += i64::from(task.cost) * 2;
                }
                ExecutionKind::Overflow => {
                    self.tasks_forced += 1;
                    self.energy_saved -= i64::from(task.cost) * 2;
                }
                ExecutionKind::Critical => self.tasks_critical += 1,
            },
            Err(error) => {
                self.tasks_failed += 1;
                eprintln!(
                    "Scheduler task {} ({:?}) failed: {}",
                    task.id, task.task_type, error
                );
            }
        }
    }

    /// Latch the dead-man gate; critical work is handled on every tick.
    fn emergency_shutdown(&mut self) {
        eprintln!("DEAD MAN SWITCH ACTIVATED - PILOT ABSENT");
        self.is_emergency_shutdown = true;
    }

    pub fn is_emergency_shutdown(&self) -> bool {
        self.is_emergency_shutdown
    }

    /// Move each pending task once, retaining normal work in FIFO order.
    fn flush_critical_tasks(&mut self, execute: &mut impl FnMut(C) -> Result<(), String>) {
        if self.pending_critical == 0 {
            return;
        }
        let pending = self.task_queue.len();
        for _ in 0..pending {
            if let Some(task) = self.task_queue.pop_front() {
                if task.task_type == TaskType::BackupS60 {
                    self.execute_task(task, ExecutionKind::Critical, execute);
                } else {
                    // pop_front already freed this slot; reuse the allocation.
                    self.task_queue.push_back(task);
                }
            }
        }
    }

    fn successful_tasks(&self) -> u128 {
        u128::from(self.tasks_in_portal)
            + u128::from(self.tasks_forced)
            + u128::from(self.tasks_critical)
    }

    pub fn get_stats(&self) -> SchedulerStats {
        let total = self.successful_tasks();
        let efficiency = if total > 0 {
            S60::from_raw(
                (u128::from(self.tasks_in_portal) * S60::SCALE_0 as u128 / total) as i64,
            )
        } else {
            S60::zero()
        };

        SchedulerStats {
            tasks_in_portal: self.tasks_in_portal,
            tasks_forced: self.tasks_forced,
            tasks_critical: self.tasks_critical,
            tasks_failed: self.tasks_failed,
            energy_saved: self.energy_saved,
            efficiency,
        }
    }

    pub fn efficiency_percent(&self) -> Option<u64> {
        let total = self.successful_tasks();
        if total == 0 {
            return None;
        }
        Some((u128::from(self.tasks_in_portal) * 100 / total) as u64)
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
        self.tasks_critical = 0;
        self.tasks_failed = 0;
        self.energy_saved = 0;
    }
}

impl QuantumScheduler<extern "C" fn()> {
    /// Execute the temporal portal model for the existing C ABI/experiments.
    pub fn tick(&mut self, current_time: S60) {
        self.tick_with_source(current_time, PortalSource::TemporalModel, &mut |callback| {
            callback();
            Ok(())
        });
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn scheduler() -> QuantumScheduler<u64> {
        let bio = Arc::new(Mutex::new(BioResonator::new()));
        // Tests drive absence explicitly rather than depending on wall time.
        bio.lock().unwrap().set_dead_man_threshold(u64::MAX);
        QuantumScheduler::new(bio)
    }

    fn enqueue(scheduler: &mut QuantumScheduler<u64>, id: u64, task_type: TaskType) {
        scheduler.enqueue(Task {
            id,
            task_type,
            cost: 10,
            callback: id,
        });
    }

    #[test]
    fn observed_gate_is_binary_and_independent_of_bio_and_temporal_portals() {
        let mut scheduler = scheduler();
        let mut executed = Vec::new();
        for id in 0..7 {
            enqueue(&mut scheduler, id, TaskType::ZPETune);
        }

        scheduler.tick_observed(S60::zero(), false, |id| {
            executed.push(id);
            Ok(())
        });
        assert!(executed.is_empty());
        assert_eq!(scheduler.queue_len(), 7);

        // Both modeled portals are closed at zero, but observation is open.
        assert!(!scheduler.portal_detector.is_portal_open(S60::zero()));
        assert!(!scheduler.bio_resonator.lock().unwrap().is_portal_open());
        scheduler.tick_observed(S60::zero(), true, |id| {
            executed.push(id);
            Ok(())
        });
        assert_eq!(executed, [0, 1, 2, 3, 4]);
        assert_eq!(scheduler.queue_len(), 2);

        scheduler.tick_observed(S60::from_int(17), true, |id| {
            executed.push(id);
            Ok(())
        });
        assert_eq!(executed, [0, 1, 2, 3, 4, 5, 6]);
        let stats = scheduler.get_stats();
        assert_eq!(stats.tasks_in_portal, 7);
        assert_eq!(stats.tasks_forced, 0);
        assert_eq!(stats.tasks_critical, 0);
        assert_eq!(stats.energy_saved, 140);
        assert_eq!(stats.efficiency, S60::one());
    }

    #[test]
    fn temporal_model_requires_both_gates_and_uses_model_batch_size() {
        let mut scheduler = scheduler();
        let portal_time = (1..680)
            .map(|step| S60::from_raw(i64::from(step) * S60::SCALE_0 / 10))
            .find(|&time| scheduler.portal_detector.is_portal_open(time))
            .expect("the temporal model has portals in its 68-second window");
        let mut executed = Vec::new();
        for id in 0..7 {
            enqueue(&mut scheduler, id, TaskType::ZPETune);
        }

        scheduler.tick_with_source(
            portal_time,
            PortalSource::TemporalModel,
            &mut |id| {
                executed.push(id);
                Ok(())
            },
        );
        assert!(executed.is_empty());

        scheduler.bio_resonator.lock().unwrap().coherence = S60::one();
        scheduler.tick_with_source(
            S60::zero(),
            PortalSource::TemporalModel,
            &mut |id| {
                executed.push(id);
                Ok(())
            },
        );
        assert!(executed.is_empty());

        scheduler.tick_with_source(
            portal_time,
            PortalSource::TemporalModel,
            &mut |id| {
                executed.push(id);
                Ok(())
            },
        );
        let completed = executed.len();
        assert!((2..=5).contains(&completed));
        assert_eq!(executed, (0..completed as u64).collect::<Vec<_>>());
        assert_eq!(scheduler.queue_len(), 7 - completed);
        assert_eq!(scheduler.get_stats().tasks_in_portal, completed as u64);
    }

    #[test]
    fn closed_portal_flushes_backups_without_bio_before_normal_overflow() {
        let mut scheduler = scheduler();
        let mut executed = Vec::new();
        enqueue(&mut scheduler, 100, TaskType::BackupS60);
        for id in 0..=scheduler.overflow_limit as u64 {
            enqueue(&mut scheduler, id, TaskType::ZPETune);
        }

        scheduler.tick_observed(S60::zero(), false, |id| {
            executed.push(id);
            Ok(())
        });

        assert_eq!(executed, [100, 0]);
        assert_eq!(scheduler.queue_len(), scheduler.overflow_limit);
        let stats = scheduler.get_stats();
        assert_eq!(stats.tasks_in_portal, 0);
        assert_eq!(stats.tasks_critical, 1);
        assert_eq!(stats.tasks_forced, 1);
        assert_eq!(stats.energy_saved, -20);
        assert_eq!(stats.efficiency, S60::zero());
        assert_eq!(scheduler.efficiency_percent(), Some(0));
    }

    #[test]
    fn backups_outside_the_portal_batch_are_critical_not_portal_successes() {
        let mut scheduler = scheduler();
        let mut executed = Vec::new();
        for id in 0..6 {
            enqueue(&mut scheduler, id, TaskType::ZPETune);
        }
        enqueue(&mut scheduler, 6, TaskType::BackupS60);

        scheduler.tick_observed(S60::zero(), true, |id| {
            executed.push(id);
            Ok(())
        });

        assert_eq!(executed, [0, 1, 2, 3, 4, 6]);
        assert_eq!(scheduler.queue_len(), 1);
        assert_eq!(scheduler.task_queue.front().unwrap().callback, 5);
        let stats = scheduler.get_stats();
        assert_eq!(stats.tasks_in_portal, 5);
        assert_eq!(stats.tasks_critical, 1);
        assert_eq!(stats.tasks_forced, 0);
        assert_eq!(stats.energy_saved, 100);
        assert_eq!(
            stats.efficiency,
            S60::from_raw(5 * S60::SCALE_0 / 6)
        );
        assert_eq!(scheduler.efficiency_percent(), Some(83));
    }

    #[test]
    fn emergency_latch_retains_normals_and_flushes_backups_received_after_latch() {
        let mut scheduler = scheduler();
        let mut executed = Vec::new();
        scheduler.bio_resonator.lock().unwrap().set_dead_man_threshold(0);
        enqueue(&mut scheduler, 0, TaskType::ZPETune);
        enqueue(&mut scheduler, 100, TaskType::BackupS60);

        scheduler.tick_observed(S60::zero(), true, |id| {
            executed.push(id);
            Ok(())
        });
        assert!(scheduler.is_emergency_shutdown());
        assert_eq!(executed, [100]);

        {
            let mut bio = scheduler.bio_resonator.lock().unwrap();
            bio.set_dead_man_threshold(u64::MAX);
            bio.inject_bio_pulse();
            bio.coherence = S60::one();
        }
        for id in 1..=scheduler.overflow_limit as u64 {
            enqueue(&mut scheduler, id, TaskType::PhaseAlign);
        }
        enqueue(&mut scheduler, 101, TaskType::BackupS60);

        scheduler.tick_observed(S60::from_int(17), true, |id| {
            executed.push(id);
            Ok(())
        });
        scheduler.tick_observed(S60::from_int(34), false, |id| {
            executed.push(id);
            Ok(())
        });

        assert!(scheduler.is_emergency_shutdown());
        assert_eq!(executed, [100, 101]);
        assert_eq!(scheduler.queue_len(), scheduler.overflow_limit + 1);
        assert_eq!(
            scheduler.task_queue.iter().map(|task| task.callback).collect::<Vec<_>>(),
            (0..=scheduler.overflow_limit as u64).collect::<Vec<_>>()
        );
        let stats = scheduler.get_stats();
        assert_eq!(stats.tasks_in_portal, 0);
        assert_eq!(stats.tasks_forced, 0);
        assert_eq!(stats.tasks_critical, 2);
        assert_eq!(stats.tasks_failed, 0);
        assert_eq!(stats.energy_saved, 0);
    }

    #[test]
    fn portal_failures_do_not_count_success_and_preserve_remaining_fifo() {
        let mut scheduler = scheduler();
        let mut attempted = Vec::new();
        for id in 0..7 {
            enqueue(&mut scheduler, id, TaskType::ZPETune);
        }
        enqueue(&mut scheduler, 100, TaskType::BackupS60);

        scheduler.tick_observed(S60::zero(), true, |id| {
            attempted.push(id);
            if id == 1 {
                Err("execution did not complete".to_owned())
            } else {
                Ok(())
            }
        });

        assert_eq!(attempted, [0, 1, 2, 3, 4, 100]);
        assert_eq!(
            scheduler.task_queue.iter().map(|task| task.callback).collect::<Vec<_>>(),
            [5, 6]
        );
        let stats = scheduler.get_stats();
        assert_eq!(stats.tasks_in_portal, 4);
        assert_eq!(stats.tasks_critical, 1);
        assert_eq!(stats.tasks_forced, 0);
        assert_eq!(stats.tasks_failed, 1);
        assert_eq!(stats.energy_saved, 80);
        assert_eq!(scheduler.efficiency_percent(), Some(80));

        scheduler.tick_observed(S60::zero(), true, |id| {
            attempted.push(id);
            Ok(())
        });
        assert_eq!(attempted, [0, 1, 2, 3, 4, 100, 5, 6]);
        assert!(scheduler.is_queue_empty());
        assert_eq!(scheduler.get_stats().tasks_failed, 1);
    }

    #[test]
    fn failed_critical_flush_does_not_block_other_backups_or_discard_normals() {
        let mut scheduler = scheduler();
        let mut attempted = Vec::new();
        scheduler.bio_resonator.lock().unwrap().set_dead_man_threshold(0);
        enqueue(&mut scheduler, 0, TaskType::ZPETune);
        enqueue(&mut scheduler, 100, TaskType::BackupS60);
        enqueue(&mut scheduler, 1, TaskType::PhaseAlign);
        enqueue(&mut scheduler, 101, TaskType::BackupS60);

        scheduler.tick_observed(S60::zero(), true, |id| {
            attempted.push(id);
            if id == 100 {
                Err("checkpoint write failed".to_owned())
            } else {
                Ok(())
            }
        });

        assert_eq!(attempted, [100, 101]);
        assert_eq!(
            scheduler.task_queue.iter().map(|task| task.callback).collect::<Vec<_>>(),
            [0, 1]
        );
        let stats = scheduler.get_stats();
        assert_eq!(stats.tasks_failed, 1);
        assert_eq!(stats.tasks_critical, 1);
        assert_eq!(stats.tasks_in_portal, 0);
        assert_eq!(stats.tasks_forced, 0);
        assert_eq!(stats.energy_saved, 0);
        assert!(scheduler.is_emergency_shutdown());
    }

    #[test]
    fn failed_overflow_does_not_apply_penalty_or_discard_later_work() {
        let mut scheduler = scheduler();
        let mut attempted = Vec::new();
        for id in 0..=scheduler.overflow_limit as u64 {
            enqueue(&mut scheduler, id, TaskType::ZPETune);
        }

        scheduler.tick_observed(S60::zero(), false, |id| {
            attempted.push(id);
            Err("forced execution failed".to_owned())
        });

        assert_eq!(attempted, [0]);
        assert_eq!(scheduler.task_queue.front().unwrap().callback, 1);
        assert_eq!(scheduler.queue_len(), scheduler.overflow_limit);
        let stats = scheduler.get_stats();
        assert_eq!(stats.tasks_failed, 1);
        assert_eq!(stats.tasks_forced, 0);
        assert_eq!(stats.tasks_in_portal, 0);
        assert_eq!(stats.tasks_critical, 0);
        assert_eq!(stats.energy_saved, 0);
        assert_eq!(scheduler.efficiency_percent(), None);
    }


    #[test]
    fn backup_completed_in_a_portal_is_not_flushed_or_counted_twice() {
        let mut scheduler = scheduler();
        let mut executed = Vec::new();
        enqueue(&mut scheduler, 100, TaskType::BackupS60);
        enqueue(&mut scheduler, 1, TaskType::ZPETune);

        scheduler.tick_observed(S60::zero(), true, |id| {
            executed.push(id);
            Ok(())
        });
        scheduler.tick_observed(S60::zero(), false, |id| {
            executed.push(id);
            Ok(())
        });

        assert_eq!(executed, [100, 1]);
        let stats = scheduler.get_stats();
        assert_eq!(stats.tasks_in_portal, 2);
        assert_eq!(stats.tasks_critical, 0);
        assert_eq!(stats.tasks_forced, 0);
        assert_eq!(stats.tasks_failed, 0);
        assert_eq!(stats.energy_saved, 40);
        assert_eq!(stats.efficiency, S60::one());
        assert!(scheduler.is_queue_empty());
    }
}
