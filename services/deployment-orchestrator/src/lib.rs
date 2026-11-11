use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Nonce,
};
use axum::{
    body::Bytes,
    extract::{DefaultBodyLimit, Path, State},
    http::{header, HeaderMap, Method, StatusCode},
    response::{IntoResponse, Response},
    routing::{get, post},
    Json, Router,
};
use base64::{engine::general_purpose::STANDARD, Engine};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::os::unix::fs::{FileTypeExt, MetadataExt, PermissionsExt};
use std::{
    env,
    net::SocketAddr,
    path::{Component, Path as FsPath, PathBuf},
    sync::Arc,
    time::Duration,
};
use tokio::{process::Command, time::timeout};
use tokio_postgres::Client;
use uuid::Uuid;

const MIGRATION: &str = include_str!("../migrations/0001_runner.sql");
pub mod purge;
pub mod storage;
fn safe_operator_path(path: &FsPath) -> bool {
    path.is_absolute()
        && !path
            .components()
            .any(|component| matches!(component, Component::ParentDir | Component::CurDir))
}

fn reject_symlink_components(path: &FsPath) -> Result<(), ()> {
    let mut current = PathBuf::from("/");
    for component in path.components().skip(1) {
        current.push(component);
        match std::fs::symlink_metadata(&current) {
            Ok(metadata) if metadata.file_type().is_symlink() => return Err(()),
            Ok(_) => {}
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(()),
            Err(_) => return Err(()),
        }
    }
    Ok(())
}

fn prepare_terraform_data(root: &FsPath, operation: &str) -> Result<PathBuf, ()> {
    if Uuid::parse_str(operation).is_err() || !safe_operator_path(root) {
        return Err(());
    }
    reject_symlink_components(root)?;
    std::fs::create_dir_all(root).map_err(|_| ())?;
    reject_symlink_components(root)?;
    let metadata = std::fs::symlink_metadata(root).map_err(|_| ())?;
    if !metadata.is_dir()
        || metadata.uid() != unsafe { libc::geteuid() }
        || metadata.mode() & 0o022 != 0
    {
        return Err(());
    }
    std::fs::set_permissions(root, std::fs::Permissions::from_mode(0o700)).map_err(|_| ())?;
    let operation_dir = root.join(operation);
    match std::fs::create_dir(&operation_dir) {
        Ok(()) => (),
        Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => (),
        Err(_) => return Err(()),
    }
    reject_symlink_components(&operation_dir)?;
    let metadata = std::fs::symlink_metadata(&operation_dir).map_err(|_| ())?;
    if !metadata.is_dir()
        || metadata.uid() != unsafe { libc::geteuid() }
        || metadata.mode() & 0o022 != 0
    {
        return Err(());
    }
    std::fs::set_permissions(&operation_dir, std::fs::Permissions::from_mode(0o700))
        .map_err(|_| ())?;
    Ok(operation_dir)
}
fn terraform_command(settings: &Settings, envs: &[(String, String)]) -> Command {
    let mut command = Command::new(&settings.terraform_executable);
    command
        .env_clear()
        .env("PATH", "/usr/bin:/bin")
        .env("HOME", &settings.terraform_data_root)
        .env(
            "DOCKER_HOST",
            format!("unix://{}", settings.docker_socket.display()),
        )
        .envs(envs.iter().map(|(key, value)| (key, value)));
    command
}
const ERROR_CODE: &str = "deployment_precondition_failed";

#[derive(Clone)]
pub struct Settings {
    pub database_url: String,
    pub service_token: String,
    pub state_username: String,
    pub state_password: String,
    pub state_key: [u8; 32],
    pub database_ca_cert: Option<PathBuf>,
    pub bind: SocketAddr,
    pub lease_seconds: i64,
    pub terraform_data_root: PathBuf,
    pub terraform_executable: PathBuf,
    pub docker_socket: PathBuf,
}
fn normalized_database_url(url: &str) -> Result<String, String> {
    let (base, query) = url
        .split_once('?')
        .ok_or_else(|| "database_tls_hostname_verification_required".to_string())?;
    let mut verified_tls = false;
    let mut parameters = Vec::new();
    for parameter in query.split('&') {
        let (name, value) = parameter
            .split_once('=')
            .ok_or_else(|| "invalid_database_url".to_string())?;
        if name == "sslmode" {
            if verified_tls || value != "verify-full" {
                return Err("database_tls_hostname_verification_required".into());
            }
            verified_tls = true;
        } else {
            parameters.push(parameter);
        }
    }
    if !verified_tls {
        return Err("database_tls_hostname_verification_required".into());
    }
    let normalized = if parameters.is_empty() {
        base.to_owned()
    } else {
        format!("{base}?{}", parameters.join("&"))
    };
    normalized
        .parse::<tokio_postgres::Config>()
        .map_err(|_| "invalid_database_url".to_string())?;
    Ok(normalized)
}

impl Settings {
    pub fn from_env() -> Result<Self, String> {
        let required = |name: &str| env::var(name).map_err(|_| format!("missing_{name}"));
        let state_key = STANDARD
            .decode(required("RUNNER_STATE_ENCRYPTION_KEY")?)
            .map_err(|_| "invalid_state_key".to_string())?;
        let state_key: [u8; 32] = state_key
            .try_into()
            .map_err(|_| "invalid_state_key_length".to_string())?;
        let bind: SocketAddr = env::var("RUNNER_BIND")
            .unwrap_or_else(|_| "127.0.0.1:8091".into())
            .parse()
            .map_err(|_| "invalid_bind".to_string())?;
        if bind.port() == 0 || !bind.ip().is_ipv4() || !bind.ip().is_loopback() {
            return Err("invalid_bind_for_local_state_backend".into());
        }
        let lease_seconds = env::var("RUNNER_LEASE_SECONDS")
            .ok()
            .and_then(|v| v.parse().ok())
            .filter(|v| *v >= 30)
            .unwrap_or(120);
        let terraform_executable = PathBuf::from(required("TERRAFORM_EXECUTABLE")?);
        if !safe_operator_path(&terraform_executable)
            || !std::fs::symlink_metadata(&terraform_executable)
                .map(|metadata| {
                    metadata.is_file()
                        && metadata.uid() == unsafe { libc::geteuid() }
                        && metadata.permissions().mode() & 0o022 == 0
                        && metadata.permissions().mode() & 0o111 != 0
                })
                .unwrap_or(false)
        {
            return Err("invalid_terraform_executable".into());
        }
        let terraform_data_root = PathBuf::from(required("RUNNER_TERRAFORM_DATA_DIR")?);
        if !safe_operator_path(&terraform_data_root) {
            return Err("invalid_terraform_data_dir".into());
        }
        let service_token = required("DEPLOYMENT_WEBHOOK_SECRET")?;
        let state_username = required("TF_HTTP_USERNAME")?;
        let state_password = required("TF_HTTP_PASSWORD")?;
        if service_token.is_empty() || state_username.is_empty() || state_password.is_empty() {
            return Err("empty_runner_credential".into());
        }
        let docker_socket = PathBuf::from(required("DEPLOYMENT_DOCKER_SOCKET")?);
        if !safe_operator_path(&docker_socket)
            || !std::fs::symlink_metadata(&docker_socket)
                .map(|metadata| {
                    metadata.file_type().is_socket() && metadata.uid() == unsafe { libc::geteuid() }
                })
                .unwrap_or(false)
        {
            return Err("invalid_local_docker_socket".into());
        }
        let database_ca_cert = match env::var_os("DATABASE_CA_CERT_FILE") {
            Some(path) => {
                let path = PathBuf::from(path);
                let metadata = std::fs::symlink_metadata(&path)
                    .map_err(|_| "invalid_database_ca_cert".to_string())?;
                if !safe_operator_path(&path)
                    || !metadata.is_file()
                    || metadata.uid() != unsafe { libc::geteuid() }
                    || metadata.permissions().mode() & 0o022 != 0
                {
                    return Err("invalid_database_ca_cert".into());
                }
                Some(path)
            }
            None => None,
        };
        Ok(Self {
            database_url: normalized_database_url(&required("DATABASE_URL")?)?,
            service_token,
            state_username,
            state_password,
            state_key,
            bind,
            database_ca_cert,
            lease_seconds,
            terraform_data_root,
            terraform_executable,
            docker_socket,
        })
    }
}

