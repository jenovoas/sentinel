// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! soma_orchestrator.rs — SOMA v4.0 Central Nervous System (Rust Edition)
//! Orquestador Resonante con Context-Push y Ciclo QHC
//! -----------------------------------------------------------------------------

use anyhow::Result;
use redis::AsyncCommands;
use std::path::Path;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tokio::fs;
use tokio::process::Command;
use tracing::{error, info, warn};

// Importar desde el core de me60os
use me60os_core::guardian_lsm::GuardianLsm;
use me60os_core::time_crystal::LiquidLattice;
use std::sync::Arc;
use tokio::sync::Mutex;

// --- Configuración Dinámica ---
fn get_env_var(key: &str, default: &str) -> String {
    std::env::var(key).unwrap_or_else(|_| default.to_string())
}

/// Umbral de coherencia para despachar tareas: 600/1000 = 0.60 (escala Base-60, sin floats)
const UMBRAL_DISPATCH: u64 = 600;
const BASE_TICK_MS: u64 = 500;
const SNAPSHOT_INTERVAL_TICKS: u64 = 120; // ~1 min

struct Orchestrator {
    redis_client: redis::Client,
    lattice: Arc<Mutex<LiquidLattice>>,
    guardian: GuardianLsm,
    snapshot_path: String,
    memory_path: String,
}

impl Orchestrator {
    async fn new() -> Result<Self> {
        let redis_host = get_env_var("REDIS_HOST", "localhost");
        let redis_port = get_env_var("REDIS_PORT", "6379");
        let redis_url = format!("redis://{}:{}/", redis_host, redis_port);
        let client = redis::Client::open(redis_url)?;

        let snapshot_path = get_env_var(
            "SNAPSHOT_PATH",
            "/home/jnovoas/.local/state/swarm/crystal_snapshot.json",
        );
        let memory_path = get_env_var(
            "MEMORY_PATH",
            "/home/jnovoas/SecurePenguin/memory/MEMORY.md",
        );

        // Inicializar lattice con 60 slots (PAI-60 standard)
        let lattice = Arc::new(Mutex::new(LiquidLattice::new(60)));
        let guardian = GuardianLsm::new(lattice.clone());

        Ok(Self {
            redis_client: client,
            lattice,
            guardian,
            snapshot_path,
            memory_path,
        })
    }

    async fn get_system_state(
        &mut self,
        conn: &mut redis::aio::MultiplexedConnection,
    ) -> Result<(String, u64)> {
        // En SOMA v4.0, la fase y coherencia viven en el Crystal Lattice (Rust)
        // Pero Redis sigue siendo el canal de comunicación para otros agentes.
        let phase: String = conn
            .get("swarm:crystal:phase")
            .await
            .unwrap_or_else(|_| "YOD".to_string());
        // Coherencia en Redis almacenada como u64 x1000 (ej: "600" = 0.60)
        let coherence_str: String = conn
            .get("swarm:crystal:coherence")
            .await
            .unwrap_or_else(|_| "0".to_string());
        let coherence: u64 = coherence_str.parse().unwrap_or(0);

        // Sincronizar estado de Redis -> Lattice local
        let mut lattice = self.lattice.lock().await;
        lattice.buffer.phase = phase.clone();
        lattice.buffer.coherence = coherence;

        Ok((phase, coherence))
    }

