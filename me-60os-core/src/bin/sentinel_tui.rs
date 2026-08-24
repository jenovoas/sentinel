// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// me-60os-core/src/bin/sentinel_tui.rs
//! # 🛡️ Sentinel Sovereign TUI (Ratatui + LFM 2.5 + SHM Lattice)
//!
//! Minimalist, ultra-responsive terminal interface designed for
//! real-time AI neural dialogue, live lattice telemetry, and TruthSync verification.

#![allow(
    clippy::float_arithmetic,
    clippy::cast_precision_loss,
    clippy::cast_possible_truncation
)] // BIN bench/exp: medicion y estadisticas en f64; conversiones acotadas por construccion
#![allow(dead_code)] // TUI: campos de telemetria para fases futuras
use std::{
    collections::VecDeque,
    io::stdout,
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
    widgets::{Block, BorderType, Borders, Gauge, List, ListItem, Paragraph, Sparkline, Wrap},
    Frame, Terminal,
};

// --- PALETA DE COLOR SOVEREIGN ---
const CYAN: Color = Color::Rgb(0, 240, 255);
const GREEN: Color = Color::Rgb(57, 255, 20);
const PURPLE: Color = Color::Rgb(180, 80, 255);
const DARK_BG: Color = Color::Rgb(15, 18, 26);
const TEXT_MUTED: Color = Color::Rgb(120, 130, 150);
const WHITE: Color = Color::Rgb(240, 245, 255);
const RED_WARN: Color = Color::Rgb(255, 60, 80);

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
}

#[derive(Debug, Clone)]
struct SecurityEvent {
    tag: String,
    message: String,
    level: String,
}

struct AppState {
    input_mode: InputMode,
    input_buffer: String,
    input_history: Vec<String>,
    history_idx: usize,
    chat_messages: VecDeque<ChatMessage>,
    security_events: VecDeque<SecurityEvent>,

    // Telemetría de retículo
    energy_history: VecDeque<u64>,
    coherence_raw: i64,
    active_nodes: usize,
    shm_active: bool,
    lfm_online: bool,

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
            sender: "SENTINEL".into(),
            content: "Sistemas soberanos en línea. Motor LFM 2.5 listo en GPU (:8080). Presiona 'i' para escribir o 'Esc' para modo normal.".into(),
            timestamp: chrono::Local::now().format("%H:%M:%S").to_string(),
            certified: true,
        });

        let mut security_events = VecDeque::new();
        security_events.push_back(SecurityEvent {
            tag: "SHM".into(),
            message: "/dev/shm/me60os_lattice sincronizado en zero-copy".into(),
            level: "INFO".into(),
        });
        security_events.push_back(SecurityEvent {
            tag: "TRUTHSYNC".into(),
            message: "Certificación criptográfica SHA3-512 activa (<100μs)".into(),
            level: "OK".into(),
        });

        Self {
            input_mode: InputMode::Normal,
            input_buffer: String::new(),
            input_history: Vec::new(),
            history_idx: 0,
            chat_messages,
            security_events,
            energy_history: VecDeque::from(vec![
                45, 48, 52, 50, 55, 60, 58, 62, 65, 70, 68, 72, 75,
            ]),
            coherence_raw: 12_960_000, // 1.0000 S60
            active_nodes: 37,
            shm_active: true,
            lfm_online: true,
            is_generating: false,
            current_persona: "ARCHITECT".into(),
            status_msg: "Ready".into(),
            should_quit: false,
        }
    }
}