#[derive(Clone)]
pub struct AppState {
    pub settings: Arc<Settings>,
}
#[derive(Debug, Deserialize, Serialize, Clone)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct DeploymentRequest {
    pub request_id: String,
    pub tenant_id: String,
    pub service_id: String,
    pub template: String,
    pub config: Value,
    pub idempotency_key: String,
    pub payload_fingerprint: String,
}
#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct OperationResponse {
    operation_id: String,
    status: String,
    public_url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    error_code: Option<String>,
}

pub fn canonical_json(value: &Value) -> String {
    match value {
        Value::Array(values) => format!(
            "[{}]",
            values
                .iter()
                .map(canonical_json)
                .collect::<Vec<_>>()
                .join(",")
        ),
        Value::Object(values) => {
            let mut sorted: Vec<_> = values.iter().collect();
            sorted.sort_unstable_by(|a, b| a.0.cmp(b.0));
            format!(
                "{{{}}}",
                sorted
                    .into_iter()
                    .map(|(k, v)| format!(
                        "{}:{}",
                        serde_json::to_string(k).unwrap_or_default(),
                        canonical_json(v)
                    ))
                    .collect::<Vec<_>>()
                    .join(",")
            )
        }
        _ => serde_json::to_string(value).unwrap_or_else(|_| "null".into()),
    }
}
pub fn payload_fingerprint(request: &DeploymentRequest) -> String {
    let canonical = serde_json::json!({ "tenantId": &request.tenant_id, "serviceId": &request.service_id, "template": &request.template, "config": &request.config });
    hex::encode(Sha256::digest(canonical_json(&canonical).as_bytes()))
}

pub(crate) async fn connect(settings: &Settings) -> Result<Client, ()> {
    let mut builder = native_tls::TlsConnector::builder();
    if let Some(path) = &settings.database_ca_cert {
        let pem = std::fs::read(path).map_err(|_| ())?;
        builder.add_root_certificate(native_tls::Certificate::from_pem(&pem).map_err(|_| ())?);
    }
    let tls = builder.build().map_err(|_| ())?;
    let tls = postgres_native_tls::MakeTlsConnector::new(tls);
    let (client, connection) = tokio_postgres::connect(&settings.database_url, tls)
        .await
        .map_err(|error| {
            tracing::error!(error = %error, "database connection failed");
        })?;
    tokio::spawn(async move {
        if let Err(error) = connection.await {
            tracing::error!(error = %error, "database connection task failed");
        }
    });
    Ok(client)
}
fn bearer(headers: &HeaderMap, expected: &str) -> bool {
    let Some(value) = headers
        .get(header::AUTHORIZATION)
        .and_then(|v| v.to_str().ok())
    else {
        return false;
    };
    let Some(token) = value.strip_prefix("Bearer ") else {
        return false;
    };
    constant_time_eq(token.as_bytes(), expected.as_bytes())
}
fn constant_time_eq(a: &[u8], b: &[u8]) -> bool {
    let mut diff = a.len() ^ b.len();
    for i in 0..a.len().max(b.len()) {
        diff |= usize::from(a.get(i).copied().unwrap_or(0) ^ b.get(i).copied().unwrap_or(0));
    }
    diff == 0
}
#[allow(clippy::result_large_err)]
fn authorized(headers: &HeaderMap, token: &str) -> Result<(), Box<Response>> {
    if bearer(headers, token) {
        Ok(())
    } else {
        Err(Box::new(StatusCode::UNAUTHORIZED.into_response()))
    }
}
fn valid_id(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 128
        && value
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b"._:-".contains(&b))
}
pub(crate) fn valid_storage_tenant_id(value: &str) -> bool {
    value.len() <= 30
        && value
            .as_bytes()
            .first()
            .is_some_and(|b| b.is_ascii_lowercase() || b.is_ascii_digit())
        && value
            .bytes()
            .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'-')
}
fn can_advance(current: &str, next: &str) -> bool {
    matches!(
        (current, next),
        ("preparing", "deploying" | "blocked" | "failed")
            | ("deploying", "verifying" | "failed")
            | ("verifying", "available" | "failed")
    )
}
async fn submit(
    State(state): State<AppState>,
    headers: HeaderMap,
    payload: Result<Json<DeploymentRequest>, axum::extract::rejection::JsonRejection>,
) -> Response {
    if let Err(response) = authorized(&headers, &state.settings.service_token) {
        return *response;
    }
    let Json(request) = match payload {
        Ok(v) => v,
        Err(_) => return StatusCode::BAD_REQUEST.into_response(),
    };
    if !valid_storage_tenant_id(&request.tenant_id)
        || !valid_id(&request.request_id)
        || !valid_id(&request.service_id)
        || !valid_id(&request.idempotency_key)
        || request.template.is_empty()
        || request.template.len() > 128
        || !valid_normalized_config(&request.config)
    {
        return StatusCode::BAD_REQUEST.into_response();
    }
    let actual = payload_fingerprint(&request);
    if request.payload_fingerprint.len() != 64
        || !constant_time_eq(
            actual.as_bytes(),
            request.payload_fingerprint.to_ascii_lowercase().as_bytes(),
        )
    {
        return (
            StatusCode::CONFLICT,
            Json(serde_json::json!({"error":"payload_fingerprint_mismatch"})),
        )
            .into_response();
    }
    let Ok(mut db) = connect(&state.settings).await else {
        return StatusCode::SERVICE_UNAVAILABLE.into_response();
    };
    let tx = match db.transaction().await {
        Ok(tx) => tx,
        Err(error) => {
            tracing::error!(error = %error, "deployment transaction failed");
            return StatusCode::SERVICE_UNAVAILABLE.into_response();
        }
    };
    if let Err(error) = tx
        .query_one(
            "SELECT pg_advisory_xact_lock(hashtextextended($1,0))",
            &[&request.tenant_id],
        )
        .await
    {
        tracing::error!(error = %error, "tenant idempotency lock failed");
        return StatusCode::SERVICE_UNAVAILABLE.into_response();
    }
    match tx
        .query_one(
            "SELECT EXISTS(SELECT 1 FROM tenant_storage_purges WHERE tenant_id=$1)",
            &[&request.tenant_id],
        )
        .await
    {
        Ok(row) if row.get::<_, bool>(0) => return StatusCode::CONFLICT.into_response(),
        Ok(_) => (),
        Err(error) => {
            tracing::error!(error = %error, "tenant purge gate query failed");
            return StatusCode::SERVICE_UNAVAILABLE.into_response();
        }
    }
    let operation_id = Uuid::new_v4().to_string();
    let config = canonical_json(&request.config);
    let initial_status = if ApprovedTemplate::from_env(&request.template).is_some()
        && ApprovedTemplate::operational_gates_ready()
    {
        "preparing"
    } else {
        "blocked"
    };
    let initial_error = if initial_status == "blocked" {
        Some(ERROR_CODE)
    } else {
        None
    };
    let inserted = tx.query_opt(
        "INSERT INTO deployment_operations(operation_id,tenant_id,request_id,service_id,template,config,idempotency_key,payload_fingerprint,status,error_code) VALUES($1,$2,$3,$4,$5,$6::text::jsonb,$7,$8,$9,$10) ON CONFLICT(tenant_id,idempotency_key) DO NOTHING RETURNING operation_id,status,public_url,error_code",
        &[&operation_id,&request.tenant_id,&request.request_id,&request.service_id,&request.template,&config,&request.idempotency_key,&actual,&initial_status,&initial_error],
    ).await;
    let row = match inserted {
        Ok(Some(row)) => row,
        Ok(None) => match tx
            .query_opt(
                "SELECT operation_id,status,public_url,error_code,payload_fingerprint FROM deployment_operations WHERE tenant_id=$1 AND idempotency_key=$2",
                &[&request.tenant_id, &request.idempotency_key],
            )
            .await
        {
            Ok(Some(row))
                if constant_time_eq(row.get::<_, String>(4).as_bytes(), actual.as_bytes()) =>
            {
                row
            }
            Ok(_) => {
                return (
                    StatusCode::CONFLICT,
                    Json(serde_json::json!({"error":"idempotency_conflict"})),
                )
                    .into_response();
            }
            Err(error) => {
                tracing::error!(error = %error, "idempotent operation lookup failed");
                return StatusCode::SERVICE_UNAVAILABLE.into_response();
            }
        },
        Err(error) if error.code() == Some(&tokio_postgres::error::SqlState::UNIQUE_VIOLATION) => {
            return StatusCode::CONFLICT.into_response();
        }
        Err(error) => {
            tracing::error!(error = %error, "deployment operation insert failed");
            return StatusCode::SERVICE_UNAVAILABLE.into_response();
        }
    };
    let response = OperationResponse {
        operation_id: row.get(0),
        status: row.get(1),
        public_url: row.get(2),
        error_code: row.try_get(3).ok().flatten(),
    };
    if let Err(error) = tx.commit().await {
        tracing::error!(error = %error, "deployment transaction commit failed");
        return StatusCode::SERVICE_UNAVAILABLE.into_response();
    }
    (StatusCode::ACCEPTED, Json(response)).into_response()
}
fn valid_domain(domain: &str) -> bool {
    domain.len() <= 253
        && domain.split('.').count() >= 2
        && domain.split('.').all(|label| {
            !label.is_empty()
                && label.len() <= 63
                && label
                    .as_bytes()
                    .first()
                    .is_some_and(u8::is_ascii_alphanumeric)
                && label
                    .as_bytes()
                    .last()
                    .is_some_and(u8::is_ascii_alphanumeric)
                && label
                    .bytes()
                    .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'-')
        })
}
fn valid_normalized_config(config: &Value) -> bool {
    let Some(fields) = config.as_object() else {
        return false;
    };
    let Some(domain) = fields.get("domain").and_then(Value::as_str) else {
        return false;
    };
    if !valid_domain(domain) {
        return false;
    }
    fields.iter().all(|(key, value)| match key.as_str() {
        "domain" => value.is_string(),
        "users" | "storage" => value.as_u64().is_some_and(|n| n <= 9_007_199_254_740_991),
        "backup" => matches!(value.as_str(), Some("daily" | "weekly")),
        _ => false,
    })
}

