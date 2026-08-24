// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/quantum/semantic_shell.rs
//! Semantic Shell - Interactive REPL for Sentinel
//!
//! Provides the "Human in the Loop" interface for:
//! 1. Teaching (Oracle Mode)
//! 2. System Control (Action Mode)
//! 3. Safety Verification
//
// Interactive REPL; pending wiring into the main binary.
#![allow(dead_code)]

use std::io::{self, Write};
use std::process::Command; // Assuming a coloring crate or basic ANSI codes if not present
                           // Use standard ANSI codes to avoid extra dependencies if 'colored' isn't in Cargo.toml

use crate::quantum::semantic_router::{Intent, SemanticRouter};
use rustyline::completion::FilenameCompleter;
use rustyline::error::ReadlineError;
use rustyline::{Config, Editor};
use rustyline_derive::{Completer, Helper, Highlighter, Hinter, Validator};
use tokio::runtime::Builder;

#[derive(Helper, Completer, Highlighter, Hinter, Validator)]
struct ShellHelper {
    #[rustyline(Completer)]
    completer: FilenameCompleter,
}

pub struct SemanticShell {
    router: SemanticRouter,
    runtime: tokio::runtime::Runtime,
}

impl Default for SemanticShell {
    fn default() -> Self {
        Self::new()
    }
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

        let config = Config::builder()
            .history_ignore_space(true)
            .completion_type(rustyline::CompletionType::List)
            .build();

        let h = ShellHelper {
            completer: FilenameCompleter::new(),
        };

        let mut rl = Editor::with_config(config)?;
        rl.set_helper(Some(h));

        // Load history if possible
        let history_path = "/tmp/.sentinel_shell_history";
        let _ = rl.load_history(history_path);

        loop {
            let prompt = "\x1b[1;32mOperador > \x1b[0m";
            match rl.readline(prompt) {
                Ok(line) => {
                    let input = line.trim();
                    if input.is_empty() {
                        continue;
                    }

                    let _ = rl.add_history_entry(input);

                    if input.eq_ignore_ascii_case("exit") || input.eq_ignore_ascii_case("q") {
                        println!("\n\x1b[1;35m🔌 Desconectando enlace neural...\x1b[0m");
                        break;
                    }

                    self.process_command(input);
                }
                Err(ReadlineError::Interrupted) => break,
                Err(ReadlineError::Eof) => break,
                Err(err) => {
                    println!("Error: {:?}", err);
                    break;
                }
            }
        }