    async fn prepare_context(
        &mut self,
        conn: &mut redis::aio::MultiplexedConnection,
        task_id: &str,
        task_data: &std::collections::HashMap<String, String>,
    ) -> Result<String> {
        // 1. Obtener reglas (RAG First / Redis)
        let mut context = String::new();

        // 1.1 Leer memoria viva (Redis) con Sanitización Semántica (TruthSync / ScvEngine)
        let scv = me60os_core::scv::ScvEngine::new();

        let handoff: std::collections::HashMap<String, String> = conn
            .hgetall("swarm:session:handoff")
            .await
            .unwrap_or_default();
        if !handoff.is_empty() {
            context.push_str("=== SWARM HANDOFF ===\n");
            for (k, v) in handoff {
                let (is_valid, _score, _entropy, _kw) = scv.analyze(&v);
                if is_valid {
                    context.push_str(&format!("{}: {}\n", k, v));
                } else {
                    warn!("🛡️ SOMA [TELEMETRY SANITIZER]: Descartada telemetría maliciosa en handoff (clave: {})", k);
                }
            }
        }

        let sys_status: std::collections::HashMap<String, String> = conn
            .hgetall("swarm:system:status")
            .await
            .unwrap_or_default();
        if !sys_status.is_empty() {
            context.push_str("\n=== SYSTEM STATUS ===\n");
            for (k, v) in sys_status {
                let (is_valid, _score, _entropy, _kw) = scv.analyze(&v);
                if is_valid {
                    context.push_str(&format!("{}: {}\n", k, v));
                } else {
                    warn!("🛡️ SOMA [TELEMETRY SANITIZER]: Descartada telemetría sospechosa en status (clave: {})", k);
                }
            }
        }

        // 1.2 Leer respaldo RAG (Archivos)
        let memory_rules = fs::read_to_string(&self.memory_path)
            .await
            .unwrap_or_default();
        if !memory_rules.is_empty() {
            context.push_str("\n=== MEMORY (RAG) ===\n");
            context.push_str(&memory_rules);
        }

        // 2. Inyectar contexto en el LiquidLattice (Memoria de Cristal)
        let context_a = task_data
            .get("description")
            .cloned()
            .unwrap_or_default()
            .into_bytes();
        let context_b = task_id.as_bytes().to_vec();
        {
            let mut lattice = self.lattice.lock().await;
            lattice.inject_dual_channel(context_a, context_b);
        }

        // 3. Construir System Prompt (Context-Push)
        let system_prompt = format!(
            "{}\n\n--- INSTRUCCIONES DE TAREA ---\nID: {}\nDescripción: {}\nScope: {}\n",
            context,
            task_id,
            task_data.get("description").unwrap_or(&"".to_string()),
            task_data.get("scope").unwrap_or(&"local".to_string())
        );

        // 4. Generar solicitud para el LLM Gateway
        let now = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();
        let req_id = format!("soma_{}_{}", task_id, now);
        let req_key = format!("swarm:llm:req:{}", req_id);

        let model_tier = if task_data.get("is_sensitive") == Some(&"1".to_string()) {
            "deep"
        } else {
            "fast"
        };

        let _: () = redis::pipe()
            .hset(&req_key, "id", &req_id)
            .hset(
                &req_key,
                "prompt",
                task_data
                    .get("prompt")
                    .or(task_data.get("description"))
                    .unwrap_or(&"".to_string()),
            )
            .hset(&req_key, "system", &system_prompt)
            .hset(
                &req_key,
                "agent_id",
                task_data.get("agent").unwrap_or(&"soma_worker".to_string()),
            )
            .hset(
                &req_key,
                "node",
                task_data.get("scope").unwrap_or(&"local".to_string()),
            )
            .hset(&req_key, "model_tier", model_tier)
            .hset(&req_key, "created_at", now)
            .expire(&req_key, 600)
            .query_async(conn)
            .await?;

        // 5. Encolar
        let _: () = conn.lpush("swarm:llm:queue", &req_id).await?;
        Ok(req_id)
    }

    async fn dispatch_task(
        &mut self,
        conn: &mut redis::aio::MultiplexedConnection,
        task_id: &str,
    ) -> Result<()> {
        let task_key = format!("swarm:task:{}", task_id);
        let task_data: std::collections::HashMap<String, String> = conn.hgetall(&task_key).await?;
        if task_data.is_empty() {
            anyhow::bail!("Tarea {} no encontrada para despacho", task_id);
        }

        info!(
            "🚀 Procesando Tarea {} via SOMA v4.0 (Rust Core)...",
            task_id
        );

        // --- GUARDIAN LSM CHECK ---
        let description = task_data.get("description").cloned().unwrap_or_default();
        if !self
            .guardian
            .verify_action("soma-rs", "dispatch_task", &description)
            .await
        {
            warn!("🛑 GUARDIAN: Acción bloqueada para tarea {}", task_id);
            let _: () = conn
                .hset(&task_key, "status", "blocked_by_guardian")
                .await?;
            return Ok(());
        }

        // --- PREPARE CONTEXT & GET REQ_ID ---
        let llm_req_id = self.prepare_context(conn, task_id, &task_data).await?;

        let _: () = conn.hset(&task_key, "status", "processing").await?;
        let _: () = conn.hset(&task_key, "llm_req_id", &llm_req_id).await?;

        Command::new("/home/jnovoas/.local/bin/soma-worker")
            .arg(task_id)
            .arg(&llm_req_id)
            .spawn()?;

        Ok(())
    }