async fn get_operation(
    State(state): State<AppState>,
    Path(operation_id): Path<String>,
    headers: HeaderMap,
) -> Response {
    if let Err(response) = authorized(&headers, &state.settings.service_token) {
        return *response;
    }
    let Some(tenant) = headers
        .get("x-tenant-id")
        .and_then(|v| v.to_str().ok())
        .filter(|v| valid_id(v))
    else {
        return StatusCode::BAD_REQUEST.into_response();
    };
    if !valid_id(&operation_id) {
        return StatusCode::NOT_FOUND.into_response();
    }
    let Ok(db) = connect(&state.settings).await else {
        return StatusCode::SERVICE_UNAVAILABLE.into_response();
    };
    match db.query_opt("SELECT operation_id,status,public_url,error_code FROM deployment_operations WHERE tenant_id=$1 AND operation_id=$2", &[&tenant,&operation_id]).await {
        Ok(Some(row)) => Json(OperationResponse { operation_id: row.get(0), status: row.get(1), public_url: row.get(2), error_code: row.try_get(3).ok().flatten() }).into_response(),
        Ok(None) => StatusCode::NOT_FOUND.into_response(),
        Err(_) => StatusCode::SERVICE_UNAVAILABLE.into_response(),
    }
}
fn tenant_scoped_owner(record_tenant: &str, requested_tenant: &str) -> bool {
    constant_time_eq(record_tenant.as_bytes(), requested_tenant.as_bytes())
}

