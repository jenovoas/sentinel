// src/quantum/semantic_shell.rs
//! Semantic Shell - Interactive REPL for Sentinel
//!
//! Provides the "Human in the Loop" interface for:
//! 1. Teaching (Oracle Mode)
//! 2. System Control (Action Mode)
//! 3. Safety Verification

use std::io::{self, Write};
use std::process::Command; // Assuming a coloring crate or basic ANSI codes if not present
                           // Use standard ANSI codes to avoid extra dependencies if 'colored' isn't in Cargo.toml
                           // Based on Cargo.toml, 'colored' is NOT listed. I will use raw ANSI codes.

use crate::quantum::semantic_router::{Intent, SemanticRouter};
use tokio::runtime::Builder;

pub struct SemanticShell {
    router: SemanticRouter,
    runtime: tokio::runtime::Runtime,
}

impl SemanticShell {
    pub fn new() -> Self {
        let runtime = Builder::new_current_thread()
            .enable_all()
            .build()
            .expect("Failed to create Tokio runtime for Shell");

        Self {
            router: SemanticRouter::new(),
            runtime,
        }
    }

    pub fn run(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        self.print_banner();

        loop {
            print!("\n\x1b[1;32mOperador > \x1b[0m");
            io::stdout().flush()?;

            let mut input = String::new();
            io::stdin().read_line(&mut input)?;
            let input = input.trim();

            if input.is_empty() {
                continue;
            }

            if input.eq_ignore_ascii_case("exit") || input.eq_ignore_ascii_case("q") {
                println!("\n\x1b[1;35m🔌 Desconectando enlace neural...\x1b[0m");
                break;
            }

            self.process_command(input);
        }

        Ok(())
    }

    fn process_command(&mut self, input: &str) {
        print!("\x1b[1;30mThinking...\x1b[0m\r");
        io::stdout().flush().unwrap();

        // Call async router from sync context
        let (intent, reason) = self.runtime.block_on(self.router.classify(input));

        // Clear "Thinking..."
        print!("             \r");

        match intent {
            Intent::Oracle => {
                println!("\n\x1b[1;36m🔮 ORACLE MODE INVOKED\x1b[0m");
                println!("   \x1b[3m{}\x1b[0m", reason);
                // For v1 Rust, we still call the python script for the actual matrix viz
                // untill we port the visualization to Rust.
                if let Err(e) = Command::new("python3")
                    .arg("quantum/quantum_oracle_cli.py")
                    .arg(input)
                    .spawn()
                    .and_then(|mut child| child.wait())
                {
                    println!("   Failed to launch Python Oracle: {}", e);
                }
            }
            Intent::SystemAction => {
                println!("\n\x1b[1;33m⚙️ SYSTEM ACTION\x1b[0m");
                println!("   Intent: {}", reason);
                // Heuristic mapping for actions (can be expanded)
                if input.to_lowercase().contains("dashboard") {
                    println!("   Launching Dashboard...");
                    // Placeholder for action dispatch
                } else {
                    println!("   Action approved but implementation pending in Rust migration.");
                }
            }
            Intent::SafetyCheck => {
                println!("\n\x1b[1;31m🛡️ SAFETY GUARD\x1b[0m");
                println!("   Analysis: {}", reason);
            }
            Intent::Unknown => {
                println!("\n\x1b[1;30m❓ UNKNOWN INTENT\x1b[0m");
                println!("   System reasoning: {}", reason);
            }
        }
    }

    fn print_banner(&self) {
        println!("\x1b[1;35m============================================================\x1b[0m");
        println!("\x1b[1;35m  🧠  SENTINEL SEMANTIC SHELL v2.0 (RUST NATIVE)  🧠\x1b[0m");
        println!("\x1b[1;35m  [MODO MAESTRO / LENGUAJE NATURAL ACTIVADO]\x1b[0m");
        println!("\x1b[1;35m============================================================\x1b[0m");
        println!("Escribe 'exit' o 'q' para volver al CLI Modular.");
    }
}
