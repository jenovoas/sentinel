// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
use anyhow::Result;
use chrono::Local;
use crossterm::{
    event::{self, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    layout::{Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, BorderType, Borders, Gauge, List, ListItem, Paragraph, Sparkline, Tabs},
    Frame, Terminal,
};
use serde::{Deserialize, Serialize};
use std::{
    collections::VecDeque,
    io,
    process::Command,
    sync::{Arc, Mutex},
    thread,
    time::{Duration, Instant},
};

// ME-60OS Core Imports
use me60os_core::adm::ADM;
use me60os_core::spa::SPA;

// --- CONSTANTS & STYLES ---
const VID_CYAN: Color = Color::Rgb(0, 255, 255);
const NEON_GREEN: Color = Color::Rgb(57, 255, 20);
const GHOST_WHITE: Color = Color::Rgb(248, 248, 255);

#[derive(Debug, PartialEq, Clone, Copy)]
enum View {
    Observatory,
    Dialogue,
    Orchestrator,
    Factory,
    Hacker,
}

#[derive(Debug, PartialEq, Clone, Copy)]
enum InputMode {
    Normal,
    Insert,
}

#[derive(Debug, Clone)]
struct SystemAgent {
    name: String,
    role: String,
    status: String,
    load: u16,
}

#[derive(Debug, Clone)]
struct ProductionPipeline {
    title: String,
    stage: String,
    progress: u16,
}

#[derive(Serialize)]
struct AIQueryRequest {
    prompt: String,
    mode: String,
    max_tokens: u32,
    temperature: f32,
}

#[derive(Deserialize)]
struct AIQueryResponse {
    response: String,
}

struct App {
    view: View,
    input_mode: InputMode,
    input: String,
    chat_history: VecDeque<(String, String)>,

    // Metrics
    energy_history: VecDeque<u64>,
    coherence: SPA,
    entropy: SPA,
    uptime: Duration,
    start_time: Instant,

    // Systems
    log_events: VecDeque<String>,
    swarm: Vec<SystemAgent>,
    factory: Vec<ProductionPipeline>,
    net: ADM,

    // Identity
    persona: String,
    clawd_online: bool,
    prediction: String,
    should_quit: bool,
    is_asking_ai: bool,
}

impl App {
    fn new() -> Self {
        let mut net = ADM::new();
        for q in -5i64..=5 {
            for r in -5i64..=5 {
                if (q + r).abs() <= 5 {
                    net.add_node(q as i32, r as i32);
                }
            }
        }

        Self {
            view: View::Observatory,
            input_mode: InputMode::Normal,
            input: String::new(),
            chat_history: VecDeque::from(vec![(
                "ORBITAL".into(),
                "Sistemas purgados. Kernel Rust activo. Bienvenido, Jaime.".into(),
            )]),
            energy_history: VecDeque::from(vec![50; 80]),
            coherence: SPA::new(1, 0, 0, 0, 0),
            entropy: SPA::new(0, 0, 50, 0, 0),
            uptime: Duration::from_secs(0),
            start_time: Instant::now(),
            log_events: VecDeque::with_capacity(100),
            swarm: vec![
                SystemAgent {
                    name: "Audit-X".into(),
                    role: "Hacker".into(),
                    status: "Scrutinizing".into(),
                    load: 5,
                },
                SystemAgent {
                    name: "Synapse".into(),
                    role: "Researcher".into(),
                    status: "Thinking".into(),
                    load: 15,
                },
                SystemAgent {
                    name: "Creator".into(),
                    role: "Factory".into(),
                    status: "Watching".into(),
                    load: 2,
                },
            ],
            factory: vec![ProductionPipeline {
                title: "Pipeline S60".into(),
                stage: "Scripting".into(),
                progress: 85,
            }],
            net,
            persona: "ARCHITECT".into(),
            clawd_online: true,
            prediction: String::new(),
            should_quit: false,
            is_asking_ai: false,
        }
    }

    fn on_tick(&mut self) {
        self.uptime = self.start_time.elapsed();
        self.net.tick(SPA::new(0, 0, 0, 0, 1));

        let last = *self.energy_history.back().unwrap_or(&50);
        let drift = (Instant::now().elapsed().as_nanos() % 7) as i64 - 3;
        let new_e = (last as i64 + drift).clamp(10, 95) as u64;
        self.energy_history.push_back(new_e);
        if self.energy_history.len() > 100 {
            self.energy_history.pop_front();
        }
    }

    fn add_log(&mut self, msg: String) {
        let ts = Local::now().format("%H:%M:%S").to_string();
        self.log_events.push_front(format!("[{}] {}", ts, msg));
        if self.log_events.len() > 100 {
            self.log_events.pop_back();
        }
    }
}

fn main() -> Result<()> {
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let app = Arc::new(Mutex::new(App::new()));

    // Background worker
    let app_worker_1 = Arc::clone(&app);
    thread::spawn(move || loop {
        thread::sleep(Duration::from_millis(2000));
        if let Ok(mut app) = app_worker_1.lock() {
            let msgs = [
                "LSM_ALLOW_OPENCODE",
                "EBPF_FILTER_ACTIVE",
                "SHM_RESONANCE_OK",
                "CLAWBOT_SYNC",
            ];
            let idx = (Instant::now().elapsed().as_secs() % 4) as usize;
            app.add_log(msgs[idx].to_string());
        }
    });

    let tick_rate = Duration::from_millis(41);
    let mut last_tick = Instant::now();

    loop {
        let mut app_state = app.lock().unwrap();
        if app_state.should_quit {
            break;
        }

        terminal.draw(|f| draw_ui(f, &mut app_state))?;

        let timeout = tick_rate
            .checked_sub(last_tick.elapsed())
            .unwrap_or(Duration::from_secs(0));
        if event::poll(timeout)? {
            if let Event::Key(key) = event::read()? {
                match app_state.input_mode {
                    InputMode::Normal => match key.code {
                        KeyCode::Char('i') => app_state.input_mode = InputMode::Insert,
                        KeyCode::Char('q') | KeyCode::Char('Q') => app_state.should_quit = true,
                        KeyCode::Char('h') | KeyCode::Left => {
                            app_state.view = match app_state.view {
                                View::Dialogue => View::Observatory,
                                View::Orchestrator => View::Dialogue,
                                View::Factory => View::Orchestrator,
                                View::Hacker => View::Factory,
                                View::Observatory => View::Hacker,
                            };
                        }
                        KeyCode::Char('l') | KeyCode::Right => {
                            app_state.view = match app_state.view {
                                View::Observatory => View::Dialogue,
                                View::Dialogue => View::Orchestrator,
                                View::Orchestrator => View::Factory,
                                View::Factory => View::Hacker,
                                View::Hacker => View::Observatory,
                            };
                        }
                        KeyCode::Char('1') => app_state.view = View::Observatory,
                        KeyCode::Char('2') => app_state.view = View::Dialogue,
                        KeyCode::Char('3') => app_state.view = View::Orchestrator,
                        KeyCode::Char('4') => app_state.view = View::Factory,
                        KeyCode::Char('5') => app_state.view = View::Hacker,
                        KeyCode::F(1) => app_state.persona = "MASTER".into(),
                        KeyCode::F(2) => app_state.persona = "HACKER".into(),
                        KeyCode::F(3) => app_state.persona = "ARCHITECT".into(),
                        KeyCode::F(4) => app_state.persona = "RESEARCHER".into(),
                        KeyCode::F(5) => app_state.persona = "CREATOR".into(),
                        _ => {}
                    },
                    InputMode::Insert => match key.code {
                        KeyCode::Esc => app_state.input_mode = InputMode::Normal,
                        KeyCode::Enter => {
                            let cmd = std::mem::take(&mut app_state.input);
                            if !cmd.is_empty() {
                                app_state
                                    .chat_history
                                    .push_front(("YOU".into(), cmd.clone()));
                                let persona = app_state.persona.clone();
                                let app_worker_ai = Arc::clone(&app);

                                thread::spawn(move || {
                                    if let Ok(mut a) = app_worker_ai.lock() {
                                        a.is_asking_ai = true;
                                    }
                                    let response = call_sentinel_ai(&cmd, &persona);
                                    if let Ok(mut a) = app_worker_ai.lock() {
                                        a.chat_history.push_front((persona, response));
                                        a.is_asking_ai = false;
                                    }
                                });
                            }
                        }
                        KeyCode::Char(c) => {
                            app_state.input.push(c);
                            // Trigger prediction update (Neural Power)
                            let context = app_state.input.clone();
                            let app_worker_predict = Arc::clone(&app);
                            thread::spawn(move || {
                                let mut cmd = Command::new("sentinel");
                                cmd.arg("predict").arg(context);
                                if let Ok(output) = cmd.output() {
                                    if output.status.success() {
                                        let pred =
                                            String::from_utf8_lossy(&output.stdout).to_string();
                                        if let Ok(mut a) = app_worker_predict.lock() {
                                            a.prediction = pred;
                                        }
                                    }
                                }
                            });
                        }
                        KeyCode::Backspace => {
                            app_state.input.pop();
                            app_state.prediction.clear();
                        }
                        KeyCode::Tab
                            if !app_state.prediction.is_empty() => {
                                let p = app_state.prediction.clone();
                                app_state.input.push_str(&p);
                                app_state.prediction.clear();
                            }
                        _ => {}
                    },
                }
            }
        }

        if last_tick.elapsed() >= tick_rate {
            app_state.on_tick();
            last_tick = Instant::now();
        }
    }

    disable_raw_mode()?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    terminal.show_cursor()?;
    Ok(())
}

fn call_sentinel_ai(prompt: &str, mode: &str) -> String {
    let client = match reqwest::blocking::Client::builder()
        .timeout(Duration::from_secs(15))
        .build()
    {
        Ok(c) => c,
        Err(_) => return "Error: No se pudo inicializar el cliente HTTP.".into(),
    };

    // 1. Intentar llamar a LFM 2.5 local en GPU (:8080)
    let sys_msg = format!("Eres Sentinel AI en modo {mode}. Responde de forma clara, técnica y concisa.");
    let lfm_req = serde_json::json!({
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.3
    });

    if let Ok(resp) = client.post("http://127.0.0.1:8080/v1/chat/completions").json(&lfm_req).send() {
        if resp.status().is_success() {
            if let Ok(val) = resp.json::<serde_json::Value>() {
                if let Some(choices) = val.get("choices").and_then(|c| c.as_array()) {
                    if let Some(first) = choices.first() {
                        if let Some(msg) = first.get("message") {
                            let content = msg.get("content").and_then(|c| c.as_str()).unwrap_or("").trim();
                            if !content.is_empty() {
                                return content.to_string();
                            }
                            let reasoning = msg.get("reasoning_content").and_then(|c| c.as_str()).unwrap_or("").trim();
                            if !reasoning.is_empty() {
                                return reasoning.to_string();
                            }
                        }
                    }
                }
            }
        }
    }

    // 2. Fallback al Neocórtex clásico (:8000)
    let legacy_req = AIQueryRequest {
        prompt: prompt.to_string(),
        mode: mode.to_lowercase(),
        max_tokens: 512,
        temperature: 0.4,
    };

    match client.post("http://localhost:8000/api/ai/query").json(&legacy_req).send() {
        Ok(resp) => {
            if let Ok(ai_resp) = resp.json::<AIQueryResponse>() {
                ai_resp.response
            } else {
                "Error: No pude decodificar el pensamiento del Cortex.".into()
            }
        }
        Err(_) => "Error de conexión: Ni LFM (:8080) ni Neocórtex (:8000) están respondiendo.".into(),
    }
}

// --- UI ---

fn draw_ui(f: &mut Frame, app: &mut App) {
    let area = f.area();
    let layout = Layout::default()
        .direction(Direction::Vertical)
        .constraints(
            [
                Constraint::Length(3),
                Constraint::Min(0),
                Constraint::Length(4),
            ]
            .as_ref(),
        )
        .split(area);

    draw_top_tabs(f, layout[0], app);

    match app.view {
        View::Observatory => draw_observatory_view(f, layout[1], app),
        View::Dialogue => draw_dialogue_view(f, layout[1], app),
        View::Orchestrator => draw_orchestrator_view(f, layout[1], app),
        View::Factory => draw_factory_view(f, layout[1], app),
        View::Hacker => draw_hacker_view(f, layout[1], app),
    }

    draw_shell_input(f, layout[2], app);
}

fn draw_top_tabs(f: &mut Frame, area: Rect, app: &mut App) {
    let tabs_titles = [
        "[1] OBSERVE",
        "[2] DIALOG",
        "[3] SWARM",
        "[4] FACTORY",
        "[5] HACKER",
    ];
    let curr = match app.view {
        View::Observatory => 0,
        View::Dialogue => 1,
        View::Orchestrator => 2,
        View::Factory => 3,
        View::Hacker => 4,
    };

    let tabs = Tabs::new(
        tabs_titles
            .iter()
            .map(|t| Line::from(*t))
            .collect::<Vec<_>>(),
    )
    .block(
        Block::default()
            .borders(Borders::ALL)
            .border_type(BorderType::Rounded)
            .title(" 🛡️ SENTINEL VID BRIDGE v8.5 "),
    )
    .select(curr)
    .style(Style::default().fg(Color::DarkGray))
    .highlight_style(Style::default().fg(VID_CYAN).add_modifier(Modifier::BOLD));

    f.render_widget(tabs, area);
}

fn draw_shell_input(f: &mut Frame, area: Rect, app: &mut App) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Length(22), Constraint::Min(0)].as_ref())
        .split(area);

    let p_color = match app.persona.as_str() {
        "HACKER" => Color::Red,
        "MASTER" => NEON_GREEN,
        "CREATOR" => Color::Magenta,
        _ => VID_CYAN,
    };

    let icon = match app.persona.as_str() {
        "HACKER" => "󰒃",
        "MASTER" => "󱚧",
        "CREATOR" => "󰕧",
        _ => "",
    };

    let p_box = Paragraph::new(format!(" {} {}", icon, app.persona))
        .style(Style::default().fg(p_color).add_modifier(Modifier::BOLD))
        .block(
            Block::default()
                .borders(Borders::ALL)
                .border_type(BorderType::Double),
        );
    f.render_widget(p_box, chunks[0]);

    let input_style = if app.input_mode == InputMode::Insert {
        Style::default().fg(Color::Yellow)
    } else {
        Style::default().fg(Color::DarkGray)
    };
    let input_text = if app.is_asking_ai {
        format!(" ... ANALIZANDO EN EL NEOCÓRTEX ... [{}]", app.input)
    } else {
        format!(
            " {} > {}",
            if app.input_mode == InputMode::Insert {
                "INSERT"
            } else {
                "NORMAL"
            },
            app.input
        )
    };

    let input_content = if app.input_mode == InputMode::Insert && !app.prediction.is_empty() {
        Line::from(vec![
            Span::raw(input_text),
            Span::styled(
                format!(" {}", app.prediction),
                Style::default()
                    .fg(Color::DarkGray)
                    .add_modifier(Modifier::ITALIC),
            ),
        ])
    } else {
        Line::from(input_text)
    };

    let input = Paragraph::new(input_content).style(input_style).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Neural Interface (SPA) - [TAB] to accept prediction "),
    );
    f.render_widget(input, chunks[1]);
}

