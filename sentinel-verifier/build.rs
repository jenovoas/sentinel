#[path = "../scripts/yatra_build_guard.rs"]
mod yatra_build_guard;

fn main() {
    let crate_dir = std::path::PathBuf::from(
        std::env::var_os("CARGO_MANIFEST_DIR").expect("CARGO_MANIFEST_DIR ausente"),
    );
    yatra_build_guard::enforce_workspace(&crate_dir);
}