async fn destroy_operation(
    State(state): State<AppState>,
    Path(operation_id): Path<String>,
    headers: HeaderMap,
) -> Response {
    if let Err(response) = authorized(&headers, &state.settings.service_token) {
        return *response;
    }
    let Some(tenant) = headers
        .get("x-tenant-id")
        .and_then(|v| v.to_str().ok())
        .filter(|v| valid_id(v))
    else {
        return StatusCode::BAD_REQUEST.into_response();
    };
    if !valid_id(&operation_id) {
        return StatusCode::NOT_FOUND.into_response();
    }
    let Ok(db) = connect(&state.settings).await else {
        return StatusCode::SERVICE_UNAVAILABLE.into_response();
    };
    let owner = Uuid::new_v4().to_string();
    let row = db.query_opt(
        "UPDATE deployment_operations SET lease_owner=$3,lease_until=now()+($4 * interval '1 second'),updated_at=now() WHERE tenant_id=$1 AND operation_id=$2 AND status IN ('available','failed') AND destroyed_at IS NULL AND (lease_owner IS NULL OR lease_until < now()) RETURNING tenant_id,request_id,service_id,template,config::text",
        &[&tenant,&operation_id,&owner,&state.settings.lease_seconds],
    ).await;
    let row = match row {
        Ok(Some(row)) => row,
        Ok(None) => {
            match db.query_opt("SELECT tenant_id,status,destroyed_at IS NOT NULL FROM deployment_operations WHERE tenant_id=$1 AND operation_id=$2", &[&tenant,&operation_id]).await {
                Ok(Some(row)) if !tenant_scoped_owner(&row.get::<_,String>(0),tenant) => return StatusCode::NOT_FOUND.into_response(),
                Ok(Some(row)) if row.get::<_,bool>(2) => return StatusCode::NO_CONTENT.into_response(),
                Ok(Some(_)) => return StatusCode::CONFLICT.into_response(),
                Ok(None) => return StatusCode::NOT_FOUND.into_response(),
                Err(_) => return StatusCode::SERVICE_UNAVAILABLE.into_response(),
            }
        }
        Err(_) => return StatusCode::SERVICE_UNAVAILABLE.into_response(),
    };
    let op_row = (
        row.get::<_, String>(0),
        row.get::<_, String>(1),
        row.get::<_, String>(3),
        row.get::<_, String>(4),
        row.get::<_, String>(2),
    );
    let has_state: bool = match db
        .query_one(
            "SELECT EXISTS(SELECT 1 FROM terraform_states WHERE state_key=$1)",
            &[&operation_id],
        )
        .await
    {
        Ok(row) => row.get(0),
        Err(_) => return StatusCode::SERVICE_UNAVAILABLE.into_response(),
    };
    if !has_state {
        return match db.execute("UPDATE deployment_operations SET destroyed_at=now(),public_url=NULL,lease_owner=NULL,lease_until=NULL,updated_at=now() WHERE tenant_id=$1 AND operation_id=$2 AND lease_owner=$3 AND destroyed_at IS NULL", &[&tenant,&operation_id,&owner]).await {
            Ok(1) => StatusCode::NO_CONTENT.into_response(), _ => StatusCode::SERVICE_UNAVAILABLE.into_response(),
        };
    }
    let Some(spec) = ApprovedTemplate::from_env(&op_row.2) else {
        let _ = db.execute("UPDATE deployment_operations SET lease_owner=NULL,lease_until=NULL WHERE operation_id=$1 AND lease_owner=$2", &[&operation_id,&owner]).await;
        return StatusCode::SERVICE_UNAVAILABLE.into_response();
    };
    let preflight = match storage::ensure_tenant_storage(
        tenant,
        spec.disk_limit_bytes,
        spec.min_host_free_bytes,
    ) {
        Ok(value) => value,
        Err(_) => {
            let _ = db.execute("UPDATE deployment_operations SET lease_owner=NULL,lease_until=NULL WHERE operation_id=$1 AND lease_owner=$2", &[&operation_id,&owner]).await;
            return StatusCode::SERVICE_UNAVAILABLE.into_response();
        }
    };
    let Ok(envs) = terraform_envs(&state.settings, &operation_id, &op_row, &spec, &preflight)
    else {
        let _ = db.execute("UPDATE deployment_operations SET lease_owner=NULL,lease_until=NULL WHERE operation_id=$1 AND lease_owner=$2", &[&operation_id,&owner]).await;
        return StatusCode::SERVICE_UNAVAILABLE.into_response();
    };
    let (stop, halt) = tokio::sync::oneshot::channel();
    let heartbeat = tokio::spawn(renew_lease(
        state.settings.clone(),
        operation_id.clone(),
        owner.clone(),
        state.settings.lease_seconds,
        halt,
    ));
    let workdir = concat!(env!("CARGO_MANIFEST_DIR"), "/terraform/tenant-compute");
    let init = timeout(
        Duration::from_secs(90),
        terraform_command(&state.settings, &envs)
            .kill_on_drop(true)
            .current_dir(workdir)
            .arg("init")
            .arg("-input=false")
            .arg("-reconfigure")
            .output(),
    )
    .await;
    let result = match init {
        Ok(Ok(out)) if out.status.success() => timeout(
            Duration::from_secs(900),
            terraform_command(&state.settings, &envs)
                .kill_on_drop(true)
                .current_dir(workdir)
                .arg("destroy")
                .arg("-input=false")
                .arg("-auto-approve")
                .arg("-lock=true")
                .output(),
        )
        .await
        .map(|r| r.map(|o| o.status.success()))
        .unwrap_or(Ok(false)),
        _ => Ok(false),
    };
    let _ = stop.send(());
    let _ = heartbeat.await;
    if matches!(result, Ok(true)) {
        match db.execute("UPDATE deployment_operations SET destroyed_at=now(),public_url=NULL,lease_owner=NULL,lease_until=NULL,updated_at=now() WHERE tenant_id=$1 AND operation_id=$2 AND lease_owner=$3 AND status IN ('available','failed') AND destroyed_at IS NULL", &[&tenant,&operation_id,&owner]).await {
            Ok(1) => StatusCode::NO_CONTENT.into_response(),
            _ => StatusCode::SERVICE_UNAVAILABLE.into_response(),
        }
    } else {
        let _ = db.execute("UPDATE deployment_operations SET lease_owner=NULL,lease_until=NULL,updated_at=now() WHERE tenant_id=$1 AND operation_id=$2 AND lease_owner=$3", &[&tenant,&operation_id,&owner]).await;
        StatusCode::SERVICE_UNAVAILABLE.into_response()
    }
}

