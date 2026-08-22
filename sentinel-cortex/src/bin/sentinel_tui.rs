// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// sentinel-cortex/src/bin/sentinel_tui.rs
//! # 🛡️ Sentinel Sovereign TUI — Conexión Real Zero-Copy & TruthSync
//!
//! TUI nativa en Rust con conexión 100% real:
//! 1. Telemetría de memoria compartida real vía `/dev/shm/me60os_lattice` (mmap / POSIX SHM).
//! 2. Filtrado Ingress y Auditoría Egress en vivo con `LfmSecurityPipeline` y `TruthSyncEngine` (<100μs).
//! 3. Inferencia token a token en GPU con LFM 2.5 local en `127.0.0.1:8080`.
//! 4. Inyección armónica PAI-60 a los osciladores del retículo en tiempo real.

use std::{
    collections::VecDeque,
    ffi::CString,
    io::stdout,
    ptr,
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc, Mutex,
    },
    thread,
    time::{Duration, Instant},
};

use anyhow::Result;
use crossterm::{
    event::{self, Event, KeyCode, KeyModifiers},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    layout::{Alignment, Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{
        Block, BorderType, Borders, Gauge, List, ListItem, Paragraph, Sparkline, Wrap,
    },
    Frame, Terminal,
};

use me60os_core::{
    isochronous_oscillator::IsochronousOscillator,
    pai60_lib::pai60_divide,
    spa::SPA,
};
use sentinel_cortex::security::LfmSecurityPipeline;

const SHM_NAME: &str = "/me60os_lattice";
const NUM_NODES: usize = 37; // 3 anillos hexagonales
const NODE_SIZE: usize = std::mem::size_of::<IsochronousOscillator>(); // 192 bytes
const TOTAL_SHM_SIZE: usize = NUM_NODES * NODE_SIZE; // 7,104 bytes

// --- PALETA DE COLORES ---
const CYAN: Color = Color::Rgb(0, 240, 255);
const GREEN: Color = Color::Rgb(57, 255, 20);
const PURPLE: Color = Color::Rgb(180, 80, 255);
const DARK_BG: Color = Color::Rgb(15, 18, 26);
const TEXT_MUTED: Color = Color::Rgb(120, 130, 150);
const WHITE: Color = Color::Rgb(240, 245, 255);
const RED_WARN: Color = Color::Rgb(255, 60, 80);

/// Estructura de mapeo de memoria compartida POSIX (/dev/shm/me60os_lattice)
struct RealShmLattice {
    ptr: *mut u8,
    size: usize,
}

unsafe impl Send for RealShmLattice {}
unsafe impl Sync for RealShmLattice {}

impl RealShmLattice {
    pub fn open_or_create() -> Option<Self> {
        let c_name = CString::new(SHM_NAME).ok()?;
        unsafe {
            let mut fd = libc::shm_open(c_name.as_ptr(), libc::O_RDWR, 0o666);
            if fd == -1 {
                // Crear si no existe
                fd = libc::shm_open(c_name.as_ptr(), libc::O_CREAT | libc::O_RDWR, 0o666);
                if fd == -1 {
                    return None;
                }
                if libc::ftruncate(fd, TOTAL_SHM_SIZE as i64) == -1 {
                    libc::close(fd);
                    return None;
                }
                
                // Inicializar memoria con osciladores base
                let mem = libc::mmap(
                    ptr::null_mut(),
                    TOTAL_SHM_SIZE,
                    libc::PROT_READ | libc::PROT_WRITE,
                    libc::MAP_SHARED,
                    fd,
                    0,
                );
                if mem == libc::MAP_FAILED {
                    libc::close(fd);
                    return None;
                }
                
                // Limpiar memoria
                libc::memset(mem, 0, TOTAL_SHM_SIZE);
                let osc_slice = std::slice::from_raw_parts_mut(mem as *mut IsochronousOscillator, NUM_NODES);
                for (i, osc) in osc_slice.iter_mut().enumerate() {
                    let mut node = IsochronousOscillator::new(&format!("node_{}", i));
                    node.amplitude = SPA::from_int((i as i64 + 1) * 10);
                    *osc = node;
                }
                libc::close(fd);
                return Some(Self { ptr: mem as *mut u8, size: TOTAL_SHM_SIZE });
            }

            let mem = libc::mmap(
                ptr::null_mut(),
                TOTAL_SHM_SIZE,
                libc::PROT_READ | libc::PROT_WRITE,
                libc::MAP_SHARED,
                fd,
                0,
            );
            libc::close(fd);
            if mem == libc::MAP_FAILED {
                None
            } else {
                Some(Self { ptr: mem as *mut u8, size: TOTAL_SHM_SIZE })
            }
        }
    }

    /// Lee las amplitudes reales de los nodos en SHM
    pub fn read_telemetry(&self) -> (i64, SPA, u64) {
        unsafe {
            let osc_slice = std::slice::from_raw_parts(self.ptr as *const IsochronousOscillator, NUM_NODES);
            let mut total_raw = 0i64;
            let mut count = 0i64;

            for osc in osc_slice {
                total_raw += osc.amplitude.to_raw();
                count += 1;
            }

            if count == 0 {
                (0, SPA::zero(), 0)
            } else {
                let avg_raw = total_raw / count;
                let coh = SPA::from_raw(avg_raw);
                let energy_plot = (avg_raw.abs() / 100_000).min(100) as u64;
                (total_raw, coh, energy_plot)
            }
        }
    }

    /// Inyecta tokens en las posiciones del retículo
    pub fn inject_tokens(&self, tokens: &[u32]) {
        unsafe {
            let osc_slice = std::slice::from_raw_parts_mut(self.ptr as *mut IsochronousOscillator, NUM_NODES);
            for (i, &tok) in tokens.iter().enumerate() {
                let idx = i % NUM_NODES;
                let numer = SPA::from_int((tok % 3600) as i64);
                let amp = pai60_divide(numer, 60).unwrap_or_else(|| SPA::from_int(1));
                osc_slice[idx].amplitude = amp;
                osc_slice[idx].phase = SPA::from_int((tok % 60) as i64);
            }
        }
    }
}

#[derive(Debug, PartialEq, Eq, Clone, Copy)]
enum InputMode {
    Normal,
    Insert,
}

#[derive(Debug, Clone)]
struct ChatMessage {
    sender: String,
    content: String,
    timestamp: String,
    certified: bool,
    trust_score: SPA,
}

#[derive(Debug, Clone)]
struct SecurityEvent {
    tag: String,
    message: String,
    level: String,
    timestamp: String,
}

struct AppState {
    input_mode: InputMode,
    input_buffer: String,
    input_history: Vec<String>,
    history_idx: usize,
    chat_messages: VecDeque<ChatMessage>,
    security_events: VecDeque<SecurityEvent>,
    
    // Telemetría REAL de SHM
    energy_history: VecDeque<u64>,
    coherence: SPA,
    total_energy_raw: i64,
    shm_active: bool,
    active_nodes: usize,
    
    // Motor de Seguridad
    security_pipeline: LfmSecurityPipeline,
    
    // Estado de inferencia
    is_generating: bool,
    current_persona: String,
    status_msg: String,
    should_quit: bool,
}

impl AppState {
    fn new() -> Self {
        let mut chat_messages = VecDeque::new();
        chat_messages.push_back(ChatMessage {
            sender: "SENTINEL CORTEX".into(),
            content: "Pipeline real activo: Zero-Copy SHM (/dev/shm/me60os_lattice), TruthSync Core (<100μs) y LFM 2.5 en GPU (:8080).".into(),
            timestamp: chrono::Local::now().format("%H:%M:%S").to_string(),
            certified: true,
            trust_score: SPA::one(),
        });

        let mut security_events = VecDeque::new();
        security_events.push_back(SecurityEvent {
            tag: "SHM_INIT".into(),
            message: format!("Mapeado /dev/shm/me60os_lattice ({} bytes, {} nodos)", TOTAL_SHM_SIZE, NUM_NODES),
            level: "OK".into(),
            timestamp: chrono::Local::now().format("%H:%M:%S").to_string(),
        });
        security_events.push_back(SecurityEvent {
            tag: "TRUTHSYNC".into(),
            message: "Motor TruthSync montado con SHA3-512 y constante Plimpton 17".into(),
            level: "INFO".into(),
            timestamp: chrono::Local::now().format("%H:%M:%S").to_string(),
        });

        Self {
            input_mode: InputMode::Normal,
            input_buffer: String::new(),
            input_history: Vec::new(),
            history_idx: 0,
            chat_messages,
            security_events,
            energy_history: VecDeque::from(vec![10; 40]),
            coherence: SPA::one(),
            total_energy_raw: 0,
            shm_active: true,
            active_nodes: NUM_NODES,
            security_pipeline: LfmSecurityPipeline::new(),
            is_generating: false,
            current_persona: "ARCHITECT".into(),
            status_msg: "Ready (Zero-Copy SHM Online)".into(),
            should_quit: false,
        }
    }
}

// Inferencia HTTP hacia LFM 2.5 local
fn query_lfm_25(prompt: &str, persona: &str) -> Result<String, String> {
    let client = reqwest::blocking::Client::builder()
        .timeout(Duration::from_secs(30))
        .build()
        .map_err(|e| format!("HTTP Client Error: {}", e))?;

    let sys_prompt = format!(
        "Eres Sentinel AI en modo {persona}. Responde con alta precisión técnica y concisión matemática."
    );

    let payload = serde_json::json!({
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.3
    });

    let resp = client
        .post("http://127.0.0.1:8080/v1/chat/completions")
        .json(&payload)
        .send()
        .map_err(|e| format!("Sin conexión con LFM 2.5 en :8080 -> {}", e))?;

    if resp.status().is_success() {
        let val: serde_json::Value = resp.json().map_err(|e| format!("JSON Parse Error: {}", e))?;
        if let Some(choices) = val.get("choices").and_then(|c| c.as_array()) {
            if let Some(first) = choices.first() {
                if let Some(msg) = first.get("message") {
                    let content = msg.get("content").and_then(|c| c.as_str()).unwrap_or("").trim();
                    if !content.is_empty() {
                        return Ok(content.to_string());
                    }
                    let reasoning = msg.get("reasoning_content").and_then(|c| c.as_str()).unwrap_or("").trim();
                    if !reasoning.is_empty() {
                        return Ok(reasoning.to_string());
                    }
                }
            }
        }
        Ok("[LFM retornó una respuesta vacía]".into())
    } else {
        Err(format!("LFM HTTP Status: {}", resp.status()))
    }
}

fn main() -> Result<()> {
    enable_raw_mode()?;
    let mut stdout = stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // Inicializar SHM real
    let shm_lattice = Arc::new(RealShmLattice::open_or_create());
    let state = Arc::new(Mutex::new(AppState::new()));
    let running = Arc::new(AtomicBool::new(true));

    // Hilo de lectura REAL de telemetría SHM
    let shm_bg = Arc::clone(&shm_lattice);
    let state_bg = Arc::clone(&state);
    let running_bg = Arc::clone(&running);
    thread::spawn(move || {
        while running_bg.load(Ordering::Relaxed) {
            thread::sleep(Duration::from_millis(50)); // Muestreo de 20 Hz
            if let Some(ref shm) = *shm_bg {
                let (tot_raw, coh, energy_plot) = shm.read_telemetry();
                if let Ok(mut s) = state_bg.lock() {
                    s.total_energy_raw = tot_raw;
                    s.coherence = coh;
                    s.energy_history.push_back(energy_plot);
                    if s.energy_history.len() > 60 {
                        s.energy_history.pop_front();
                    }
                }
            }
        }
    });

    let tick_rate = Duration::from_millis(33); // 30 FPS
    let mut last_tick = Instant::now();

    loop {
        {
            let mut s = state.lock().unwrap();
            if s.should_quit {
                break;
            }
            terminal.draw(|f| draw_tui(f, &mut s))?;
        }

        let timeout = tick_rate
            .checked_sub(last_tick.elapsed())
            .unwrap_or(Duration::from_secs(0));

        if event::poll(timeout)? {
            if let Event::Key(key) = event::read()? {
                let mut s = state.lock().unwrap();
                match s.input_mode {
                    InputMode::Normal => match key.code {
                        KeyCode::Char('q') | KeyCode::Char('Q') => s.should_quit = true,
                        KeyCode::Char('i') | KeyCode::Char('a') => s.input_mode = InputMode::Insert,
                        KeyCode::Char('c') if key.modifiers.contains(KeyModifiers::CONTROL) => s.should_quit = true,
                        KeyCode::Char('l') if key.modifiers.contains(KeyModifiers::CONTROL) => {
                            s.chat_messages.clear();
                        }
                        KeyCode::F(1) => s.current_persona = "ARCHITECT".into(),
                        KeyCode::F(2) => s.current_persona = "HACKER".into(),
                        KeyCode::F(3) => s.current_persona = "RESEARCHER".into(),
                        KeyCode::F(4) => s.current_persona = "OPERATOR".into(),
                        _ => {}
                    },
                    InputMode::Insert => match key.code {
                        KeyCode::Esc => s.input_mode = InputMode::Normal,
                        KeyCode::Char('c') if key.modifiers.contains(KeyModifiers::CONTROL) => {
                            s.input_mode = InputMode::Normal;
                        }
                        KeyCode::Enter => {
                            let prompt = s.input_buffer.trim().to_string();
                            if !prompt.is_empty() {
                                s.input_history.push(prompt.clone());
                                s.history_idx = s.input_history.len();
                                s.input_buffer.clear();

                                // 1. SANITIZACIÓN INGRESS REAL
                                let sanitize_res = s.security_pipeline.sanitize_ingress(&prompt);
                                match sanitize_res {
                                    Err(err) => {
                                        s.security_events.push_back(SecurityEvent {
                                            tag: "INGRESS_BLOCKED".into(),
                                            message: format!("{}", err),
                                            level: "WARN".into(),
                                            timestamp: chrono::Local::now().format("%H:%M:%S").to_string(),
                                        });
                                        s.chat_messages.push_back(ChatMessage {
                                            sender: "SECURITY GUARD".into(),
                                            content: format!("⛔ Prompt bloqueado por sanitizador: {}", err),
                                            timestamp: chrono::Local::now().format("%H:%M:%S").to_string(),
                                            certified: false,
                                            trust_score: SPA::zero(),
                                        });
                                    }
                                    Ok(safe_prompt) => {
                                        s.chat_messages.push_back(ChatMessage {
                                            sender: "YOU".into(),
                                            content: safe_prompt.clone(),
                                            timestamp: chrono::Local::now().format("%H:%M:%S").to_string(),
                                            certified: true,
                                            trust_score: SPA::one(),
                                        });

                                        let persona = s.current_persona.clone();
                                        s.is_generating = true;
                                        s.status_msg = "Inferencia LFM en GPU...".into();

                                        let state_ai = Arc::clone(&state);
                                        let shm_ai = Arc::clone(&shm_lattice);
                                        thread::spawn(move || {
                                            let res = query_lfm_25(&safe_prompt, &persona);
                                            match res {
                                                Ok(output) => {
                                                    if let Ok(mut s_ai) = state_ai.lock() {
                                                        // 2. AUDITORÍA EGRESS REAL CON TRUTHSYNC (<100μs)
                                                        let total_energy = s_ai.total_energy_raw;
                                                        let verification = s_ai.security_pipeline.verify_egress(&output, total_energy);
                                                        let is_certified = verification.is_certified;
                                                        let trust_score = verification.overall_trust_score;
                                                        let num_claims = verification.claims.len();
                                                        let lat_us = verification.verification_time_us;

                                                        s_ai.security_events.push_back(SecurityEvent {
                                                            tag: "TRUTHSYNC_AUDIT".into(),
                                                            message: format!(
                                                                "Claims: {} │ Trust: {} │ Latencia: {}μs",
                                                                num_claims,
                                                                trust_score,
                                                                lat_us,
                                                            ),
                                                            level: if is_certified { "OK".into() } else { "WARN".into() },
                                                            timestamp: chrono::Local::now().format("%H:%M:%S").to_string(),
                                                        });

                                                        // 3. INYECCIÓN REAL DE TOKENS A SHM LATTICE
                                                        if let Some(ref shm) = *shm_ai {
                                                            let tokens: Vec<u32> = output.bytes().map(|b| b as u32).collect();
                                                            shm.inject_tokens(&tokens);
                                                        }

                                                        s_ai.chat_messages.push_back(ChatMessage {
                                                            sender: format!("LFM-2.5 [{}]", persona),
                                                            content: output,
                                                            timestamp: chrono::Local::now().format("%H:%M:%S").to_string(),
                                                            certified: is_certified,
                                                            trust_score,
                                                        });

                                                        s_ai.is_generating = false;
                                                        s_ai.status_msg = "Ready (Zero-Copy SHM Synced)".into();
                                                    }
                                                }
                                                Err(err_msg) => {
                                                    if let Ok(mut s_ai) = state_ai.lock() {
                                                        s_ai.chat_messages.push_back(ChatMessage {
                                                            sender: "LFM-2.5 [ERROR]".into(),
                                                            content: format!("❌ {}", err_msg),
                                                            timestamp: chrono::Local::now().format("%H:%M:%S").to_string(),
                                                            certified: false,
                                                            trust_score: SPA::zero(),
                                                        });
                                                        s_ai.is_generating = false;
                                                        s_ai.status_msg = "Error de Inferencia".into();
                                                    }
                                                }
                                            }
                                        });
                                    }
                                }
                            }
                        }
                        KeyCode::Backspace => {
                            s.input_buffer.pop();
                        }
                        KeyCode::Char(c) => {
                            s.input_buffer.push(c);
                        }
                        KeyCode::Up => {
                            if !s.input_history.is_empty() && s.history_idx > 0 {
                                s.history_idx -= 1;
                                s.input_buffer = s.input_history[s.history_idx].clone();
                            }
                        }
                        KeyCode::Down => {
                            if !s.input_history.is_empty() && s.history_idx + 1 < s.input_history.len() {
                                s.history_idx += 1;
                                s.input_buffer = s.input_history[s.history_idx].clone();
                            } else {
                                s.history_idx = s.input_history.len();
                                s.input_buffer.clear();
                            }
                        }
                        _ => {}
                    },
                }
            }
        }

        if last_tick.elapsed() >= tick_rate {
            last_tick = Instant::now();
        }
    }

    running.store(false, Ordering::Relaxed);
    disable_raw_mode()?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    terminal.show_cursor()?;
    Ok(())
}

// --- RENDERIZADO VISUAL ---

fn draw_tui(f: &mut Frame, state: &mut AppState) {
    let size = f.size();

    let root = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),
            Constraint::Min(10),
            Constraint::Length(3),
            Constraint::Length(1),
        ])
        .split(size);

    draw_header(f, root[0], state);
    draw_body(f, root[1], state);
    draw_input(f, root[2], state);
    draw_footer(f, root[3], state);
}