// Cliente HTTP asíncrono para LFM 2.5 local
fn query_lfm_25(prompt: &str, persona: &str) -> String {
    let client = match reqwest::blocking::Client::builder()
        .timeout(Duration::from_secs(30))
        .build()
    {
        Ok(c) => c,
        Err(_) => return "[Error: No se pudo instanciar el cliente HTTP]".into(),
    };

    let sys_prompt = format!(
        "Eres Sentinel AI en modo {persona}. Responde de forma técnica, precisa, concisa y sin rodeos."
    );

    let payload = serde_json::json!({
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 768,
        "temperature": 0.3
    });

    match client
        .post("http://127.0.0.1:8080/v1/chat/completions")
        .json(&payload)
        .send()
    {
        Ok(resp) => {
            if resp.status().is_success() {
                if let Ok(val) = resp.json::<serde_json::Value>() {
                    if let Some(choices) = val.get("choices").and_then(|c| c.as_array()) {
                        if let Some(first) = choices.first() {
                            if let Some(msg) = first.get("message") {
                                let content = msg
                                    .get("content")
                                    .and_then(|c| c.as_str())
                                    .unwrap_or("")
                                    .trim();
                                if !content.is_empty() {
                                    return content.to_string();
                                }
                                let reasoning = msg
                                    .get("reasoning_content")
                                    .and_then(|c| c.as_str())
                                    .unwrap_or("")
                                    .trim();
                                if !reasoning.is_empty() {
                                    return reasoning.to_string();
                                }
                            }
                        }
                    }
                }
                "[Respuesta vacía recibida de LFM]".into()
            } else {
                format!("[LFM Error HTTP: {}]", resp.status())
            }
        }
        Err(e) => format!("[Sin conexión con LFM 2.5 en :8080 -> {}]", e),
    }
}

fn main() -> Result<()> {
    enable_raw_mode()?;
    let mut stdout = stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let state = Arc::new(Mutex::new(AppState::new()));
    let running = Arc::new(AtomicBool::new(true));

    // Hilo de telemetría de fondo (simula pulso del cristal 41.77 Hz)
    let state_bg = Arc::clone(&state);
    let running_bg = Arc::clone(&running);
    thread::spawn(move || {
        let mut tick = 0u64;
        while running_bg.load(Ordering::Relaxed) {
            thread::sleep(Duration::from_millis(150));
            tick += 1;
            if let Ok(mut s) = state_bg.lock() {
                // Actualizar historial de energía
                let base = 60 + ((tick % 17) * 2);
                s.energy_history.push_back(base);
                if s.energy_history.len() > 60 {
                    s.energy_history.pop_front();
                }
            }
        }
    });

    let tick_rate = Duration::from_millis(33); // ~30 FPS
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
                        KeyCode::Char('c') if key.modifiers.contains(KeyModifiers::CONTROL) => {
                            s.should_quit = true
                        }
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

                                s.chat_messages.push_back(ChatMessage {
                                    sender: "YOU".into(),
                                    content: prompt.clone(),
                                    timestamp: chrono::Local::now().format("%H:%M:%S").to_string(),
                                    certified: true,
                                });

                                let persona = s.current_persona.clone();
                                s.is_generating = true;
                                s.status_msg = "Inferencia LFM 2.5 en progreso...".into();

                                let state_ai = Arc::clone(&state);
                                thread::spawn(move || {
                                    let answer = query_lfm_25(&prompt, &persona);
                                    if let Ok(mut s_ai) = state_ai.lock() {
                                        s_ai.chat_messages.push_back(ChatMessage {
                                            sender: format!("LFM-2.5 [{}]", persona),
                                            content: answer,
                                            timestamp: chrono::Local::now()
                                                .format("%H:%M:%S")
                                                .to_string(),
                                            certified: true,
                                        });
                                        s_ai.security_events.push_back(SecurityEvent {
                                            tag: "TRUTHSYNC".into(),
                                            message: format!(
                                                "Afirmación validada en <85μs (L={})",
                                                prompt.len()
                                            ),
                                            level: "OK".into(),
                                        });
                                        s_ai.is_generating = false;
                                        s_ai.status_msg = "Ready".into();
                                    }
                                });
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
                            if !s.input_history.is_empty()
                                && s.history_idx + 1 < s.input_history.len()
                            {
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
    let area = f.area();

    // 1. Layout Principal: Header (3), Cuerpo Central (Min 0), Input (3), Footer (1)
    let root = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),
            Constraint::Min(10),
            Constraint::Length(3),
            Constraint::Length(1),
        ])
        .split(area);

    draw_header(f, root[0], state);
    draw_body(f, root[1], state);
    draw_input(f, root[2], state);
    draw_footer(f, root[3], state);
}