fn state_auth(headers: &HeaderMap, settings: &Settings) -> bool {
    let Some(value) = headers
        .get(header::AUTHORIZATION)
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.strip_prefix("Basic "))
    else {
        return false;
    };
    let Ok(raw) = STANDARD.decode(value) else {
        return false;
    };
    let expected = format!("{}:{}", settings.state_username, settings.state_password);
    constant_time_eq(&raw, expected.as_bytes())
}
fn state_path_valid(key: &str) -> bool {
    Uuid::parse_str(key).is_ok()
}
async fn known_state_operation(db: &Client, operation_id: &str) -> Result<bool, ()> {
    let row = db
        .query_one(
            "SELECT EXISTS(SELECT 1 FROM deployment_operations WHERE operation_id=$1)",
            &[&operation_id],
        )
        .await
        .map_err(|_| ())?;
    Ok(row.get(0))
}
fn cipher(settings: &Settings) -> Result<Aes256Gcm, ()> {
    Aes256Gcm::new_from_slice(&settings.state_key).map_err(|_| ())
}
fn encrypt_state(settings: &Settings, key: &str, bytes: &[u8]) -> Result<Vec<u8>, ()> {
    let cipher = cipher(settings)?;
    let nonce_bytes: [u8; 12] = Uuid::new_v4().as_bytes()[..12].try_into().map_err(|_| ())?;
    let nonce = Nonce::from(nonce_bytes);
    let encrypted = cipher
        .encrypt(
            &nonce,
            aes_gcm::aead::Payload {
                msg: bytes,
                aad: key.as_bytes(),
            },
        )
        .map_err(|_| ())?;
    let mut out = nonce_bytes.to_vec();
    out.extend_from_slice(&encrypted);
    Ok(out)
}
fn decrypt_state(settings: &Settings, key: &str, bytes: &[u8]) -> Result<Vec<u8>, ()> {
    if bytes.len() < 28 {
        return Err(());
    }
    let nonce_bytes: [u8; 12] = bytes[..12].try_into().map_err(|_| ())?;
    let nonce = Nonce::from(nonce_bytes);
    cipher(settings)?
        .decrypt(
            &nonce,
            aes_gcm::aead::Payload {
                msg: &bytes[12..],
                aad: key.as_bytes(),
            },
        )
        .map_err(|_| ())
}
fn state_response(status: StatusCode) -> Response {
    status.into_response()
}
async fn state_get(
    State(state): State<AppState>,
    Path(key): Path<String>,
    headers: HeaderMap,
) -> Response {
    if !state_auth(&headers, &state.settings) {
        return state_response(StatusCode::UNAUTHORIZED);
    }
    if !state_path_valid(&key) {
        return state_response(StatusCode::BAD_REQUEST);
    }
    let Ok(db) = connect(&state.settings).await else {
        return state_response(StatusCode::SERVICE_UNAVAILABLE);
    };
    match known_state_operation(&db, &key).await {
        Ok(true) => (),
        Ok(false) => return StatusCode::NOT_FOUND.into_response(),
        Err(_) => return StatusCode::SERVICE_UNAVAILABLE.into_response(),
    }
    match db.query_opt("SELECT ciphertext FROM terraform_states WHERE state_key=$1 AND EXISTS (SELECT 1 FROM deployment_operations WHERE operation_id=$1)", &[&key]).await {
        Ok(Some(row)) => match decrypt_state(&state.settings,&key,&row.get::<_,Vec<u8>>(0)) { Ok(bytes) => ([(header::CONTENT_TYPE,"application/json")],bytes).into_response(), Err(_) => state_response(StatusCode::INTERNAL_SERVER_ERROR) },
        Ok(None) => state_response(StatusCode::NOT_FOUND), Err(_) => state_response(StatusCode::SERVICE_UNAVAILABLE),
    }
}
async fn state_put(
    State(state): State<AppState>,
    Path(key): Path<String>,
    headers: HeaderMap,
    body: Bytes,
) -> Response {
    if !state_auth(&headers, &state.settings) {
        return state_response(StatusCode::UNAUTHORIZED);
    }
    if !state_path_valid(&key) || body.is_empty() || body.len() > 64 * 1024 * 1024 {
        return state_response(StatusCode::BAD_REQUEST);
    }
    let Ok(encrypted) = encrypt_state(&state.settings, &key, &body) else {
        return state_response(StatusCode::INTERNAL_SERVER_ERROR);
    };
    let Ok(db) = connect(&state.settings).await else {
        return state_response(StatusCode::SERVICE_UNAVAILABLE);
    };
    match db.execute("INSERT INTO terraform_states(state_key,ciphertext) SELECT $1,$2 WHERE EXISTS (SELECT 1 FROM deployment_operations WHERE operation_id=$1) AND EXISTS (SELECT 1 FROM terraform_state_locks WHERE state_key=$1) ON CONFLICT(state_key) DO UPDATE SET ciphertext=EXCLUDED.ciphertext,updated_at=now()", &[&key,&encrypted]).await {
        Ok(1) => StatusCode::OK.into_response(), Ok(_) => StatusCode::LOCKED.into_response(), Err(_) => state_response(StatusCode::SERVICE_UNAVAILABLE),
    }
}
async fn lock_state(
    State(state): State<AppState>,
    Path(key): Path<String>,
    headers: HeaderMap,
    method: Method,
    body: Bytes,
) -> Response {
    if method.as_str() != "LOCK" {
        return state_response(StatusCode::METHOD_NOT_ALLOWED);
    }
    if !state_auth(&headers, &state.settings) {
        return state_response(StatusCode::UNAUTHORIZED);
    }
    if !state_path_valid(&key) || body.len() > 16 * 1024 {
        return state_response(StatusCode::BAD_REQUEST);
    }
    let Ok(value) = serde_json::from_slice::<Value>(&body) else {
        return state_response(StatusCode::BAD_REQUEST);
    };
    let Some(lock_id) = value
        .get("ID")
        .and_then(Value::as_str)
        .filter(|v| valid_id(v))
    else {
        return state_response(StatusCode::BAD_REQUEST);
    };
    let Ok(db) = connect(&state.settings).await else {
        return state_response(StatusCode::SERVICE_UNAVAILABLE);
    };
    match known_state_operation(&db, &key).await {
        Ok(true) => (),
        Ok(false) => return StatusCode::NOT_FOUND.into_response(),
        Err(_) => return StatusCode::SERVICE_UNAVAILABLE.into_response(),
    }
    match db.query_opt("INSERT INTO terraform_state_locks(state_key,lock_id,lock_info) SELECT $1,$2,$3::text::jsonb WHERE EXISTS (SELECT 1 FROM deployment_operations WHERE operation_id=$1) ON CONFLICT(state_key) DO NOTHING RETURNING lock_id", &[&key,&lock_id,&String::from_utf8_lossy(&body).to_string()]).await {
        Ok(Some(_)) => (StatusCode::OK,body).into_response(),
        Ok(None) => match db.query_opt("SELECT lock_id,lock_info FROM terraform_state_locks WHERE state_key=$1", &[&key]).await {
            Ok(Some(row)) if row.get::<_,String>(0)==lock_id => (StatusCode::OK,body).into_response(),
            Ok(Some(row)) => (StatusCode::LOCKED, row.get::<_,String>(1)).into_response(),
            _ => state_response(StatusCode::SERVICE_UNAVAILABLE),
        },
        Err(_) => state_response(StatusCode::SERVICE_UNAVAILABLE),
    }
}
async fn unlock_state(
    State(state): State<AppState>,
    Path(key): Path<String>,
    headers: HeaderMap,
    method: Method,
    body: Bytes,
) -> Response {
    if method.as_str() != "UNLOCK" {
        return state_response(StatusCode::METHOD_NOT_ALLOWED);
    }
    if !state_auth(&headers, &state.settings) {
        return state_response(StatusCode::UNAUTHORIZED);
    }
    let Ok(value) = serde_json::from_slice::<Value>(&body) else {
        return state_response(StatusCode::BAD_REQUEST);
    };
    let Some(lock_id) = value
        .get("ID")
        .and_then(Value::as_str)
        .filter(|v| valid_id(v))
    else {
        return state_response(StatusCode::BAD_REQUEST);
    };
    if !state_path_valid(&key) {
        return state_response(StatusCode::BAD_REQUEST);
    }
    let Ok(db) = connect(&state.settings).await else {
        return state_response(StatusCode::SERVICE_UNAVAILABLE);
    };
    match known_state_operation(&db, &key).await {
        Ok(true) => (),
        Ok(false) => return StatusCode::NOT_FOUND.into_response(),
        Err(_) => return StatusCode::SERVICE_UNAVAILABLE.into_response(),
    }
    match db.execute("DELETE FROM terraform_state_locks WHERE state_key=$1 AND lock_id=$2 AND EXISTS (SELECT 1 FROM deployment_operations WHERE operation_id=$1)", &[&key,&lock_id]).await {
        Ok(1) => (StatusCode::OK,body).into_response(), Ok(_) => state_response(StatusCode::CONFLICT), Err(_) => state_response(StatusCode::SERVICE_UNAVAILABLE),
    }
}
async fn state_delete(
    State(state): State<AppState>,
    Path(key): Path<String>,
    headers: HeaderMap,
) -> Response {
    if !state_auth(&headers, &state.settings) {
        return state_response(StatusCode::UNAUTHORIZED);
    }
    if !state_path_valid(&key) {
        return state_response(StatusCode::BAD_REQUEST);
    }
    let Ok(db) = connect(&state.settings).await else {
        return state_response(StatusCode::SERVICE_UNAVAILABLE);
    };
    match known_state_operation(&db, &key).await {
        Ok(true) => (),
        Ok(false) => return StatusCode::NOT_FOUND.into_response(),
        Err(_) => return StatusCode::SERVICE_UNAVAILABLE.into_response(),
    }
    match db.execute("DELETE FROM terraform_states WHERE state_key=$1 AND EXISTS (SELECT 1 FROM deployment_operations WHERE operation_id=$1) AND NOT EXISTS (SELECT 1 FROM terraform_state_locks WHERE state_key=$1)", &[&key]).await {
        Ok(_) => StatusCode::OK.into_response(), Err(_) => state_response(StatusCode::SERVICE_UNAVAILABLE),
    }
}

