use axum::{
    body::Body,
    extract::State,
    http::{header, Request, StatusCode},
    middleware::Next,
    response::{IntoResponse, Response},
};
use jsonwebtoken::{decode, Algorithm, DecodingKey, Validation};
use serde::Deserialize;
use std::{collections::HashSet, sync::Arc, time::SystemTime};
use uuid::Uuid;

const ALLOWED_ROLES: [&str; 3] = ["admin", "member", "viewer"];
const MAX_TOKEN_TTL_SECS: u64 = 600;
const WS_SESSION_COOKIE: &str = "sentinel_session";

#[derive(Clone)]
pub struct AuthConfig {
    key: DecodingKey,
    issuer: String,
    audience: String,
    ws_allowed_origins: HashSet<String>,
}

impl AuthConfig {
    pub fn from_env() -> Result<Self, String> {
        let secret = required_env("SENTINEL_JWT_SECRET")?;
        if secret.len() < 32 {
            return Err("SENTINEL_JWT_SECRET debe tener al menos 32 bytes".into());
        }
        let origins = parse_allowed_origins(&required_env("SENTINEL_WS_ALLOWED_ORIGINS")?)?;
        let mut config = Self::new(
            secret.as_bytes(),
            required_env("SENTINEL_JWT_ISSUER")?,
            required_env("SENTINEL_JWT_AUDIENCE")?,
        )?;
        config.ws_allowed_origins = origins;
        Ok(config)
    }

    pub fn new(secret: &[u8], issuer: String, audience: String) -> Result<Self, String> {
        Self::with_ws_allowed_origins(secret, issuer, audience, HashSet::new())
    }

    fn with_ws_allowed_origins(
        secret: &[u8],
        issuer: String,
        audience: String,
        ws_allowed_origins: HashSet<String>,
    ) -> Result<Self, String> {
        if secret.is_empty() || issuer.is_empty() || audience.is_empty() {
            return Err("La clave, issuer y audience JWT son obligatorios".into());
        }
        Ok(Self {
            key: DecodingKey::from_secret(secret),
            issuer,
            audience,
            ws_allowed_origins,
        })
    }

    fn validation(&self) -> Validation {
        let mut validation = Validation::new(Algorithm::HS256);
        validation.algorithms = vec![Algorithm::HS256];
        validation.set_issuer(&[self.issuer.as_str()]);
        validation.set_audience(&[self.audience.as_str()]);
        validation.required_spec_claims =
            HashSet::from(["exp".to_owned(), "iss".to_owned(), "aud".to_owned()]);
        validation.leeway = 0;
        validation
    }
}

fn required_env(name: &str) -> Result<String, String> {
    std::env::var(name).map_err(|_| format!("Falta la variable obligatoria {name}"))
}

fn parse_allowed_origins(value: &str) -> Result<HashSet<String>, String> {
    let origins: HashSet<String> = value.split(',').map(str::trim).map(str::to_owned).collect();
    if origins.is_empty() || origins.iter().any(|origin| !is_exact_origin(origin)) {
        return Err(
            "SENTINEL_WS_ALLOWED_ORIGINS debe contener orígenes exactos sin wildcard".into(),
        );
    }
    Ok(origins)
}

fn is_exact_origin(origin: &str) -> bool {
    let Some((scheme, host)) = origin.split_once("://") else {
        return false;
    };
    matches!(scheme, "http" | "https")
        && !host.is_empty()
        && host.chars().all(|character| {
            character.is_ascii_alphanumeric() || matches!(character, '.' | '-' | ':' | '[' | ']')
        })
}

#[allow(dead_code)]
#[derive(Clone, Debug, Deserialize)]
pub struct SessionClaims {
    pub sub: Uuid,
    pub tenant_id: Uuid,
    pub role: String,
    pub is_superuser: bool,
    pub iat: u64,
    pub exp: u64,
}

fn decode_session(token: &str, config: &AuthConfig) -> Result<SessionClaims, StatusCode> {
    let claims = decode::<SessionClaims>(token, &config.key, &config.validation())
        .map_err(|_| StatusCode::UNAUTHORIZED)?
        .claims;
    let now = SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .map_err(|_| StatusCode::UNAUTHORIZED)?
        .as_secs();
    if claims.iat > now
        || claims.exp <= claims.iat
        || claims.exp.saturating_sub(claims.iat) > MAX_TOKEN_TTL_SECS
    {
        return Err(StatusCode::UNAUTHORIZED);
    }
    if !ALLOWED_ROLES.contains(&claims.role.as_str()) {
        return Err(StatusCode::FORBIDDEN);
    }
    Ok(claims)
}

pub async fn require_session(
    State(config): State<Arc<AuthConfig>>,
    mut request: Request<Body>,
    next: Next,
) -> Response {
    let token = request
        .headers()
        .get(header::AUTHORIZATION)
        .and_then(|value| value.to_str().ok())
        .and_then(|value| value.strip_prefix("Bearer "));

    let Some(token) = token else {
        return unauthorized();
    };

    let claims = match decode_session(token, &config) {
        Ok(claims) => claims,
        Err(StatusCode::FORBIDDEN) => return StatusCode::FORBIDDEN.into_response(),
        Err(_) => return unauthorized(),
    };
    request.extensions_mut().insert(claims);
    next.run(request).await
}