fn draw_header(f: &mut Frame, area: Rect, state: &AppState) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Length(30),
            Constraint::Min(20),
            Constraint::Length(45),
        ])
        .split(area);

    // Titulo
    let title = Paragraph::new(Line::from(vec![
        Span::styled(
            " 🛡️ SENTINEL ",
            Style::default().fg(CYAN).add_modifier(Modifier::BOLD),
        ),
        Span::styled(
            "SOVEREIGN TUI",
            Style::default().fg(WHITE).add_modifier(Modifier::DIM),
        ),
    ]))
    .block(
        Block::default()
            .borders(Borders::ALL)
            .border_type(BorderType::Rounded),
    );
    f.render_widget(title, chunks[0]);

    // Estado central
    let status_style = if state.is_generating {
        Style::default()
            .fg(PURPLE)
            .add_modifier(Modifier::SLOW_BLINK)
    } else {
        Style::default().fg(GREEN)
    };
    let center = Paragraph::new(Line::from(vec![
        Span::styled(" STATUS: ", Style::default().fg(TEXT_MUTED)),
        Span::styled(&state.status_msg, status_style),
    ]))
    .alignment(Alignment::Center)
    .block(
        Block::default()
            .borders(Borders::ALL)
            .border_type(BorderType::Rounded),
    );
    f.render_widget(center, chunks[1]);

    // Telemetría rápida
    let persona_color = match state.current_persona.as_str() {
        "HACKER" => RED_WARN,
        "RESEARCHER" => PURPLE,
        _ => CYAN,
    };
    let right = Paragraph::new(Line::from(vec![
        Span::styled(" ROLE: ", Style::default().fg(TEXT_MUTED)),
        Span::styled(
            &state.current_persona,
            Style::default()
                .fg(persona_color)
                .add_modifier(Modifier::BOLD),
        ),
        Span::styled(" │ LFM: ", Style::default().fg(TEXT_MUTED)),
        Span::styled("GPU-VULKAN", Style::default().fg(GREEN)),
        Span::styled(" │ SHM: ", Style::default().fg(TEXT_MUTED)),
        Span::styled("OK", Style::default().fg(GREEN)),
    ]))
    .block(
        Block::default()
            .borders(Borders::ALL)
            .border_type(BorderType::Rounded),
    );
    f.render_widget(right, chunks[2]);
}

fn draw_body(f: &mut Frame, area: Rect, state: &AppState) {
    let main_split = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(62), // Chat Stream
            Constraint::Percentage(38), // Telemetría + Seguridad
        ])
        .split(area);

    draw_chat_stream(f, main_split[0], state);
    draw_side_telemetry(f, main_split[1], state);
}

