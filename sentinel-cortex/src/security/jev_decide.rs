// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
//! Cliente mínimo Jev (TypeSafe AI): decisión tipada barata para SUSPECT.
//! Sin LFM local, sin GPU, sin texto generado. Solo decide:
//! ALLOW (ejecutar), DENY (bloquear), ESCALATE (elevar a cortex).
//! $0.042/1M tokens input, output gratis, ~0.4s por decisión.

use serde::{Deserialize, Serialize};

/// Decisión consensuada eBPF→gateway→cortex.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum JevVerdict {
    /// Ejecutar: el evento es benigno con alta probabilidad.
    Allow,
    /// Bloquear: el evento es malicioso con alta probabilidad.
    Deny,
    /// Elevar: incertidumbre; el cortex decide por coherencia/portal.
    Escalate,
}

/// Pregunta tipada a Jev. Sin texto libre: solo hechos del evento eBPF.
#[derive(Debug, Clone, Serialize)]
pub struct JevQuery {
    pub event_type: String,
    pub process_path_hash: String,
    pub uid: u32,
    pub severity: u8,
    pub entropy_s60_raw: u64,
    pub guardian_code: u8,
}

/// Respuesta Jev: veredicto + probabilidad 0-1000 (milésimas, S60-friendly).
#[derive(Debug, Clone, Deserialize)]
pub struct JevAnswer {
    pub verdict: JevVerdict,
    pub confidence_mille: u16,
}

/// Cliente mínimo: POST JSON, timeout 2s, sin reintentos agresivos.
/// Si Jev no responde: ESCALATE (el cortex decide; nunca bloquear a ciegas).
pub async fn ask_jev(
    client: &reqwest::Client,
    endpoint: &str,
    api_key: &str,
    query: &JevQuery,
) -> JevAnswer {
    let fallback = JevAnswer {
        verdict: JevVerdict::Escalate,
        confidence_mille: 0,
    };
    let fut = client
        .post(endpoint)
        .header("Authorization", format!("Bearer {api_key}"))
        .json(query)
        .send();
    let resp = match tokio::time::timeout(std::time::Duration::from_secs(2), fut).await {
        Ok(Ok(r)) => r,
        _ => return fallback,
    };
    resp.json::<JevAnswer>().await.unwrap_or(fallback)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fallback_is_escalate() {
        // Sin red no hay decisión: el cortex dispone, no se bloquea a ciegas.
        let rt = tokio::runtime::Runtime::new().unwrap();
        let ans = rt.block_on(ask_jev(
            &reqwest::Client::new(),
            "http://127.0.0.1:9/nope",
            "x",
            &JevQuery {
                event_type: "EXEC_ALLOWED".into(),
                process_path_hash: "abc".into(),
                uid: 1000,
                severity: 1,
                entropy_s60_raw: 25920000,
                guardian_code: 1,
            },
        ));
        assert_eq!(ans.verdict, JevVerdict::Escalate);
    }
}
