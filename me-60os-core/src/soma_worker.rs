// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! soma_worker.rs — Worker SOMA Rust (SCV Anti-Hallucination Pipeline)
//! -----------------------------------------------------------------------------

use anyhow::Result;
use once_cell::sync::Lazy;
use redis::AsyncCommands;
use regex::Regex;
use std::collections::HashMap;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tracing::{error, info, warn};

// Importar tipos del core
use me60os_core::spa::SPA;

// --- SCV Constants & Regex ---
const BLOCKED_PHRASES: &[&str] = &[
    "no puedo",
    "no tengo acceso",
    "herramienta no encontrada",
    "no disponible en este contexto",
    "no existe",
    "error desconocido",
    "imposible completar",
    "no puedo ejecutar",
    "lo siento, pero no puedo",
    "lo siento, no puedo",
    "no tengo capacidad",
    "no se pudo establecer",
    "sin acceso directo",
];

const ALLOWED_KEYWORDS: &[&str] = &[
    "completado",
    "éxito",
    "verificado",
    "implementado",
    "creado",
    "actualizado",
    "corregido",
    "fix",
    "resultado",
    "score",
    "activo",
    "operativo",
    "corriendo",
    "ok",
];

static GHOST_PATTERNS: Lazy<Vec<(&'static str, Regex)>> = Lazy::new(|| {
    vec![
    ("ghost_ssh_prescription", Regex::new(r"(?i)requiere\s+ssh\s+a\s+\w+\s*:").unwrap()),
    ("ghost_access_prescription", Regex::new(r"(?i)requiere\s+(acceso|conexi[oó]n)\s+a\s+\w+").unwrap()),
    ("ghost_install_prescription", Regex::new(r"(?i)requiere\s+instalar\s+\w+").unwrap()),
    ("ghost_command_only", Regex::new(r"(?im)^(sudo|podman|docker|samba-tool|systemctl|journalctl|kubectl)\s+\S+\s*$").unwrap()),
    ("ghost_instruction", Regex::new(r"(?is)para\s+(completar|ejecutar)\s+esta\s+tarea.{0,30}(deb[eé]|necesitas|hay que)").unwrap()),
    ("ghost_destructive", Regex::new(r"(?i)(drop\s+table|delete\s+from|rm\s+-rf|truncate\s+table)").unwrap()),
]
});

// --- Core Worker App ---
struct WorkerApp {
    conn: redis::aio::MultiplexedConnection,
    task_id: String,
    llm_req_id: String,
}

impl WorkerApp {
    async fn new(task_id: String, llm_req_id: String) -> Result<Self> {
        let redis_host = std::env::var("REDIS_HOST").unwrap_or_else(|_| "localhost".to_string());
        let redis_port = std::env::var("REDIS_PORT").unwrap_or_else(|_| "6379".to_string());
        let redis_url = format!("redis://{}:{}/", redis_host, redis_port);
        let client = redis::Client::open(redis_url)?;
        let conn = client.get_multiplexed_async_connection().await?;
        Ok(Self {
            conn,
            task_id,
            llm_req_id,
        })
    }

    async fn pull_llm_result(&mut self) -> Result<String> {
        let result_key = format!("swarm:llm:result:{}", self.llm_req_id);
        let mut timeout = 300;

        while timeout > 0 {
            let res: HashMap<String, String> = self.conn.hgetall(&result_key).await?;
            if let Some(content) = res.get("content") {
                return Ok(content.clone());
            }
            if let Some(error) = res.get("error") {
                anyhow::bail!("Gateway Error: {}", error);
            }
            tokio::time::sleep(Duration::from_secs(2)).await;
            timeout -= 2;
        }
        anyhow::bail!("Timeout esperando al LLM Gateway")
    }