pub fn router(settings: Settings) -> Router {
    let state = AppState {
        settings: Arc::new(settings),
    };
    let terraform_state = Router::new()
        .route(
            "/terraform/state/{*key}",
            get(state_get)
                .post(state_put)
                .put(state_put)
                .delete(state_delete),
        )
        .layer(DefaultBodyLimit::max(64 * 1024 * 1024));
    Router::new()
        .route("/deployments", post(submit))
        .route("/deployments/{operation_id}", get(get_operation))
        .route(
            "/deployments/{operation_id}/destroy",
            post(destroy_operation),
        )
        .route("/terraform/lock/{*key}", axum::routing::any(lock_state))
        .route("/terraform/unlock/{*key}", axum::routing::any(unlock_state))
        .merge(terraform_state)
        .with_state(state)
}

async fn transition(
    db: &Client,
    operation: &str,
    owner: &str,
    next: &str,
    public_url: Option<&str>,
    error: Option<&str>,
) -> Result<(), ()> {
    let row = db
        .query_opt(
            "SELECT status FROM deployment_operations WHERE operation_id=$1 AND lease_owner=$2",
            &[&operation, &owner],
        )
        .await
        .map_err(|_| ())?;
    let Some(row) = row else {
        return Err(());
    };
    let current: String = row.get(0);
    if !can_advance(&current, next) {
        return Err(());
    }
    let updated = db.execute("UPDATE deployment_operations SET status=$3,public_url=COALESCE($4,public_url),error_code=$5,updated_at=now() WHERE operation_id=$1 AND lease_owner=$2 AND status=$6", &[&operation,&owner,&next,&public_url,&error,&current]).await.map_err(|_| ())?;
    if updated != 1 {
        return Err(());
    }
    Ok(())
}

#[derive(Clone)]
struct ApprovedTemplate {
    image_digest: String,
    disk_limit_bytes: i64,
    min_host_free_bytes: i64,
    cpu_limit: String,
    memory_limit_mb: i64,
    tmpfs_limit_mb: i64,
    volume_paths: Vec<String>,
}
impl ApprovedTemplate {
    fn from_env(template: &str) -> Option<Self> {
        const SUPPORTED_TEMPLATE: &str = "docker-pilot";
        if template != SUPPORTED_TEMPLATE
            || env::var("DEPLOYMENT_EXECUTION_ENABLED").ok()?.as_str() != "true"
            || env::var("DEPLOYMENT_APPROVED_TEMPLATE").ok()?.as_str() != SUPPORTED_TEMPLATE
            || env::var("DEPLOYMENT_IMAGE_METADATA_REVIEWED")
                .ok()?
                .as_str()
                != "true"
        {
            return None;
        }
        let volume_paths: Vec<String> =
            serde_json::from_str(&env::var("DEPLOYMENT_IMAGE_VOLUME_PATHS").ok()?).ok()?;
        let writable_paths: Vec<String> =
            serde_json::from_str(&env::var("DEPLOYMENT_IMAGE_WRITABLE_PATHS").ok()?).ok()?;
        if volume_paths
            .iter()
            .chain(writable_paths.iter())
            .any(|p| !mapped_image_path(p))
        {
            return None;
        }
        let spec = Self {
            image_digest: env::var("DEPLOYMENT_IMAGE_DIGEST").ok()?,
            disk_limit_bytes: env::var("DEPLOYMENT_DISK_LIMIT_BYTES").ok()?.parse().ok()?,
            min_host_free_bytes: env::var("DEPLOYMENT_MIN_HOST_FREE_BYTES")
                .ok()?
                .parse()
                .ok()?,
            cpu_limit: env::var("DEPLOYMENT_CPU_LIMIT").ok()?,
            memory_limit_mb: env::var("DEPLOYMENT_MEMORY_LIMIT_MB").ok()?.parse().ok()?,
            tmpfs_limit_mb: env::var("DEPLOYMENT_TMPFS_LIMIT_MB").ok()?.parse().ok()?,
            volume_paths,
        };
        let digest = spec.image_digest.rsplit_once("@sha256:").map(|(_, v)| v)?;
        if digest.len() != 64
            || !digest.bytes().all(|b| b.is_ascii_hexdigit())
            || spec.disk_limit_bytes <= 0
            || spec.min_host_free_bytes <= 0
            || spec.volume_paths.iter().any(|p| !mapped_volume_path(p))
        {
            return None;
        }
        Some(spec)
    }
    fn operational_gates_ready() -> bool {
        [
            "DEPLOYMENT_PILOT_IDENTITY_AUTHORIZED",
            "DEPLOYMENT_GUACAMOLE_ACL_VERIFIED",
            "DEPLOYMENT_CAPACITY_APPROVED",
        ]
        .iter()
        .all(|name| env::var(name).ok().as_deref() == Some("true"))
    }
}
fn safe_container_path(path: &str) -> bool {
    path.starts_with('/')
        && path.len() > 1
        && !path.contains('\\')
        && path[1..].split('/').all(|part| {
            !part.is_empty()
                && part != "."
                && part != ".."
                && part
                    .bytes()
                    .all(|b| b.is_ascii_alphanumeric() || b"._-".contains(&b))
        })
}
fn mapped_volume_path(path: &str) -> bool {
    path == "/workspace" || path == "/tmp"
}
fn mapped_image_path(path: &str) -> bool {
    safe_container_path(path)
        && ["/workspace", "/tmp"].iter().any(|root| {
            path == *root
                || path
                    .strip_prefix(root)
                    .is_some_and(|rest| rest.starts_with('/'))
        })
}
fn trusted_local_socket(settings: &Settings) -> bool {
    std::fs::symlink_metadata(&settings.docker_socket)
        .map(|metadata| metadata.file_type().is_socket())
        .unwrap_or(false)
}

fn terraform_envs(
    settings: &Settings,
    op: &str,
    row: &(String, String, String, String, String),
    spec: &ApprovedTemplate,
    storage: &crate::storage::StoragePreflight,
) -> Result<Vec<(String, String)>, ()> {
    if !trusted_local_socket(settings) {
        return Err(());
    }
    let (tenant, request, _, _, _) = row;
    let state_key = op.to_string();
    let base = format!("http://127.0.0.1:{}", settings.bind.port());
    let data_dir = prepare_terraform_data(&settings.terraform_data_root, op)?;
    Ok(vec![
        (
            "TF_DATA_DIR".into(),
            data_dir.to_string_lossy().into_owned(),
        ),
        (
            "TF_HTTP_ADDRESS".into(),
            format!("{base}/terraform/state/{state_key}"),
        ),
        (
            "TF_HTTP_LOCK_ADDRESS".into(),
            format!("{base}/terraform/lock/{state_key}"),
        ),
        (
            "TF_HTTP_UNLOCK_ADDRESS".into(),
            format!("{base}/terraform/unlock/{state_key}"),
        ),
        ("TF_HTTP_LOCK_METHOD".into(), "LOCK".into()),
        ("TF_HTTP_UNLOCK_METHOD".into(), "UNLOCK".into()),
        ("TF_HTTP_USERNAME".into(), settings.state_username.clone()),
        ("TF_HTTP_PASSWORD".into(), settings.state_password.clone()),
        ("TF_IN_AUTOMATION".into(), "1".into()),
        ("TF_INPUT".into(), "0".into()),
        ("TF_VAR_tenant_id".into(), tenant.clone()),
        ("TF_VAR_request_id".into(), request.clone()),
        ("TF_VAR_operation_id".into(), op.to_owned()),
        ("TF_VAR_image_digest".into(), spec.image_digest.clone()),
        (
            "TF_VAR_docker_socket_path".into(),
            settings.docker_socket.to_string_lossy().into_owned(),
        ),
        ("TF_VAR_storage_path".into(), storage.mount_path.clone()),
        (
            "TF_VAR_disk_limit_bytes".into(),
            spec.disk_limit_bytes.to_string(),
        ),
        (
            "TF_VAR_min_host_free_bytes".into(),
            spec.min_host_free_bytes.to_string(),
        ),
        ("TF_VAR_cpu_limit".into(), spec.cpu_limit.clone()),
        (
            "TF_VAR_memory_limit_mb".into(),
            spec.memory_limit_mb.to_string(),
        ),
        ("TF_VAR_storage_preflight_verified".into(), "true".into()),
        (
            "TF_VAR_storage_filesystem_bytes".into(),
            storage.filesystem_bytes.to_string(),
        ),
        (
            "TF_VAR_storage_host_free_bytes".into(),
            storage.host_free_bytes.to_string(),
        ),
        (
            "TF_VAR_tmpfs_limit_mb".into(),
            spec.tmpfs_limit_mb.to_string(),
        ),
        ("TF_VAR_pilot_identity_authorized".into(), "true".into()),
        ("TF_VAR_guacamole_acl_verified".into(), "true".into()),
        ("TF_VAR_remote_backend_lock_verified".into(), "true".into()),
        ("TF_VAR_capacity_approved".into(), "true".into()),
    ])
}
fn storage_quota_valid(
    filesystem_bytes: i64,
    host_free_bytes: i64,
    maximum: i64,
    minimum_free: i64,
) -> bool {
    filesystem_bytes > 0 && filesystem_bytes <= maximum && host_free_bytes >= minimum_free
}