fn draw_observatory_view(f: &mut Frame, area: Rect, app: &mut App) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(32), Constraint::Percentage(68)].as_ref())
        .split(area);

    let left = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Length(8), Constraint::Min(0)].as_ref())
        .split(chunks[0]);

    let spark_data = app.energy_history.iter().cloned().collect::<Vec<_>>();
    let spark = Sparkline::default()
        .block(Block::default().borders(Borders::ALL).title(" FLUJO DE ENERGÍA "))
        .data(&spark_data)
        .style(Style::default().fg(NEON_GREEN));
    f.render_widget(spark, left[0]);

    let stats = vec![
        Line::from(vec![
            Span::raw("Coherence: "),
            Span::styled(format!("{}", app.coherence), Style::default().fg(VID_CYAN)),
        ]),
        Line::from(vec![
            Span::raw("Entropy:   "),
            Span::styled(format!("{}", app.entropy), Style::default().fg(Color::Red)),
        ]),
    ];
    let stats_p = Paragraph::new(stats).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" QUANTUM CORE "),
    );
    f.render_widget(stats_p, left[1]);

    let lattice = Block::default()
        .borders(Borders::ALL)
        .title(" MYCNET SYNAPTIC LATTICE (RUST) ");
    let inner = lattice.inner(chunks[1]);
    f.render_widget(lattice, chunks[1]);

    let cx = (inner.x + inner.width / 2) as i32;
    let cy = (inner.y + inner.height / 2) as i32;
    for (coord, node) in &app.net.nodes {
        let sx = cx + (2 * coord.q + coord.r) * 2;
        let sy = cy + coord.r;
        if sx >= inner.x as i32
            && sx < (inner.x + inner.width) as i32
            && sy >= inner.y as i32
            && sy < (inner.y + inner.height) as i32
        {
            let color = if node.amplitude > SPA::new(1, 0, 0, 0, 0) {
                Color::Red
            } else if node.amplitude > SPA::new(0, 40, 0, 0, 0) {
                Color::Yellow
            } else {
                Color::DarkGray
            };
            f.buffer_mut()
                .set_string(sx as u16, sy as u16, "⬢", Style::default().fg(color));
        }
    }
}