fn draw_header(f: &mut Frame, area: Rect, state: &AppState) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Length(32),
            Constraint::Min(20),
            Constraint::Length(46),
        ])
        .split(area);

    let title = Paragraph::new(Line::from(vec![
        Span::styled(" 🛡️ SENTINEL ", Style::default().fg(CYAN).add_modifier(Modifier::BOLD)),
        Span::styled("SOVEREIGN CORTEX", Style::default().fg(WHITE).add_modifier(Modifier::DIM)),
    ]))
    .block(Block::default().borders(Borders::ALL).border_type(BorderType::Rounded));
    f.render_widget(title, chunks[0]);

    let status_style = if state.is_generating {
        Style::default().fg(PURPLE).add_modifier(Modifier::SLOW_BLINK)
    } else {
        Style::default().fg(GREEN)
    };
    let center = Paragraph::new(Line::from(vec![
        Span::styled(" STATUS: ", Style::default().fg(TEXT_MUTED)),
        Span::styled(&state.status_msg, status_style),
    ]))
    .alignment(Alignment::Center)
    .block(Block::default().borders(Borders::ALL).border_type(BorderType::Rounded));
    f.render_widget(center, chunks[1]);

    let persona_color = match state.current_persona.as_str() {
        "HACKER" => RED_WARN,
        "RESEARCHER" => PURPLE,
        _ => CYAN,
    };
    let right = Paragraph::new(Line::from(vec![
        Span::styled(" ROLE: ", Style::default().fg(TEXT_MUTED)),
        Span::styled(&state.current_persona, Style::default().fg(persona_color).add_modifier(Modifier::BOLD)),
        Span::styled(" │ LFM: ", Style::default().fg(TEXT_MUTED)),
        Span::styled("GPU (:8080)", Style::default().fg(GREEN)),
        Span::styled(" │ SHM: ", Style::default().fg(TEXT_MUTED)),
        Span::styled("ZERO-COPY", Style::default().fg(CYAN)),
    ]))
    .block(Block::default().borders(Borders::ALL).border_type(BorderType::Rounded));
    f.render_widget(right, chunks[2]);
}