async fn terraform_apply(
    db: &Client,
    settings: &Settings,
    op: &str,
    owner: &str,
    row: &(String, String, String, String, String),
) -> Result<(), ()> {
    let (_, _, template, _, _) = row;
    let Some(spec) = ApprovedTemplate::from_env(template) else {
        transition(db, op, owner, "blocked", None, Some(ERROR_CODE)).await?;
        return Ok(());
    };
    if !ApprovedTemplate::operational_gates_ready() {
        transition(db, op, owner, "blocked", None, Some(ERROR_CODE)).await?;
        return Ok(());
    }
    let current: String = db
        .query_one(
            "SELECT status FROM deployment_operations WHERE operation_id=$1 AND lease_owner=$2",
            &[&op, &owner],
        )
        .await
        .map_err(|_| ())?
        .get(0);
    if !["preparing", "deploying", "verifying"].contains(&current.as_str()) {
        return Err(());
    }
    let preflight = match storage::ensure_tenant_storage(
        &row.0,
        spec.disk_limit_bytes,
        spec.min_host_free_bytes,
    ) {
        Ok(value) => value,
        Err(_) => {
            transition(db, op, owner, "failed", None, Some(ERROR_CODE)).await?;
            return Ok(());
        }
    };
    let envs = terraform_envs(settings, op, row, &spec, &preflight)?;
    let workdir = concat!(env!("CARGO_MANIFEST_DIR"), "/terraform/tenant-compute");
    let init = timeout(
        Duration::from_secs(90),
        terraform_command(settings, &envs)
            .kill_on_drop(true)
            .current_dir(workdir)
            .arg("init")
            .arg("-input=false")
            .arg("-reconfigure")
            .output(),
    )
    .await
    .map_err(|_| ())?
    .map_err(|_| ())?;
    if !init.status.success() {
        transition(db, op, owner, "failed", None, Some(ERROR_CODE)).await?;
        return Ok(());
    }
    if current == "preparing" {
        transition(db, op, owner, "deploying", None, None).await?;
    }
    if current != "verifying" {
        let output = timeout(
            Duration::from_secs(900),
            terraform_command(settings, &envs)
                .kill_on_drop(true)
                .current_dir(workdir)
                .arg("apply")
                .arg("-input=false")
                .arg("-auto-approve")
                .arg("-lock=true")
                .output(),
        )
        .await;
        let output = match output {
            Ok(Ok(o)) => o,
            _ => {
                transition(db, op, owner, "failed", None, Some(ERROR_CODE)).await?;
                return Ok(());
            }
        };
        if !output.status.success() {
            transition(db, op, owner, "failed", None, Some(ERROR_CODE)).await?;
            return Ok(());
        }
        if current != "verifying" {
            transition(db, op, owner, "verifying", None, None).await?;
        }
    }
    let verified = timeout(
        Duration::from_secs(30),
        terraform_command(settings, &envs)
            .kill_on_drop(true)
            .current_dir(workdir)
            .arg("output")
            .arg("-json")
            .output(),
    )
    .await;
    let verified = match verified {
        Ok(Ok(o)) if o.status.success() => serde_json::from_slice::<Value>(&o.stdout).ok(),
        _ => None,
    };
    let Some(outputs) = verified else {
        transition(db, op, owner, "failed", None, Some(ERROR_CODE)).await?;
        return Ok(());
    };
    let value = |name: &str| outputs.get(name).and_then(|v| v.get("value"));
    let preflight = value("storage_preflight");
    let verified_storage = preflight
        .and_then(|v| v.get("verified"))
        .and_then(Value::as_bool)
        .unwrap_or(false);
    let filesystem_bytes = preflight
        .and_then(|v| v.get("filesystem_bytes"))
        .and_then(Value::as_i64)
        .unwrap_or_default();
    let host_free_bytes = preflight
        .and_then(|v| v.get("host_free_bytes"))
        .and_then(Value::as_i64)
        .unwrap_or_default();
    let has_resources = ["container_id", "network_id"].iter().all(|name| {
        value(name)
            .and_then(Value::as_str)
            .is_some_and(|s| !s.is_empty())
    });
    if verified_storage
        && storage_quota_valid(
            filesystem_bytes,
            host_free_bytes,
            spec.disk_limit_bytes,
            spec.min_host_free_bytes,
        )
        && has_resources
    {
        transition(db, op, owner, "available", None, None).await?;
    } else {
        transition(db, op, owner, "failed", None, Some(ERROR_CODE)).await?;
    }
    Ok(())
}