    // SCV Layer 1: Semántica (Aritmética SPA)
    fn check_semantic(&self, text: &str) -> (SPA, Vec<String>) {
        let mut issues = Vec::new();
        let text_lower = text.to_lowercase();

        let blocked = BLOCKED_PHRASES
            .iter()
            .filter(|&p| text_lower.contains(*p))
            .count() as i64;

        let allowed = ALLOWED_KEYWORDS
            .iter()
            .filter(|&k| text_lower.contains(*k))
            .count() as i64;

        // one = 1.0 = 12,960,000
        let one = SPA::one();

        // allowed_score = (allowed / 3.0).min(1.0) -> (allowed * SCALE_0 / 3).clamp(0, SCALE_0)
        let allowed_score = SPA::from_raw((allowed * SPA::SCALE_0 / 3).min(SPA::SCALE_0));
        
        // blocked_penalty = blocked.min(1.0) -> if >0 SCALE_0 else 0
        let blocked_penalty = if blocked > 0 { one } else { SPA::zero() };

        // Simple entropy (Integer approximation)
        // placeholder entropy logic using SPA
        let entropy_score = SPA::from_raw(SPA::SCALE_0 / 2); // 0.5 center

        // weighted: (1.0 - blocked_penalty)*0.4 + (allowed_score)*0.3 + (entropy)*0.3
        // 0.4 = 40/100, 0.3 = 30/100
        let semantic_score = 
            (one - blocked_penalty) * 40 / 100 + 
            allowed_score * 30 / 100 + 
            entropy_score * 30 / 100;

        if blocked > 0 {
            issues.push(format!("semantic:blocked_phrases({})", blocked));
        }

        (semantic_score, issues)
    }

    // SCV Layer 2: Ghost Execution (SPA 1.0)
    fn check_ghost(&self, text: &str) -> (SPA, Option<String>) {
        for (reason, regex) in GHOST_PATTERNS.iter() {
            if regex.is_match(text) {
                return (SPA::one(), Some(reason.to_string()));
            }
        }
        (SPA::zero(), None)
    }

    // SCV Layer 3: Velocidad (SPA)
    fn check_velocity(
        &self,
        scope: &str,
        started_at: u64,
        completed_at: u64,
    ) -> (SPA, Option<String>) {
        let elapsed = if completed_at > started_at {
            completed_at - started_at
        } else {
            0
        };
        let scope_base = scope.split(':').next().unwrap_or("default");

        let min_time = match scope_base {
            "kingu" => 45,
            "sentinel" => 20,
            "centurion" => 30,
            "llm" => 60,
            "ALL" => 30,
            "fenix" => 10,
            _ => 15,
        };

        if elapsed < 5 {
            return (SPA::one(), Some(format!("velocity_impossible:{}s<5s", elapsed)));
        }
        if elapsed < min_time {
            // half = 0.5 = 6,480,000
            return (
                SPA::from_raw(SPA::SCALE_0 / 2),
                Some(format!("velocity_suspicious:{}s<{}s", elapsed, min_time)),
            );
        }
        (SPA::zero(), None)
    }

    // SCV Layer 4: Ring0 Telemetry (SPA)
    async fn check_ring0(&mut self, _scope: &str) -> (SPA, Option<String>) {
        let cpu_freq: String = self
            .conn
            .get("swarm:system:cpu_freq")
            .await
            .unwrap_or_default();
        let ebpf_active: String = self
            .conn
            .get("swarm:system:ebpf_active")
            .await
            .unwrap_or_default();

        if ebpf_active != "1" {
            return (SPA::zero(), Some("ring0_inactive".to_string()));
        }

        // Comprobar anomalía (reporte sin uso CPU)
        if !cpu_freq.is_empty() {
            let parts: Vec<&str> = cpu_freq.split(',').collect();
            if parts.len() >= 2 {
                let d: u64 = parts[0].parse().unwrap_or(0);
                let m: u64 = parts[1].parse().unwrap_or(0);
                let cpu_val_x60 = d * 60 + m;

                if cpu_val_x60 < 2 {
                    // 0.1 penalty = 1,296,000
                    return (SPA::from_raw(SPA::SCALE_0 / 10), Some("stress_anomaly:low_cpu".to_string()));
                }
            }
        }

        (SPA::zero(), None)
    }

