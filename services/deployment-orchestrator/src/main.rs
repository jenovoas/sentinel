use deployment_orchestrator::{purge::purge_tenant, serve, Settings};

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "deployment_orchestrator=info".into()),
        )
        .json()
        .init();
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.first().map(String::as_str) == Some("purge-tenant") {
        if args.len() != 3
            || args[2]
                != format!(
                    "--confirm-tenant={}",
                    args.get(1).map(String::as_str).unwrap_or_default()
                )
        {
            tracing::error!(
                error_code = "purge_confirmation_required",
                "tenant purge rejected"
            );
            std::process::exit(2);
        }
        let settings = match Settings::from_env() {
            Ok(settings) => settings,
            Err(code) => {
                tracing::error!(error_code = %code, "tenant purge configuration rejected");
                std::process::exit(1);
            }
        };
        match purge_tenant(&args[1], &settings).await {
            Ok(()) => tracing::info!("tenant storage purge completed"),
            Err(code) => {
                tracing::error!(error_code = %code, "tenant storage purge refused or failed");
                std::process::exit(1);
            }
        }
        return;
    }
    if !args.is_empty() {
        tracing::error!(
            error_code = "unknown_command",
            "deployment runner command rejected"
        );
        std::process::exit(2);
    }
    match Settings::from_env() {
        Ok(settings) => {
            if let Err(code) = serve(settings).await {
                tracing::error!(error_code = %code, "deployment runner stopped");
                std::process::exit(1);
            }
        }
        Err(code) => {
            tracing::error!(error_code = %code, "deployment runner configuration rejected");
            std::process::exit(1);
        }
    }
}
