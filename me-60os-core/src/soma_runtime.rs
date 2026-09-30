//! Runtime configuration shared by the SOMA orchestrator and worker.

use std::env;

const DEFAULT_REDIS_HOST: &str = "127.0.0.1";
const DEFAULT_REDIS_PORT: &str = "6379";
const DEFAULT_REDIS_DB: &str = "0";
const DEFAULT_SNAPSHOT_PATH: &str = "/var/lib/sentinel/soma/crystal_snapshot.json";
const DEFAULT_MEMORY_PATH: &str = "/var/lib/sentinel/soma/MEMORY.md";
const DEFAULT_WORKER_BINARY: &str = "soma-worker";

/// Returns the configured Redis URL, or builds one from split environment variables.
/// `REDIS_PASSWORD` is percent-encoded before it is inserted into the URL.
pub fn redis_url() -> String {
    if let Ok(url) = env::var("REDIS_URL") {
        if !url.trim().is_empty() {
            return url;
        }
    }

    let host = env::var("REDIS_HOST").unwrap_or_else(|_| DEFAULT_REDIS_HOST.to_string());
    let port = env::var("REDIS_PORT").unwrap_or_else(|_| DEFAULT_REDIS_PORT.to_string());
    let db = env::var("REDIS_DB").unwrap_or_else(|_| DEFAULT_REDIS_DB.to_string());
    let password = env::var("REDIS_PASSWORD").ok();

    build_redis_url(&host, &port, &db, password.as_deref())
}

fn build_redis_url(host: &str, port: &str, db: &str, password: Option<&str>) -> String {
    match password.filter(|value| !value.is_empty()) {
        Some(password) => format!(
            "redis://:{}@{}:{}/{}",
            encode_url_component(password),
            host,
            port,
            db
        ),
        None => format!("redis://{}:{}/{}", host, port, db),
    }
}

fn encode_url_component(value: &str) -> String {
    let mut encoded = String::with_capacity(value.len());
    for byte in value.bytes() {
        if byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'.' | b'_' | b'~') {
            encoded.push(byte as char);
        } else {
            encoded.push('%');
            encoded.push(char::from_digit((byte >> 4) as u32, 16).unwrap().to_ascii_uppercase());
            encoded.push(char::from_digit((byte & 0x0f) as u32, 16).unwrap().to_ascii_uppercase());
        }
    }
    encoded
}

pub fn snapshot_path() -> String {
    env::var("SOMA_SNAPSHOT_PATH").unwrap_or_else(|_| DEFAULT_SNAPSHOT_PATH.to_string())
}

pub fn memory_path() -> String {
    env::var("SOMA_MEMORY_PATH").unwrap_or_else(|_| DEFAULT_MEMORY_PATH.to_string())
}

pub fn worker_binary() -> String {
    env::var("SOMA_WORKER_BIN").unwrap_or_else(|_| DEFAULT_WORKER_BINARY.to_string())
}

#[cfg(test)]
mod tests {
    use super::build_redis_url;

    #[test]
    fn builds_authenticated_url_with_encoded_password() {
        assert_eq!(
            build_redis_url("localhost", "6379", "2", Some("p@ss word")),
            "redis://:p%40ss%20word@localhost:6379/2"
        );
    }

    #[test]
    fn builds_unauthenticated_url_without_password_marker() {
        assert_eq!(
            build_redis_url("127.0.0.1", "6379", "0", None),
            "redis://127.0.0.1:6379/0"
        );
    }
}