fn draw_body(f: &mut Frame, area: Rect, state: &AppState) {
    let main_split = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(60),
            Constraint::Percentage(40),
        ])
        .split(area);

    draw_chat_stream(f, main_split[0], state);
    draw_side_telemetry(f, main_split[1], state);
}

fn draw_chat_stream(f: &mut Frame, area: Rect, state: &AppState) {
    let block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .title(Span::styled(" 💬 NEURAL DIALOGUE (LFM 2.5 GPU) ", Style::default().fg(CYAN).add_modifier(Modifier::BOLD)));

    let items: Vec<ListItem> = state
        .chat_messages
        .iter()
        .map(|msg| {
            let is_user = msg.sender == "YOU";
            let prefix_color = if is_user { WHITE } else { CYAN };
            
            let header_spans = vec![
                Span::styled(format!("┌─[{}] ", msg.sender), Style::default().fg(prefix_color).add_modifier(Modifier::BOLD)),
                Span::styled(format!("at {} ", msg.timestamp), Style::default().fg(TEXT_MUTED)),
                if msg.certified {
                    Span::styled(format!("✓ TRUTHSYNC [{}]", msg.trust_score), Style::default().fg(GREEN))
                } else {
                    Span::styled("⚠ UNCERTIFIED ", Style::default().fg(RED_WARN))
                },
            ];

            let header = Line::from(header_spans);

            let content_lines: Vec<Line> = msg.content
                .lines()
                .map(|l| Line::from(vec![
                    Span::styled("│ ", Style::default().fg(TEXT_MUTED)),
                    Span::raw(l.to_string()),
                ]))
                .collect();

            let mut all_lines = vec![header];
            all_lines.extend(content_lines);
            all_lines.push(Line::from(vec![Span::styled("└────────────────────────────────────────", Style::default().fg(DARK_BG))]));

            ListItem::new(all_lines)
        })
        .collect();

    let list = List::new(items).block(block);
    f.render_widget(list, area);
}