    async fn save_snapshot(&self, conn: &mut redis::aio::MultiplexedConnection) -> Result<()> {
        // Asegurar que el directorio existe
        if let Some(parent) = Path::new(&self.snapshot_path).parent() {
            fs::create_dir_all(parent).await?;
        }

        // Sincronizar ticks de Redis -> Lattice antes de salvar
        let _tick_str: String = conn
            .get("swarm:crystal:tick")
            .await
            .unwrap_or_else(|_| "0".to_string());
        // self.lattice.buffer.clock.ticks = tick_str.parse().unwrap_or(0); // Orchestrator is &self here

        // LiquidLattice::save usa ResonantBuffer::save_snapshot que consolida TODO (lattice + meta)
        let res = {
            let lattice = self.lattice.lock().await;
            lattice.save(self.snapshot_path.clone())
        };
        res.map_err(|e| anyhow::anyhow!("{}", e))?;

        info!(
            "💾 Unified Crystal Snapshot guardado en {}",
            self.snapshot_path
        );
        Ok(())
    }

    async fn load_snapshot(&mut self, conn: &mut redis::aio::MultiplexedConnection) -> Result<()> {
        if !Path::new(&self.snapshot_path).exists() {
            return Ok(());
        }

        {
            let mut lattice = self.lattice.lock().await;
            lattice
                .load(self.snapshot_path.clone())
                .map_err(|e| anyhow::anyhow!("{}", e))?;
        }

        // Restaurar estado en Redis para otros agentes
        let (phase, ticks) = {
            let lattice = self.lattice.lock().await;
            (lattice.buffer.phase.clone(), lattice.buffer.clock.ticks)
        };

        let _: () = conn.set("swarm:crystal:phase", &phase).await?;
        let _: () = conn
            .set(
                "swarm:crystal:coherence",
                "600", // Default initialization
            )
            .await?;
        let _: () = conn.set("swarm:crystal:tick", ticks).await?;

        info!(
            "📂 Unified Crystal Snapshot cargado (Phase: {}, Ticks: {})",
            phase, ticks
        );
        Ok(())
    }

    async fn run(mut self) -> Result<()> {
        let mut conn = self.redis_client.get_multiplexed_async_connection().await?;
        info!("🧠 SOMA Orchestrator Rust Online (Quantum Core Integrated).");

        if let Err(e) = self.load_snapshot(&mut conn).await {
            error!("Error cargando snapshot: {}", e);
        }

        let mut ticks = 0;
        loop {
            let (phase, coherence) = self.get_system_state(&mut conn).await?;

            if phase == "VAV" && coherence >= UMBRAL_DISPATCH {
                let tasks: Vec<String> = conn.zrevrange("swarm:tasks:queue", 0, 0).await?;
                if let Some(task_id) = tasks.first() {
                    let lock_key = format!("swarm:lock:{}", task_id);
                    let locked: bool = redis::cmd("SET")
                        .arg(&lock_key)
                        .arg("soma-rs")
                        .arg("NX")
                        .arg("EX")
                        .arg(30)
                        .query_async(&mut conn)
                        .await
                        .unwrap_or(false);

                    if locked {
                        let _: () = conn.zrem("swarm:tasks:queue", task_id).await?;
                        if let Err(e) = self.dispatch_task(&mut conn, task_id).await {
                            error!("Error despachando {}: {}", task_id, e);
                        }
                    }
                }
            }

            ticks += 1;
            if ticks >= SNAPSHOT_INTERVAL_TICKS {
                if let Err(e) = self.save_snapshot(&mut conn).await {
                    error!("Error guardando snapshot: {}", e);
                }
                ticks = 0;
            }

            tokio::time::sleep(Duration::from_millis(BASE_TICK_MS)).await;
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt::init();
    let orch = Orchestrator::new().await?;
    orch.run().await
}