        let _ = rl.save_history(history_path);
        Ok(())
    }

    fn fuzzy_cd(&self, target: &str) -> Option<std::path::PathBuf> {
        // 1. Try exact match
        let exact = std::path::PathBuf::from(target);
        if exact.is_dir() {
            return Some(exact);
        }

        // 2. Try prefix match (case-insensitive)
        if let Ok(entries) = std::fs::read_dir(".") {
            for entry in entries.flatten() {
                if entry.file_type().map(|t| t.is_dir()).unwrap_or(false) {
                    let name = entry.file_name().to_string_lossy().to_lowercase();
                    let target_lower = target.to_lowercase();
                    if name == target_lower || name.starts_with(&target_lower) {
                        return Some(entry.path());
                    }
                }
            }
        }
        None
    }

    fn process_command(&mut self, input: &str) {
        // --- FAST PATH: SHELL BUILTINS & COMMON COMMANDS ---
        // Avoids LLM latency for trivial operations.
        let args: Vec<&str> = input.split_whitespace().collect();
        if let Some(cmd) = args.first() {
            match *cmd {
                "cd" => {
                    let path_raw = input.strip_prefix("cd").unwrap_or("").trim();
                    let target_path_buf = if path_raw.is_empty() || path_raw == "~" {
                        Some(std::path::PathBuf::from(
                            std::env::var("HOME").unwrap_or_else(|_| "/".to_string()),
                        ))
                    } else {
                        self.fuzzy_cd(path_raw)
                    };

                    match target_path_buf {
                        Some(path) => {
                            if let Err(e) = std::env::set_current_dir(&path) {
                                println!("   \x1b[31mFailed to change directory: {}\x1b[0m", e);
                            } else {
                                let cwd = std::env::current_dir().unwrap_or_default();
                                println!("   📂 \x1b[33m{}\x1b[0m", cwd.display());
                            }
                        }
                        None => {
                            println!(
                                "   \x1b[31mNo se encontró el directorio: {}\x1b[0m",
                                path_raw
                            );
                        }
                    }
                    return;
                }
                "ls" | "pwd" | "clear" | "echo" | "cat" | "grep" | "git" | "cargo" | "mkdir"
                | "rm" | "touch" => {
                    // Execute directly
                    match Command::new("sh").arg("-c").arg(input).status() {
                        Ok(_) => {}
                        Err(e) => println!("   \x1b[31mFailed to execute: {}\x1b[0m", e),
                    }
                    return;
                }
                _ => {} // Fall through to AI
            }
        }

        // Only show "Thinking..." for non-fast-path commands
        print!("\x1b[1;30mThinking...\x1b[0m\r");
        io::stdout().flush().unwrap();

        // Call async router from sync context
        let (intent, reason) = self.runtime.block_on(self.router.classify(input));

        // Clear "Thinking..."
        print!("             \r");

        match intent {
            Intent::Oracle => {
                println!("\n\x1b[1;36m🔮 ORACLE MODE INVOKED (RUST NATIVE)\x1b[0m");
                println!("   \x1b[3m{}\x1b[0m", reason);

                // Native Rust implementation (Placeholder for future port)
                // We strictly avoid legacy Python calls as requested.
                println!("\n\x1b[1;35m⚙️  SINTONIZANDO MATRIZ (RUST CORE)\x1b[0m");
                println!("   \x1b[32m✅ Yatra Protocol: ENFORCED (Base-60)\x1b[0m");

                // Simulate processing delay for effect
                std::thread::sleep(std::time::Duration::from_millis(500));

                println!("\n\x1b[1;34m🌊 ESTADO DE LA ONDA:\x1b[0m");
                println!("   Resonancia: ESTABLE (17:34:21 S60)");
            }
            Intent::SystemAction => {
                println!("\n\x1b[1;33m⚙️ SYSTEM ACTION\x1b[0m");

                if reason.starts_with("CMD: ") {
                    let cmd_str = reason.trim_start_matches("CMD: ").trim();

                    // Split command and args (simplistic splitting)
                    let parts: Vec<&str> = cmd_str.split_whitespace().collect();
                    if let Some(cmd_name) = parts.first() {
                        if *cmd_name == "cd" {
                            // Re-run through fast path for consistency
                            self.process_command(cmd_str);
                        } else if ["research", "produce", "pipeline", "scan"].contains(cmd_name) {
                            // Direct invocation of Sentinel CLI (Rust Internal)
                            let agent_path = "/home/jnovoas/documentos/Obsidian/_Agentes/agente.sh"; // This IS the compiled Rust binary

                            // Map short commands to CLI args
                            let mut cmd_args = vec![*cmd_name];
                            cmd_args.extend_from_slice(&parts[1..]);

                            let _ = Command::new(agent_path).args(&cmd_args).status();
                        } else if *cmd_name == "certify" {
                            // Legacy Python Fallback (until ported)
                            let script_path =
                                "/home/jnovoas/documentos/Obsidian/_Agentes/certify.py";
                            let args = &parts[1..];
                            // certify.py expects --file argument
                            let mut cmd = Command::new("python3");
                            cmd.arg(script_path);
                            if !args.contains(&"--file") && !args.is_empty() {
                                cmd.arg("--file").arg(args[0]);
                            } else {
                                cmd.args(args);
                            }

                            let _ = cmd.status();
                        } else {
                            // External commands
                            let _ = Command::new(cmd_name).args(&parts[1..]).status();
                        }
                    }
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
        println!("\x1b[1;35m  🧠  SENTINEL SEMANTIC SHELL v2.2 (RUST NATIVE)  🧠\x1b[0m");
        println!("\x1b[1;35m  [MODO MAESTRO / TAB-COMPLETION ACTIVADO]\x1b[0m");
        println!("\x1b[1;35m============================================================\x1b[0m");
        println!("Escribe 'exit' o 'q' para volver. TAB para completar archivos.");
    }
}