    async fn run(mut self) -> Result<()> {
        let task_key = format!("swarm:task:{}", self.task_id);
        let task_data: HashMap<String, String> = self.conn.hgetall(&task_key).await?;

        if task_data.is_empty() {
            anyhow::bail!("Tarea {} no encontrada en Redis", self.task_id);
        }

        // 1. Obtener resultado del LLM (esperando a Queue)
        let llm_content = match self.pull_llm_result().await {
            Ok(content) => content,
            Err(e) => {
                error!("❌ Falla obteniendo resultado LLM: {}", e);
                let _: () = self.conn.hset(&task_key, "status", "failed").await?;
                return Ok(());
            }
        };

        // 2. Extraer metadatos para SCV
        let scope = task_data
            .get("scope")
            .cloned()
            .unwrap_or_else(|| "local".to_string());
        let agent = task_data
            .get("agent")
            .cloned()
            .unwrap_or_else(|| "soma_worker".to_string());
        let started_at: u64 = task_data
            .get("started_at")
            .unwrap_or(&"0".to_string())
            .parse()
            .unwrap_or(0);
        let completed_at = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();

        // 3. Ejecutar Pipeline SCV Nativo
        let mut issues = Vec::new();
        let (semantic_score, mut sem_issues) = self.check_semantic(&llm_content);
        issues.append(&mut sem_issues);

        let (ghost_pen, ghost_reason) = self.check_ghost(&llm_content);
        if let Some(r) = ghost_reason {
            issues.push(format!("ghost:{}", r));
        }

        let (vel_pen, vel_reason) = self.check_velocity(&scope, started_at, completed_at);
        if let Some(r) = vel_reason {
            issues.push(format!("velocity:{}", r));
        }

        let (ring0_pen, ring0_reason) = self.check_ring0(&scope).await;
        if let Some(r) = ring0_reason {
            issues.push(format!("ring0:{}", r));
        }

        // Métrica final de Coherencia (Aritmética SPA)
        let one = SPA::one();
        let is_ghost = ghost_pen.to_raw() > 0;
        let coherence = 
            (semantic_score * 25 / 100) +
            (one - ghost_pen) * 40 / 100 +
            (one - vel_pen) * 20 / 100 +
            (one - ring0_pen) * 15 / 100;

        let base_score: i64 = 20;
        let mut final_score = base_score;
        let mut report_prefix = String::new();

        if is_ghost {
            warn!("SCV: GHOST EXECUTION detectado en {}", self.task_id);
            final_score = 0;
            report_prefix = "[SCV:GHOST] ".to_string();
        } else if vel_pen.to_raw() > 0 {
            warn!("SCV: VELOCITY ANOMALY en {}", self.task_id);
            final_score = base_score * 20 / 100;
            report_prefix = "[SCV:VELOCITY] ".to_string();
        }

        let full_report = format!("{}{}", report_prefix, llm_content);

        // 4. Actualizar Estado Global en Redis
        let mut pipe = redis::pipe();
        pipe.srem("swarm:tasks:running", &self.task_id)
            .zadd("swarm:tasks:done", &self.task_id, completed_at)
            .zincr("swarm:scores", &agent, final_score)
            .hincr("swarm:tasks_count", &agent, 1)
            .hset(&task_key, "status", "completed")
            .hset(&task_key, "completed_at", completed_at)
            .hset(&task_key, "score", final_score)
            .hset(&task_key, "report", &full_report)
            .del(format!("swarm:lock:{}", self.task_id));

        let _: () = pipe.query_async(&mut self.conn).await?;

        if is_ghost || vel_pen.to_raw() > 0 {
            let _: () = self.conn.zincr("swarm:agent_incidents", &agent, 1).await?;
        }

        info!(
            "✅ Tarea {} completada. Score asignado: {} (Coh: {})",
            self.task_id, final_score, coherence
        );
        if !issues.is_empty() {
            warn!("   SCV Issues: {:?}", issues);
        }

        Ok(())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt::init();
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 {
        anyhow::bail!("Uso: soma-worker <task_id> <llm_req_id>");
    }

    let task_id = args[1].clone();
    let llm_req_id = args[2].clone();

    info!(
        "👷 SOMA Worker (Rust SCV Pipeline) activo (Tarea: {}, Req: {})",
        task_id, llm_req_id
    );

    let worker = WorkerApp::new(task_id, llm_req_id).await?;
    worker.run().await
}
