// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/security/telemetry_sanitizer.rs
//! 🛡️ PURE RUST TELEMETRY SANITIZER & PROMPT INJECTION DEFENSE 🛡️
//!
//! Prevents adversarial prompt injection attacks (AIOpsDoom) and telemetry poisoning
//! by validating and sanitizing telemetry data in pure Rust (zero external dependencies).

#[derive(Debug, Clone)]
#[allow(dead_code)]
pub struct SanitizationResult {
    pub is_safe: bool,
    pub blocked_patterns: Vec<String>,
    pub safe_prompt: Option<String>,
    pub original_prompt: String,
}

#[allow(dead_code)]
pub struct TelemetrySanitizer {
    enabled: bool,
    dangerous_keywords: Vec<(&'static str, &'static str)>,
    allowlist_keywords: Vec<&'static str>,
}

impl Default for TelemetrySanitizer {
    fn default() -> Self {
        Self::new(true)
    }
}

#[allow(dead_code)]
impl TelemetrySanitizer {
    pub fn new(enabled: bool) -> Self {
        let dangerous_keywords = vec![
            ("DROP TABLE", "DROP TABLE"),
            ("DROP DATABASE", "DROP DATABASE"),
            ("DELETE FROM", "DELETE FROM"),
            ("TRUNCATE TABLE", "TRUNCATE TABLE"),
            ("INSERT INTO", "INSERT INTO"),
            ("UPDATE ", "UPDATE SET"),
            ("EXEC(", "EXEC()"),
            ("OR '1'='1", "SQL OR injection"),
            ("RM -RF", "rm -rf"),
            ("SHUTDOWN", "shutdown"),
            ("SYSTEMCTL STOP", "systemctl stop"),
            ("SUDO ", "sudo"),
            ("CHMOD 777", "chmod 777"),
            ("EVAL(", "eval()"),
            ("| BASH", "pipe to bash"),
            ("| SH", "pipe to sh"),
            ("WGET HTTP", "wget download"),
            ("CURL HTTP", "curl download"),
            ("../../", "path traversal"),
            ("/ETC/PASSWD", "/etc/passwd access"),
            ("/ETC/SHADOW", "/etc/shadow access"),
            ("__IMPORT__", "__import__()"),
            ("OS.SYSTEM", "os.system()"),
            ("SUBPROCESS.", "subprocess"),
            ("USERADD ", "useradd command"),
        ];

        let allowlist_keywords = vec![
            "HOW TO DROP TABLE",
            "WHAT IS DROP TABLE",
            "EXPLAIN DROP TABLE",
        ];

        Self {
            enabled,
            dangerous_keywords,
            allowlist_keywords,
        }
    }

    /// Sanitize a prompt or telemetry payload before processing in Cortex / LLM
    pub fn sanitize_prompt(&self, prompt: &str) -> SanitizationResult {
        if !self.enabled {
            return SanitizationResult {
                is_safe: true,
                blocked_patterns: vec![],
                safe_prompt: Some(prompt.to_string()),
                original_prompt: prompt.to_string(),
            };
        }

        let trimmed = prompt.trim();
        if trimmed.is_empty() {
            return SanitizationResult {
                is_safe: false,
                blocked_patterns: vec!["empty_prompt".to_string()],
                safe_prompt: None,
                original_prompt: prompt.to_string(),
            };
        }

        if prompt.len() > 10000 {
            return SanitizationResult {
                is_safe: false,
                blocked_patterns: vec!["excessive_length".to_string()],
                safe_prompt: None,
                original_prompt: prompt.chars().take(100).collect(),
            };
        }

        let upper_prompt = prompt.to_uppercase();

        for allow in &self.allowlist_keywords {
            if upper_prompt.contains(allow) {
                return SanitizationResult {
                    is_safe: true,
                    blocked_patterns: vec![],
                    safe_prompt: Some(prompt.to_string()),
                    original_prompt: prompt.to_string(),
                };
            }
        }

        let mut blocked = Vec::new();
        for (pattern, name) in &self.dangerous_keywords {
            if upper_prompt.contains(pattern) {
                blocked.push(name.to_string());
            }
        }

        if !blocked.is_empty() {
            return SanitizationResult {
                is_safe: false,
                blocked_patterns: blocked,
                safe_prompt: None,
                original_prompt: prompt.to_string(),
            };
        }

        SanitizationResult {
            is_safe: true,
            blocked_patterns: vec![],
            safe_prompt: Some(prompt.to_string()),
            original_prompt: prompt.to_string(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sanitizer_blocks_sql_injection() {
        let sanitizer = TelemetrySanitizer::new(true);
        let res = sanitizer.sanitize_prompt("SELECT * FROM users; DROP TABLE users;");
        assert!(!res.is_safe);
        assert!(res.blocked_patterns.contains(&"DROP TABLE".to_string()));
    }

    #[test]
    fn test_sanitizer_blocks_live_truth_claim_patterns() {
        let sanitizer = TelemetrySanitizer::new(true);
        for sample in ["drop database", "rm -rf /", "shutdown now", "systemctl stop nginx"] {
            let res = sanitizer.sanitize_prompt(sample);
            assert!(!res.is_safe, "{sample}");
        }
    }

    #[test]
    fn test_sanitizer_allows_safe_telemetry() {
        let sanitizer = TelemetrySanitizer::new(true);
        let res = sanitizer.sanitize_prompt("Lattice node 42 temperature 23.9C");
        assert!(res.is_safe);
    }
}