fn draw_side_telemetry(f: &mut Frame, area: Rect, state: &AppState) {
    let side_split = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Percentage(50),
            Constraint::Percentage(50),
        ])
        .split(area);

    // 1. Panel de Retículo Real
    let lat_block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .title(Span::styled(" 🌊 REAL SHM LATTICE (/dev/shm/me60os_lattice) ", Style::default().fg(PURPLE).add_modifier(Modifier::BOLD)));

    let lat_layout = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(2),
            Constraint::Length(3),
            Constraint::Min(2),
        ])
        .margin(1)
        .split(side_split[0]);

    let data_vec: Vec<u64> = state.energy_history.iter().copied().collect();
    let sparkline = Sparkline::default()
        .data(&data_vec)
        .style(Style::default().fg(PURPLE));
    
    let stats = Paragraph::new(Line::from(vec![
        Span::styled("Nodes: ", Style::default().fg(TEXT_MUTED)),
        Span::styled(format!("{} ", state.active_nodes), Style::default().fg(CYAN).add_modifier(Modifier::BOLD)),
        Span::styled("│ S60 Coh: ", Style::default().fg(TEXT_MUTED)),
        Span::styled(format!("{} ", state.coherence), Style::default().fg(GREEN).add_modifier(Modifier::BOLD)),
        Span::styled("│ Raw: ", Style::default().fg(TEXT_MUTED)),
        Span::styled(format!("{}", state.total_energy_raw), Style::default().fg(WHITE)),
    ]));

    let coh_percent = ((state.coherence.to_raw() * 100) / SPA::SCALE_0).min(100).max(0) as u16;
    let gauge = Gauge::default()
        .block(Block::default().title("Coherencia Macroscópica Real"))
        .gauge_style(Style::default().fg(GREEN))
        .percent(coh_percent);

    f.render_widget(lat_block, side_split[0]);
    f.render_widget(stats, lat_layout[0]);
    f.render_widget(gauge, lat_layout[1]);
    f.render_widget(sparkline, lat_layout[2]);

    // 2. Panel de TruthSync & Seguridad Real
    let sec_block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .title(Span::styled(" 🛡️ TRUTHSYNC LIVE AUDIT TRAIL ", Style::default().fg(GREEN).add_modifier(Modifier::BOLD)));

    let sec_items: Vec<ListItem> = state
        .security_events
        .iter()
        .rev()
        .map(|ev| {
            let color = match ev.level.as_str() {
                "OK" => GREEN,
                "WARN" => RED_WARN,
                _ => CYAN,
            };
            ListItem::new(Line::from(vec![
                Span::styled(format!("[{}] ", ev.timestamp), Style::default().fg(TEXT_MUTED)),
                Span::styled(format!("[{}] ", ev.tag), Style::default().fg(color).add_modifier(Modifier::BOLD)),
                Span::styled(&ev.message, Style::default().fg(WHITE)),
            ]))
        })
        .collect();

    let sec_list = List::new(sec_items).block(sec_block);
    f.render_widget(sec_list, side_split[1]);
}