pub async fn require_ws_session(
    State(config): State<Arc<AuthConfig>>,
    mut request: Request<Body>,
    next: Next,
) -> Response {
    let origin_allowed = request
        .headers()
        .get(header::ORIGIN)
        .and_then(|value| value.to_str().ok())
        .is_some_and(|origin| config.ws_allowed_origins.contains(origin));
    if !origin_allowed {
        return StatusCode::FORBIDDEN.into_response();
    }

    let cookie = request
        .headers()
        .get(header::COOKIE)
        .and_then(|value| value.to_str().ok());
    let mut sessions = cookie
        .into_iter()
        .flat_map(|cookies| cookies.split(';'))
        .filter_map(|cookie| cookie.trim().split_once('='))
        .filter(|(name, _)| *name == WS_SESSION_COOKIE)
        .map(|(_, value)| value.trim());
    let Some(token) = sessions.next().filter(|token| !token.is_empty()) else {
        return unauthorized();
    };
    if sessions.next().is_some() {
        return unauthorized();
    }

    let claims = match decode_session(token, &config) {
        Ok(claims) => claims,
        Err(StatusCode::FORBIDDEN) => return StatusCode::FORBIDDEN.into_response(),
        Err(_) => return unauthorized(),
    };
    request.extensions_mut().insert(claims);
    next.run(request).await
}

pub async fn require_superuser(request: Request<Body>, next: Next) -> Response {
    if request
        .extensions()
        .get::<SessionClaims>()
        .is_some_and(|claims| claims.is_superuser)
    {
        next.run(request).await
    } else {
        StatusCode::FORBIDDEN.into_response()
    }
}

fn unauthorized() -> Response {
    (
        StatusCode::UNAUTHORIZED,
        [(header::WWW_AUTHENTICATE, "Bearer")],
    )
        .into_response()
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::{routing::get, Router};
    use tower::ServiceExt;

    const SECRET: &[u8] = b"test-secret-for-ws-auth";
    const ORIGIN: &str = "https://sentinel.pinguinoseguro.cl";

    fn token(ttl: u64) -> String {
        let iat = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_secs();
        let exp = iat + ttl;
        let claims = serde_json::json!({
            "iss": "sentinel-auth",
            "aud": "sentinel-cortex",
            "sub": Uuid::from_u128(1),
            "tenant_id": Uuid::from_u128(2),
            "role": "member",
            "is_superuser": false,
            "iat": iat,
            "exp": exp
        });
        jsonwebtoken::encode(
            &jsonwebtoken::Header::new(Algorithm::HS256),
            &claims,
            &jsonwebtoken::EncodingKey::from_secret(SECRET),
        )
        .unwrap()
    }

    fn test_app() -> Router {
        let mut config =
            AuthConfig::new(SECRET, "sentinel-auth".into(), "sentinel-cortex".into()).unwrap();
        config.ws_allowed_origins = parse_allowed_origins(ORIGIN).unwrap();
        Router::new()
            .route("/", get(|| async { StatusCode::NO_CONTENT }))
            .route_layer(axum::middleware::from_fn_with_state(
                Arc::new(config),
                require_ws_session,
            ))
    }

    async fn request(origin: Option<&str>, cookie: Option<String>) -> StatusCode {
        let mut request = Request::builder().uri("/");
        if let Some(origin) = origin {
            request = request.header(header::ORIGIN, origin);
        }
        if let Some(cookie) = cookie {
            request = request.header(header::COOKIE, cookie);
        }
        test_app()
            .oneshot(request.body(Body::empty()).unwrap())
            .await
            .unwrap()
            .status()
    }

    #[tokio::test]
    async fn websocket_requires_exact_origin_and_session_cookie() {
        let valid_cookie = format!("{WS_SESSION_COOKIE}={}", token(60));
        assert_eq!(
            request(None, Some(valid_cookie.clone())).await,
            StatusCode::FORBIDDEN
        );
        assert_eq!(
            request(Some("https://evil.example"), Some(valid_cookie.clone())).await,
            StatusCode::FORBIDDEN
        );
        assert_eq!(request(Some(ORIGIN), None).await, StatusCode::UNAUTHORIZED);
        assert_eq!(
            request(Some(ORIGIN), Some(valid_cookie)).await,
            StatusCode::NO_CONTENT
        );
    }

    #[test]
    fn websocket_origin_list_rejects_wildcards_and_malformed_values() {
        assert!(parse_allowed_origins("https://one.example,https://two.example").is_ok());
        assert!(parse_allowed_origins("*").is_err());
        assert!(parse_allowed_origins("https://*.example").is_err());
        assert!(parse_allowed_origins("").is_err());
    }

    #[test]
    fn session_lifetime_is_limited_to_ten_minutes() {
        let config =
            AuthConfig::new(SECRET, "sentinel-auth".into(), "sentinel-cortex".into()).unwrap();
        assert!(decode_session(&token(MAX_TOKEN_TTL_SECS), &config).is_ok());
        assert!(matches!(
            decode_session(&token(MAX_TOKEN_TTL_SECS + 1), &config),
            Err(StatusCode::UNAUTHORIZED)
        ));
    }
}