async fn claim(
    db: &mut Client,
    lease_seconds: i64,
) -> Result<Option<(String, String, (String, String, String, String, String))>, ()> {
    let owner = Uuid::new_v4().to_string();
    let tx = db.transaction().await.map_err(|_| ())?;
    let row = tx.query_opt("SELECT operation_id,tenant_id,request_id,template,config::text,service_id FROM deployment_operations WHERE status IN ('preparing','deploying','verifying') AND (lease_until IS NULL OR lease_until < now()) ORDER BY created_at LIMIT 1 FOR UPDATE SKIP LOCKED", &[]).await.map_err(|_| ())?;
    let Some(row) = row else {
        tx.commit().await.map_err(|_| ())?;
        return Ok(None);
    };
    let op: String = row.get(0);
    let tenant: String = row.get(1);
    let request: String = row.get(2);
    let template: String = row.get(3);
    let config: String = row.get(4);
    let service: String = row.get(5);
    tx.execute("UPDATE deployment_operations SET lease_owner=$2,lease_until=now()+($3 * interval '1 second'),attempts=attempts+1,updated_at=now() WHERE operation_id=$1", &[&op,&owner,&lease_seconds]).await.map_err(|_| ())?;
    tx.commit().await.map_err(|_| ())?;
    Ok(Some((
        op,
        owner,
        (tenant, request, template, config, service),
    )))
}
async fn renew_lease(
    settings: Arc<Settings>,
    op: String,
    owner: String,
    seconds: i64,
    mut stop: tokio::sync::oneshot::Receiver<()>,
) {
    loop {
        tokio::select! {
            _ = &mut stop => return,
            _ = tokio::time::sleep(Duration::from_secs((seconds / 3).max(10) as u64)) => {
                let Ok(db) = connect(&settings).await else { return; };
                let updated = db.execute("UPDATE deployment_operations SET lease_until=now()+($3 * interval '1 second') WHERE operation_id=$1 AND lease_owner=$2", &[&op,&owner,&seconds]).await;
                if !matches!(updated, Ok(1)) { return; }
            }
        }
    }
}
pub async fn worker(settings: Arc<Settings>) {
    loop {
        match connect(&settings).await {
            Ok(mut db) => match claim(&mut db, settings.lease_seconds).await {
                Ok(Some((op, owner, row))) => {
                    let (stop, halt) = tokio::sync::oneshot::channel();
                    let heartbeat = tokio::spawn(renew_lease(
                        settings.clone(),
                        op.clone(),
                        owner.clone(),
                        settings.lease_seconds,
                        halt,
                    ));
                    let outcome = terraform_apply(&db, &settings, &op, &owner, &row).await;
                    let _ = stop.send(());
                    let _ = heartbeat.await;
                    if outcome.is_err() {
                        let _ =
                            transition(&db, &op, &owner, "failed", None, Some(ERROR_CODE)).await;
                    }
                    let _ = db.execute("UPDATE deployment_operations SET lease_owner=NULL,lease_until=NULL,updated_at=now() WHERE operation_id=$1 AND lease_owner=$2", &[&op,&owner]).await;
                }
                _ => tokio::time::sleep(Duration::from_secs(3)).await,
            },
            Err(_) => tokio::time::sleep(Duration::from_secs(3)).await,
        }
    }
}
pub async fn serve(settings: Settings) -> Result<(), String> {
    let db = connect(&settings)
        .await
        .map_err(|_| "database_unavailable".to_string())?;
    db.batch_execute(MIGRATION)
        .await
        .map_err(|_| "migration_failed".to_string())?;
    let settings = Arc::new(settings);
    tokio::spawn(worker(settings.clone()));
    let listener = tokio::net::TcpListener::bind(settings.bind)
        .await
        .map_err(|_| "bind_failed".to_string())?;
    axum::serve(listener, router((*settings).clone()))
        .await
        .map_err(|_| "server_failed".to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn canonical_json_sorts_nested_objects() {
        let v: Value = serde_json::from_str(r#"{"z":1,"a":{"y":2,"b":3}}"#).unwrap();
        assert_eq!(canonical_json(&v), r#"{"a":{"b":3,"y":2},"z":1}"#);
    }
    #[test]
    fn database_url_requires_verified_tls_and_removes_only_sslmode() {
        assert_eq!(
            normalized_database_url(
                "postgres://runner:secret@127.0.0.1:15432/runner?sslmode=verify-full&application_name=tenant-runner"
            )
            .unwrap(),
            "postgres://runner:secret@127.0.0.1:15432/runner?application_name=tenant-runner"
        );
        assert!(normalized_database_url("postgres://runner:secret@localhost/runner").is_err());
        assert!(normalized_database_url(
            "postgres://runner:secret@localhost/runner?sslmode=disable"
        )
        .is_err());
        assert!(normalized_database_url(
            "postgres://runner:secret@localhost/runner?sslmode=verify-full&sslmode=disable"
        )
        .is_err());
    }

    #[test]
    fn idempotency_digest_is_stable_and_covers_template() {
        let request = DeploymentRequest {
            request_id: "r".into(),
            tenant_id: "t".into(),
            service_id: "s".into(),
            template: "tpl".into(),
            config: serde_json::json!({"domain":"a.test","users":3}),
            idempotency_key: "k".into(),
            payload_fingerprint: String::new(),
        };
        assert_eq!(payload_fingerprint(&request), payload_fingerprint(&request));
        let mut changed = request.clone();
        changed.template = "other".into();
        assert_ne!(payload_fingerprint(&request), payload_fingerprint(&changed));
    }
    #[test]
    fn status_transitions_are_monotonic_and_terminal() {
        assert!(can_advance("preparing", "deploying"));
        assert!(can_advance("deploying", "verifying"));
        assert!(!can_advance("verifying", "preparing"));
        assert!(!can_advance("failed", "available"));
    }
    #[test]
    fn storage_quota_observes_ext4_capacity_bounds() {
        assert!(!storage_quota_valid(0, 2048, 4096, 1024));
        assert!(storage_quota_valid(1, 1024, 4096, 1024));
        assert!(storage_quota_valid(4096, 1024, 4096, 1024));
        assert!(!storage_quota_valid(4097, 1024, 4096, 1024));
        assert!(!storage_quota_valid(4096, 1023, 4096, 1024));
    }
    #[test]
    fn catalog_is_closed_without_explicit_approval() {
        std::env::remove_var("DEPLOYMENT_APPROVED_TEMPLATE");
        std::env::remove_var("DEPLOYMENT_EXECUTION_ENABLED");
        assert!(ApprovedTemplate::from_env("docker-pilot").is_none());
    }
    #[test]
    fn normalized_config_preserves_omission_and_rejects_unmapped_fields() {
        let omitted = serde_json::json!({"domain":"tenant.example"});
        let explicit = serde_json::json!({"domain":"tenant.example","users":1});
        assert!(valid_normalized_config(&omitted));
        assert!(valid_normalized_config(&explicit));
        assert_ne!(canonical_json(&omitted), canonical_json(&explicit));
        assert!(!valid_normalized_config(
            &serde_json::json!({"domain":"tenant.example","arbitrary":{"path":"/etc"}})
        ));
        assert!(!valid_normalized_config(
            &serde_json::json!({"domain":"tenant.example","users":1.5})
        ));
    }
    #[test]
    fn destroy_is_tenant_scoped_and_not_a_path_or_command_input() {
        assert!(tenant_scoped_owner("tenant-a", "tenant-a"));
        assert!(!tenant_scoped_owner("tenant-a", "tenant-b"));
        assert!(mapped_image_path("/workspace/cache"));
        assert!(mapped_image_path("/tmp/runtime"));
        assert!(!mapped_image_path("/var/lib/app"));
        assert!(!mapped_image_path("/workspace/../etc"));
        assert!(!mapped_volume_path("/workspace/cache"));
    }
    #[test]
    fn state_encryption_is_authenticated_to_the_operation_key() {
        let settings = Settings {
            database_url: String::new(),
            database_ca_cert: None,
            service_token: String::new(),
            state_username: String::new(),
            state_password: String::new(),
            state_key: [7; 32],
            bind: "127.0.0.1:0".parse().unwrap(),
            lease_seconds: 120,
            terraform_data_root: PathBuf::from("/unused"),
            terraform_executable: PathBuf::from("/unused"),
            docker_socket: PathBuf::from("/unused"),
        };
        let ciphertext = encrypt_state(&settings, "operation-a", b"state bytes").unwrap();
        assert_eq!(
            decrypt_state(&settings, "operation-a", &ciphertext).unwrap(),
            b"state bytes"
        );
        assert!(decrypt_state(&settings, "operation-b", &ciphertext).is_err());
    }
}