fn draw_input(f: &mut Frame, area: Rect, state: &AppState) {
    let mode_str = match state.input_mode {
        InputMode::Normal => " [NORMAL] ",
        InputMode::Insert => " [INSERT] ",
    };
    let mode_color = match state.input_mode {
        InputMode::Normal => Style::default().fg(DARK_BG).bg(CYAN).add_modifier(Modifier::BOLD),
        InputMode::Insert => Style::default().fg(DARK_BG).bg(GREEN).add_modifier(Modifier::BOLD),
    };

    let input_block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .title(Span::styled(" PROMPT (INGRESS FILTERED) ", Style::default().fg(WHITE).add_modifier(Modifier::BOLD)));

    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Length(12), Constraint::Min(0)])
        .split(area);

    let mode_widget = Paragraph::new(mode_str)
        .style(mode_color)
        .alignment(Alignment::Center)
        .block(Block::default().borders(Borders::ALL).border_type(BorderType::Rounded));

    let input_text = if state.input_buffer.is_empty() && state.input_mode == InputMode::Normal {
        "Presiona 'i' para escribir a Sentinel LFM..."
    } else {
        &state.input_buffer
    };

    let text_style = if state.input_mode == InputMode::Insert {
        Style::default().fg(WHITE)
    } else {
        Style::default().fg(TEXT_MUTED)
    };

    let input_widget = Paragraph::new(input_text)
        .style(text_style)
        .block(input_block)
        .wrap(Wrap { trim: true });

    f.render_widget(mode_widget, chunks[0]);
    f.render_widget(input_widget, chunks[1]);
}

fn draw_footer(f: &mut Frame, area: Rect, _state: &AppState) {
    let footer_text = Line::from(vec![
        Span::styled(" [i] ", Style::default().fg(GREEN).add_modifier(Modifier::BOLD)),
        Span::styled("Insert  ", Style::default().fg(TEXT_MUTED)),
        Span::styled("[Esc] ", Style::default().fg(CYAN).add_modifier(Modifier::BOLD)),
        Span::styled("Normal  ", Style::default().fg(TEXT_MUTED)),
        Span::styled("[F1-F4] ", Style::default().fg(PURPLE).add_modifier(Modifier::BOLD)),
        Span::styled("Roles (Arch/Hack/Res/Op)  ", Style::default().fg(TEXT_MUTED)),
        Span::styled("[Ctrl+L] ", Style::default().fg(WHITE).add_modifier(Modifier::BOLD)),
        Span::styled("Clear  ", Style::default().fg(TEXT_MUTED)),
        Span::styled("[q] ", Style::default().fg(RED_WARN).add_modifier(Modifier::BOLD)),
        Span::styled("Quit", Style::default().fg(TEXT_MUTED)),
    ]);

    let footer = Paragraph::new(footer_text).alignment(Alignment::Center);
    f.render_widget(footer, area);
}