fn draw_dialogue_view(f: &mut Frame, area: Rect, app: &mut App) {
    let items: Vec<ListItem> = app
        .chat_history
        .iter()
        .map(|(sender, msg)| {
            let color = if sender == "YOU" {
                GHOST_WHITE
            } else {
                VID_CYAN
            };
            ListItem::new(vec![
                Line::from(vec![
                    Span::styled(
                        format!("{}> ", sender),
                        Style::default().fg(color).add_modifier(Modifier::BOLD),
                    ),
                    Span::raw(msg),
                ]),
                Line::from(" "),
            ])
        })
        .collect();
    let chat = List::new(items).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" NEURAL DIALOGUE (REPL) "),
    );
    f.render_widget(chat, area);
}

fn draw_orchestrator_view(f: &mut Frame, area: Rect, app: &mut App) {
    let items: Vec<ListItem> = app
        .swarm
        .iter()
        .map(|a| {
            ListItem::new(format!(
                "🤖 {} [{}] -> Load: {}% | Status: {}",
                a.name, a.role, a.load, a.status
            ))
        })
        .collect();
    let list = List::new(items).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" AGENT SWARM "),
    );
    f.render_widget(list, area);
}

fn draw_factory_view(f: &mut Frame, area: Rect, app: &mut App) {
    for job in &app.factory {
        let g = Gauge::default()
            .block(
                Block::default()
                    .borders(Borders::ALL)
                    .title(format!(" 🎬 YT FACTORY: {} [{}] ", job.title, job.stage)),
            )
            .percent(job.progress);
        f.render_widget(g, area);
    }
}