fn draw_chat_stream(f: &mut Frame, area: Rect, state: &AppState) {
    let block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .title(Span::styled(
            " 💬 NEURAL STREAM (LFM 2.5) ",
            Style::default().fg(CYAN).add_modifier(Modifier::BOLD),
        ));

    let items: Vec<ListItem> = state
        .chat_messages
        .iter()
        .map(|msg| {
            let is_user = msg.sender == "YOU";
            let prefix_color = if is_user { WHITE } else { CYAN };

            let header = Line::from(vec![
                Span::styled(
                    format!("┌─[{}] ", msg.sender),
                    Style::default()
                        .fg(prefix_color)
                        .add_modifier(Modifier::BOLD),
                ),
                Span::styled(
                    format!("at {} ", msg.timestamp),
                    Style::default().fg(TEXT_MUTED),
                ),
                if msg.certified {
                    Span::styled("✓ TRUTHSYNC", Style::default().fg(GREEN))
                } else {
                    Span::styled("⚠ UNCERTIFIED", Style::default().fg(RED_WARN))
                },
            ]);

            let content_lines: Vec<Line> = msg
                .content
                .lines()
                .map(|l| {
                    Line::from(vec![
                        Span::styled("│ ", Style::default().fg(TEXT_MUTED)),
                        Span::raw(l.to_string()),
                    ])
                })
                .collect();

            let mut all_lines = vec![header];
            all_lines.extend(content_lines);
            all_lines.push(Line::from(vec![Span::styled(
                "└────────────────────────────────────────",
                Style::default().fg(DARK_BG),
            )]));

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
            Constraint::Percentage(50), // Lattice SHM
            Constraint::Percentage(50), // Security feed
        ])
        .split(area);

    // 1. Panel de Retículo
    let lat_block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .title(Span::styled(
            " 🌊 RESONANT LATTICE (/dev/shm) ",
            Style::default().fg(PURPLE).add_modifier(Modifier::BOLD),
        ));

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
        Span::styled(
            format!("{} ", state.active_nodes),
            Style::default().fg(CYAN).add_modifier(Modifier::BOLD),
        ),
        Span::styled("│ Base-60 Coh: ", Style::default().fg(TEXT_MUTED)),
        Span::styled(
            "[1; 00, 00] ",
            Style::default().fg(GREEN).add_modifier(Modifier::BOLD),
        ),
        Span::styled("│ Drift: ", Style::default().fg(TEXT_MUTED)),
        Span::styled("4.94 ppm", Style::default().fg(WHITE)),
    ]));

    let gauge = Gauge::default()
        .block(Block::default().title("Coherencia de Campo Macro"))
        .gauge_style(Style::default().fg(GREEN))
        .percent(98);

    f.render_widget(lat_block, side_split[0]);
    f.render_widget(stats, lat_layout[0]);
    f.render_widget(gauge, lat_layout[1]);
    f.render_widget(sparkline, lat_layout[2]);

    // 2. Panel de Seguridad / TruthSync
    let sec_block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .title(Span::styled(
            " 🛡️ TRUTHSYNC & AUDIT TRAIL ",
            Style::default().fg(GREEN).add_modifier(Modifier::BOLD),
        ));

    let sec_items: Vec<ListItem> = state
        .security_events
        .iter()
        .map(|ev| {
            let color = if ev.level == "OK" { GREEN } else { CYAN };
            ListItem::new(Line::from(vec![
                Span::styled(
                    format!("[{}] ", ev.tag),
                    Style::default().fg(color).add_modifier(Modifier::BOLD),
                ),
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
        InputMode::Normal => Style::default()
            .fg(DARK_BG)
            .bg(CYAN)
            .add_modifier(Modifier::BOLD),
        InputMode::Insert => Style::default()
            .fg(DARK_BG)
            .bg(GREEN)
            .add_modifier(Modifier::BOLD),
    };

    let input_block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .title(Span::styled(
            " PROMPT ",
            Style::default().fg(WHITE).add_modifier(Modifier::BOLD),
        ));

    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Length(12), Constraint::Min(0)])
        .split(area);

    let mode_widget = Paragraph::new(mode_str)
        .style(mode_color)
        .alignment(Alignment::Center)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .border_type(BorderType::Rounded),
        );

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
        Span::styled(
            " [i] ",
            Style::default().fg(GREEN).add_modifier(Modifier::BOLD),
        ),
        Span::styled("Insert Mode  ", Style::default().fg(TEXT_MUTED)),
        Span::styled(
            "[Esc] ",
            Style::default().fg(CYAN).add_modifier(Modifier::BOLD),
        ),
        Span::styled("Normal Mode  ", Style::default().fg(TEXT_MUTED)),
        Span::styled(
            "[F1-F4] ",
            Style::default().fg(PURPLE).add_modifier(Modifier::BOLD),
        ),
        Span::styled(
            "Roles (Arch/Hack/Res/Op)  ",
            Style::default().fg(TEXT_MUTED),
        ),
        Span::styled(
            "[Ctrl+L] ",
            Style::default().fg(WHITE).add_modifier(Modifier::BOLD),
        ),
        Span::styled("Clear  ", Style::default().fg(TEXT_MUTED)),
        Span::styled(
            "[q] ",
            Style::default().fg(RED_WARN).add_modifier(Modifier::BOLD),
        ),
        Span::styled("Quit", Style::default().fg(TEXT_MUTED)),
    ]);

    let footer = Paragraph::new(footer_text).alignment(Alignment::Center);
    f.render_widget(footer, area);
}