fn draw_hacker_view(f: &mut Frame, area: Rect, app: &mut App) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(50), Constraint::Percentage(50)].as_ref())
        .split(area);

    let logs: Vec<ListItem> = app
        .log_events
        .iter()
        .map(|s| {
            let color = if s.contains("ALERT") {
                Color::Red
            } else if s.contains("ALLOW") {
                NEON_GREEN
            } else {
                Color::Blue
            };
            ListItem::new(Line::from(vec![Span::styled(
                s,
                Style::default().fg(color),
            )]))
        })
        .collect();
    let list = List::new(logs).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" KERNEL RING-BUFFER "),
    );
    f.render_widget(list, chunks[0]);

    let info = vec![
        Line::from(" 󰒃 CLAWDBOT BRIDGE: ACTIVE"),
        Line::from(format!(
            "  WhatsApp Status: {}",
            if app.clawd_online {
                "ONLINE"
            } else {
                "OFFLINE"
            }
        )),
        Line::from(""),
        Line::from("  DEBIAN OPTIMIZATION"),
        Line::from("  - CPU Isolation: Core 2,3"),
        Line::from("  - Power Mode: LEVITATION (SPA)"),
        Line::from(""),
        Line::from(Span::styled(
            " [ARMED] DEEP_GUARDIAN_MODE ",
            Style::default()
                .fg(Color::Red)
                .add_modifier(Modifier::REVERSED),
        )),
    ];
    let p = Paragraph::new(info).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" SECURITY & CLAWBOT "),
    );
    f.render_widget(p, chunks[1]);
}
