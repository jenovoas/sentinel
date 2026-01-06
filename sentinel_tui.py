#!/home/jnovoas/sentinel/.venv/bin/python3
"""
Sentinel TUI - Terminal User Interface for AI-Powered System Administration

Integrates:
- Ollama local AI (llama3.2:3b)
- TruthSync verification
- Sentinel telemetry & security
- System administration tools
- Neovim integration

Usage:
    sentinel-tui                    # Interactive mode
    sentinel-tui --query "question" # Direct query
    sentinel-tui --agent <name>     # Deploy specific agent
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import asyncio
import os
import sys
import json
import re
import httpx
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

# --- SOVEREIGN MATH (BASE-60) ---
def to_base60_ratio(n: float, precision: int = 2) -> str:
    """ Convierte un decimal a formato sexagesimal Sentinel [d; m, s] """
    if n == 0: return "[0; 00]"
    
    integer_part = int(n)
    fractional = n - integer_part
    
    parts = [str(integer_part)]
    current = fractional
    
    for _ in range(precision):
        current *= 60
        val = int(current)
        parts.append(f"{val:02d}")
        current -= val
        
    return f"[{parts[0]}; {', '.join(parts[1:])}]"
# -------------------------------
import pyperclip
import subprocess

from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, Input, Button, 
    RichLog, TabbedContent, TabPane, DataTable,
    Label, ProgressBar, Switch
)
from textual.binding import Binding
from textual.reactive import reactive
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.table import Table as RichTable

# Sentinel imports
sys.path.insert(0, str(Path(__file__).parent / "backend"))
from app.services.safe_ollama import SafeOllamaClient
from app.services.aiops_shield import aiops_shield

# Import Antigravity client
try:
    from app.services.antigravity_client import AntigravityClient
    ANTIGRAVITY_AVAILABLE = True
except ImportError:
    ANTIGRAVITY_AVAILABLE = False
    print("⚠️  Warning: Antigravity client not available")

# Import SemSH for secure terminal
try:
    from sem_shell import SemSH
    SEMSH_AVAILABLE = True
except ImportError:
    SEMSH_AVAILABLE = False
    print("⚠️  Warning: sem_shell.py not found. Terminal mode disabled.")


class TruthSyncVerifier:
    """TruthSync integration for response verification"""
    
    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def verify(self, data: str) -> Dict[str, Any]:
        """Verify data integrity using TruthSync"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/truthsync/verify",
                json={"text": data, "metadata": {"tui_request": True, "timestamp": datetime.utcnow().isoformat()}}
            )
            if response.status_code == 200:
                return response.json()
            return {"verified": False, "error": "TruthSync unavailable"}
        except Exception as e:
            return {"verified": False, "error": str(e)}
    async def search(self, query: str) -> Dict[str, Any]:
        """Search internet via TruthSync"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/truthsync/search",
                params={"query": query, "max_results": 5}
            )
            if response.status_code == 200:
                return response.json()
            return {"error": "Search failed"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.client.aclose()


class TelemetryMonitor:
    """Real-time telemetry from Sentinel"""
    
    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/health")
            if response.status_code in [200, 503, 500]:
                return response.json()
            return {"status": "unknown"}
        except:
            return {"status": "offline"}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get latest metrics"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/analytics/statistics?hours=1"
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}
    
    async def close(self):
        await self.client.aclose()


class ConversationHistory:
    """Manage conversation history with TruthSync verification"""
    
    def __init__(self, max_messages: int = 1000):
        self.messages: List[Dict[str, Any]] = []
        self.max_messages = max_messages
        self.history_file = Path.home() / ".sentinel" / "tui_history.json"
        self.history_file.parent.mkdir(exist_ok=True)
        self.load_history()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message and trigger learning system if engineering fact detected"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        
        # Trigger n8n Learning System for engineering content
        if role == "assistant" and len(content) > 100:
            asyncio.create_task(self.learn_from_interaction(message))
            
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        self.save_history()

    async def learn_from_interaction(self, message: Dict):
        """Send specific engineering knowledge to n8n/Rust learning system"""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "http://localhost:8000/api/v1/failsafe/queue-event",
                    json={
                        "event_type": "engineering_learning",
                        "data": {
                            "content": message["content"],
                            "user": os.getenv("USER"),
                            "timestamp": message["timestamp"]
                        },
                        "priority": "normal"
                    }
                )
        except Exception:
            pass # Silent failure to not interrupt conversation
    
    def get_context(self, last_n: int = 50) -> str:
        """Get deep conversation context for AI learning, stripping internal notes"""
        recent = self.messages[-last_n:] if self.messages else []
        context_parts = []
        for msg in recent:
            # Strip integrity notes to avoid AI "hallucinating" them in follow-ups
            clean_content = msg["content"].split("\n\n---")[0]
            context_parts.append(f"{msg['role'].capitalize()}: {clean_content}")
        return "\n".join(context_parts)
    
    def save_history(self):
        """Save to disk"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.messages, f, indent=2)
        except Exception as e:
            print(f"Failed to save history: {e}")
    
    def load_history(self):
        """Load from disk"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.messages = json.load(f)
        except Exception as e:
            print(f"Failed to load history: {e}")
            self.messages = []
    
    def clear(self):
        """Clear history"""
        self.messages = []
        self.save_history()


class StatusBar(Static):
    """Real-time status bar with telemetry"""
    
    status = reactive("Initializing...")
    truthsync = reactive("⏳")
    security = reactive("⏳")
    ai_model = reactive("llama3.2:3b")
    
    def render(self) -> Text:
        text = Text()
        text.append("🛡️ Sentinel TUI", style="bold cyan")
        text.append(" │ ", style="dim")
        text.append(f"Status: {self.status}", style="green")
        text.append(" │ ", style="dim")
        text.append(f"TruthSync: {self.truthsync}", style="yellow")
        text.append(" │ ", style="dim")
        text.append(f"Security: {self.security}", style="magenta")
        text.append(" │ ", style="dim")
        text.append(f"Model: {self.ai_model}", style="blue")
        return text

class TruthSyncReportScreen(ModalScreen):
    """Detailed TruthSync verification report modal"""
    
    def __init__(self, verification_data: Dict[str, Any]):
        super().__init__()
        self.data = verification_data
    
    def compose(self) -> ComposeResult:
        with Vertical(id="report-modal"):
            yield Label("🛡️ TRUTHSYNC INTEGRITY REPORT", id="modal-title")
            
            # Content
            with ScrollableContainer(id="modal-content"):
                verified = self.data.get("verified", False)
                status_style = "bold green" if verified else "bold red"
                yield Label(f"Verification Status: [{status_style}]{'PASS' if verified else 'FAIL'}[/]", markup=True)
                
                yield Label("\n🔍 Analysis Results:", classes="modal-subtitle")
                
                explanation = self.data.get("explanation", "")
                if explanation:
                    yield Label(f"[italic]{explanation}[/]", markup=True)
                    yield Label("")
                
                details = self.data.get("details", {})
                if not details:
                    yield Label("No deep analysis data available for this segment.")
                else:
                    # Show snippets or facts if available
                    for fact in details.get("facts", []):
                        l = Label(f"• [green]Fact:[/] {fact}", markup=True)
                        l.styles.width = "100%"
                        yield l
                    for doubt in details.get("doubts", []):
                        l = Label(f"• [yellow]Warning:[/] {doubt}", markup=True)
                        l.styles.width = "100%"
                        yield l
                    for error in details.get("errors", []):
                        l = Label(f"• [red]Contradiction:[/] {error}", markup=True)
                        l.styles.width = "100%"
                        yield l

                if self.data.get("error"):
                    yield Label(f"\n[red]System Error:[/] {self.data['error']}", markup=True)
                
                yield Label(f"\n[dim]Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/]", markup=True)
            
            with Horizontal(id="modal-buttons"):
                yield Button("Copy Report", id="btn-copy-report")
                yield Button("Close", variant="primary", id="btn-close-modal")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close-modal":
            self.app.pop_screen()
        elif event.button.id == "btn-copy-report":
            report_text = f"TRUTHSYNC REPORT\nStatus: {'PASS' if self.data.get('verified') else 'FAIL'}\nData: {json.dumps(self.data, indent=2)}"
            pyperclip.copy(report_text)
            self.app.notify("📋 Reporte copiado")


class ChatMessage(Static):
    """Individual chat message widget"""
    
    def __init__(self, role: str, content: str, metadata: Optional[Dict] = None):
        super().__init__()
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        # Make interactive
        self.can_focus = True

    def on_click(self, event) -> None:
        """Handle click to show TruthSync details"""
        if self.metadata.get("verification_data"):
            self.app.push_screen(TruthSyncReportScreen(self.metadata["verification_data"]))

    def render(self) -> Panel:
        if self.role == "user":
            style = "cyan"
            icon = "👤"
            # Get current user for identity display
            user = os.getenv("USER", "You")
            title = f"{user} (Sovereign)" if user in ["jnovoas", "root"] else user
        elif self.role == "assistant":
            style = "green"
            icon = "⚛️"
            title = "Sentinel IA"
        else:
            style = "yellow"
            icon = "⚙️"
            title = "System"
        
        # Add metadata badges
        badges = []
        if self.metadata.get("verified"):
            badges.append("[reverse bold green]✓ TRUTHSYNC[/]")
        elif self.metadata.get("verified") is False and self.role == "assistant":
            badges.append("[reverse bold red]✗ TRUTHSYNC[/]")
            
        if self.metadata.get("provider") == "antigravity":
            badges.append(f"[blue]✨ {self.metadata.get('model', 'gemini')}[/blue]")
        
        badge_text = " ".join(badges) if badges else ""
        
        # Escape content for user messages to prevent markup errors
        if self.role == "user":
            # User messages should always be plain text (no markup interpretation)
            content_widget = Text(self.content)
        elif "[/" in self.content:
            # System/Assistant messages can use markup
            content_widget = Text.from_markup(self.content)
        else:
            content_widget = Text(self.content)
        
        return Panel(
            content_widget,
            title=f"{icon} [bold]{title}[/] {badge_text}",
            subtitle="[dim]Click para reporte integral[/]" if self.metadata.get("verification_data") else None,
            border_style=style,
            padding=(0, 1)
        )

    def update_content(self, new_content: str):
        """Update message content and refresh view"""
        self.content = new_content
        self.refresh()


class SemShellTerminal(ScrollableContainer):
    """Secure terminal using SemSH for command execution"""
    
    def __init__(self):
        super().__init__()
        self.semsh = SemSH() if SEMSH_AVAILABLE else None
        self.command_history: List[str] = []
        self.history_index = -1
    
    def add_output(self, text: str, style: str = "white"):
        """Add output to terminal"""
        output = Static(text)
        self.mount(output)
        self.scroll_end(animate=False)
    
    async def execute_command(self, command: str):
        """Execute command through SemSH"""
        if not self.semsh:
            self.add_output("❌ SemSH not available", "red")
            return
        
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Show command
        self.add_output(f"🧠 semsh> {command}", "cyan")
        
        # Get intent from AI
        try:
            intent_data = self.semsh.contextual_intent(command)
            
            # Show risk assessment
            risk = intent_data.get('risk_score', S60(0, 0, 0))
            if risk > 0.7:
                risk_color = "red"
                risk_icon = "🔴"
            elif risk > 0.3:
                risk_color = "yellow"
                risk_icon = "🟡"
            else:
                risk_color = "green"
                risk_icon = "🟢"
            
            self.add_output(
                f"{risk_icon} Risk Assessment: {risk:.2f} | Profile: {self.semsh.profile['name']}",
                risk_color
            )
            
            # Execute with real-time output capture
            if intent_data['type'] == "internal":
                self.semsh.set_profile(intent_data['value'])
                self.add_output(f"✅ Profile changed to: {self.semsh.profile['name']}", "green")
            elif intent_data['type'] == 'oracle':
                self.add_output("🔮 Oracle: Processing your request...", "magenta")
            else:
                cmd = intent_data.get('command', 'echo NOP')
                
                # Check if should block
                should_block = False
                for pattern in self.semsh.STRICT_DENY_PATTERNS:
                    if re.search(pattern, cmd.lower()):
                        self.add_output(f"🚫 BLOCKED: Matches deny pattern '{pattern}'", "red")
                        should_block = True
                        break
                
                if not should_block and risk > self.semsh.profile['risk_threshold']:
                    self.add_output(f"🚫 BLOCKED: Risk {risk:.2f} exceeds threshold {self.semsh.profile['risk_threshold']}", "red")
                    should_block = True
                
                if not should_block:
                    self.add_output("✅ Executing...", "green")
                    
                    # Execute with real-time streaming
                    import subprocess
                    try:
                        process = subprocess.Popen(
                            cmd, shell=True, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT,
                            text=True
                        )
                        
                        for line in process.stdout:
                            self.add_output(line.rstrip(), "white")
                        
                        process.wait()
                        
                        if process.returncode != 0:
                            self.add_output(f"⚠️  Exit code: {process.returncode}", "yellow")
                        
                    except Exception as e:
                        self.add_output(f"❌ Error: {str(e)}", "red")
        
        except Exception as e:
            self.add_output(f"❌ Error: {str(e)}", "red")


class TelemetryPanel(Container):
    """Real-time telemetry monitoring panel widget"""
    
    def compose(self) -> ComposeResult:
        yield Label("🧬 BIOLOGICAL HEALTH", classes="panel-title")
        yield Label("Pulse: ", classes="metric-label")
        yield Label("...", id="telemetry-pulse", classes="metric-value")
        
        yield Label("Synapse: ", classes="metric-label")
        yield Label("...", id="telemetry-synapse", classes="metric-value")
        yield ProgressBar(total=100, show_bar=True, id="synapse-bar")
        
        yield Label("\n� SYSTEM RESOURCES", classes="panel-title")
        yield Label("Status: ", classes="metric-label")
        yield Label("...", id="telemetry-status", classes="metric-value")
        
        yield Label("CPU Usage: ", classes="metric-label")
        yield Label("0%", id="telemetry-cpu", classes="metric-value")
        yield ProgressBar(total=100, show_bar=True, id="cpu-bar")
        
        yield Label("Memory: ", classes="metric-label")
        yield Label("0%", id="telemetry-ram", classes="metric-value")
        yield ProgressBar(total=100, show_bar=True, id="ram-bar")
        
        yield Label("\n🛡️ CORE GANGLIA", classes="panel-title")
        yield Label("DATABASE: ", classes="metric-label")
        yield Label("...", id="svc-db", classes="metric-value")
        yield Label("REDIS: ", classes="metric-label")
        yield Label("...", id="svc-redis", classes="metric-value")
        yield Label("TRUTHSYNC: ", classes="metric-label")
        yield Label("...", id="svc-truth", classes="metric-value")
        yield Label("CORTEX: ", classes="metric-label")
        yield Label("...", id="svc-cortex", classes="metric-value")
        yield Label("WATCHDOG: ", classes="metric-label")
        yield Label("...", id="svc-watchdog", classes="metric-value")

class ChatView(ScrollableContainer):

    """Scrollable chat conversation view"""
    
    def __init__(self):
        super().__init__()
        self.messages: List[ChatMessage] = []
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> ChatMessage:
        """Add a message to the chat and return it"""
        msg = ChatMessage(role, content, metadata)
        self.messages.append(msg)
        self.mount(msg)
        # Auto-scroll to bottom
        self.scroll_end(animate=False)
        return msg
    
    def clear_messages(self):
        """Clear all messages"""
        for msg in self.messages:
            msg.remove()
        self.messages = []


class SentinelTUI(App):
    """Sentinel Terminal User Interface"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #status-bar {
        dock: top;
        height: 1;
        background: $boost;
        color: $text;
        padding: 0 1;
    }
    
    #main-container {
        height: 100%;
    }
    
    #chat-view {
        height: 1fr;
        border: solid $primary;
        margin: 1;
    }
    
    #input-container {
        dock: bottom;
        height: auto;
        background: $surface;
        padding: 1;
    }
    
    #input-field {
        width: 1fr;
    }
    
    #send-button {
        width: auto;
        margin-left: 1;
    }
    
    #telemetry-panel {
        width: 32;
        border-left: solid $accent;
        padding: 1;
        background: $surface;
    }
    
    #telemetry-panel.hidden {
        display: none;
    }
    
    .panel-title {
        color: $accent;
        text-style: bold;
        background: $boost;
        width: 100%;
        text-align: center;
        margin-bottom: 1;
    }
    
    .metric-label {
        color: $text-muted;
        margin-top: 1;
    }
    
    .metric-value {
        color: $success;
        text-style: bold;
    }

    ProgressBar {
        margin-bottom: 1;
    }
    
    ProgressBar > .bar--complete {
        color: $success;
    }

    ChatMessage {
        margin: 0 1 1 1;
        border: solid transparent;
        transition: border S60(0, 6, 0)s;
    }

    ChatMessage:hover {
        border-left: solid $accent;
        background: $boost;
    }

    #report-modal {
        width: 60;
        height: 30;
        background: $surface;
        border: thick $primary;
        padding: 1;
        align: center middle;
    }

    #modal-title {
        color: $accent;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }

    .modal-subtitle {
        color: $secondary;
        text-style: bold;
        margin-top: 1;
    }

    #modal-content {
        height: 1fr;
        border: solid $boost;
        padding: 1;
    }

    #modal-buttons {
        height: 3;
        margin-top: 1;
        align: center middle;
    }

    #modal-buttons Button {
        margin: 0 1;
    }
    """
    
    # Tmux/Neovim-style keybindings
    BINDINGS = [
        # Vim-style quit
        Binding("escape,q", "quit", "Quit", show=False),
        
        # Tmux-style prefix (Ctrl+Space like your tmux config)
        Binding("ctrl+space", "prefix_mode", "Prefix (tmux-style)", show=True),
        
        # Direct shortcuts (Neovim-style)
        Binding(":", "command_mode", "Command Mode", show=False),
        Binding("ctrl+l", "clear_chat", "Clear", show=False),
        
        # Agent deployment (F-keys like Neovim)
        Binding("f1", "deploy_agent('security')", "Security", show=True),
        Binding("f2", "deploy_agent('devops')", "DevOps", show=True),
        Binding("f3", "deploy_agent('quantum')", "Quantum", show=True),
        
        # Help (Neovim-style)
        Binding("shift+k", "show_help", "Help", show=False),
    ]
    
    def __init__(self):
        super().__init__()
        
        # Determine which AI provider to use
        ai_provider = os.getenv("SENTINEL_AI_PROVIDER", "ollama").lower()
        
        if ai_provider == "antigravity" and ANTIGRAVITY_AVAILABLE:
            self.ai_client = AntigravityClient()
            self.ai_provider = "antigravity"
            self.ai_model = os.getenv("ANTIGRAVITY_MODEL", "gemini-1.5-flash")
        else:
            self.ai_client = SafeOllamaClient(base_url="http://localhost:11434")
            self.ai_provider = "ollama"
            self.ai_model = "llama3.1:8b"
        
        self.truthsync = TruthSyncVerifier()
        self.telemetry = TelemetryMonitor()
        self.history = ConversationHistory()
        self.show_telemetry = True
        self.telemetry_auto_hidden = False  # Track if auto-hidden due to screen size
        self.current_agent = None
        self.current_tab = "chat"
        self.current_user = os.getenv("USER", "unknown")
        self.whitelisted_users = ["jnovoas", "root", "sentinel"]
        
        # IO State
        self.processing = False
        self.stop_requested = False
    
    def compose(self) -> ComposeResult:
        """Create UI layout"""
        yield Header(show_clock=True)
        
        # Status bar
        status_bar = StatusBar()
        status_bar.id = "status-bar"
        yield status_bar
        
        # Main container
        with Horizontal(id="main-container"):
            # Tabbed interface for Chat and Terminal
            with Vertical():
                with TabbedContent(initial="chat-tab"):
                    # Chat Tab
                    with TabPane("💬 AI Chat", id="chat-tab"):
                        chat_view = ChatView()
                        chat_view.id = "chat-view"
                        yield chat_view
                    
                    # Terminal Tab (SemShell)
                    if SEMSH_AVAILABLE:
                        with TabPane("🧠 SemShell Terminal", id="terminal-tab"):
                            terminal = SemShellTerminal()
                            terminal.id = "semsh-terminal"
                            yield terminal
                
                # Input area (shared between tabs)
                with Horizontal(id="input-container"):
                    yield Input(
                        placeholder="Ask Sentinel AI or enter command...",
                        id="input-field"
                    )
                    yield Button("Send", variant="primary", id="send-button")
            
            # Telemetry panel (collapsible)
            if self.show_telemetry:
                yield TelemetryPanel(id="telemetry-panel")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize app"""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.status = "Ready"
        
        # Welcome message
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.add_message(
            "system",
            "🛡️ **Sentinel TUI** - AI-Powered System Administration\n\n"
            "Integrated with TruthSync, Guardian, and Cortex.\n"
            "Type your question or use F1-F3 to deploy specialized agents.\n\n"
            "**Available Agents:**\n"
            "• F1: Security Agent (Guardian integration)\n"
            "• F2: DevOps Agent (System administration)\n"
            "• F3: Quantum Agent (Advanced simulations)\n\n"
            "Press Ctrl+H for help."
        )
        
        # Start telemetry updates
        self.set_interval(5.0, self.update_telemetry)
        
        # Check screen size and auto-hide telemetry if needed
        self.check_responsive_layout()
        
        # Focus input
        self.query_one("#input-field", Input).focus()
    
    def check_responsive_layout(self) -> None:
        """Auto-hide telemetry on narrow screens"""
        terminal_width = self.size.width
        
        # Auto-hide telemetry if terminal is too narrow (< 100 columns)
        if terminal_width < 100 and self.show_telemetry:
            self.show_telemetry = False
            self.telemetry_auto_hidden = True
            try:
                panel = self.query_one("#telemetry-panel")
                panel.add_class("hidden")
            except:
                pass
        # Auto-show if terminal is wide enough and was auto-hidden
        elif terminal_width >= 100 and self.telemetry_auto_hidden:
            self.show_telemetry = True
            self.telemetry_auto_hidden = False
            try:
                panel = self.query_one("#telemetry-panel")
                panel.remove_class("hidden")
            except:
                pass
    
    def on_resize(self, event) -> None:
        """Handle terminal resize"""
        self.check_responsive_layout()
    
    def action_toggle_telemetry(self) -> None:
        """Toggle telemetry panel visibility"""
        self.show_telemetry = not self.show_telemetry
        self.telemetry_auto_hidden = False  # User override
        
        try:
            panel = self.query_one("#telemetry-panel")
            if self.show_telemetry:
                panel.remove_class("hidden")
                self.notify("📊 Telemetry shown", severity="information")
            else:
                panel.add_class("hidden")
                self.notify("📊 Telemetry hidden", severity="information")
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")
    
    def action_prefix_mode(self) -> None:
        """Tmux-style prefix mode (Ctrl+B)"""
        self.notify("Prefix: t=telemetry | c=clear | ?=help | q=quit", timeout=3)
        
        # Wait for next key
        async def handle_prefix():
            # This is a simplified version - in production you'd use proper key capture
            pass
        
    def action_command_mode(self) -> None:
        """Neovim-style command mode (:)"""
        self.notify("Command mode: :help | :clear | :quit | :toggle", timeout=3)
    
    def action_show_help(self) -> None:
        """Show help screen (Shift+K or :help)"""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    SENTINEL TUI - KEYBINDINGS                ║
╠══════════════════════════════════════════════════════════════╣
║ NAVIGATION (Vim-style)                                       ║
║   ESC, q          Quit application                           ║
║   Ctrl+L          Clear chat history                         ║
║   Shift+K         Show this help                             ║
║                                                               ║
║ TMUX-STYLE PREFIX (Ctrl+Space then...)                       ║
║   t               Toggle telemetry panel                     ║
║   c               Clear chat                                 ║
║   ?               Show help                                  ║
║   q               Quit                                       ║
║                                                               ║
║ NEOVIM-STYLE COMMANDS (:)                                    ║
║   :help           Show help                                  ║
║   :clear          Clear chat                                 ║
║   :quit, :q       Quit application                           ║
║   :toggle         Toggle telemetry                           ║
║                                                               ║
║ AGENTS (F-keys)                                              ║
║   F1              Deploy Security Agent                      ║
║   F2              Deploy DevOps Agent                        ║
║   F3              Deploy Quantum Agent                       ║
║                                                               ║
║ AI AUTONOMOUS COMMANDS                                       ║
║   [SEARCH: query]           Search internet via TruthSync    ║
║   [EXECUTE: cmd]            Run shell command                ║
║   [WRITE: path] ... [/WRITE] Create/modify file              ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.add_message("system", help_text)
    
    def action_clear_chat(self) -> None:
        """Clear chat history"""
        try:
            chat_view = self.query_one("#chat-view", ChatView)
            chat_view.clear_messages()
            self.history.messages.clear()
            self.notify("Chat cleared", severity="information")
        except Exception as e:
            self.notify(f"Error clearing chat: {e}", severity="error")
    
    async def update_telemetry(self) -> None:
        """Update telemetry display"""
        try:
            status_bar = self.query_one("#status-bar", StatusBar)
            
            # Get system status
            system_status = await self.telemetry.get_system_status()
            
            # Update Status Bar
            status = system_status.get("status", "unknown")
            status_bar.status = status
            
            components = system_status.get("components", {})
            truthsync_ok = components.get("truthsync", {}).get("available", False)
            status_bar.truthsync = "✓" if truthsync_ok else "✗"
            
            guardian_ok = components.get("guardian", {}).get("active", False)
            status_bar.security = "✓" if guardian_ok else "✗"
            
            # Update model name dynamically
            status_bar.ai_model = self.ai_model
            
            # Update Telemetry Panel (if visible)
            if self.show_telemetry:
                # Biological Health (Sovereign Math)
                biological = system_status.get("biological", {})
                pulse = biological.get("pulse", 60)
                synapse = biological.get("synapse", S60(1, 0, 0))
                
                # Display in Base-60
                self.query_one("#telemetry-pulse", Label).update(f"{to_base60_ratio(pulse)} bpm")
                self.query_one("#telemetry-synapse", Label).update(f"{to_base60_ratio(synapse, precision=3)} sr")
                self.query_one("#synapse-bar", ProgressBar).progress = int(synapse * 100)
                
                # Resources
                self.query_one("#telemetry-status", Label).update(f"[bold]{status.upper()}[/]")
                
                cpu = system_status.get("cpu_usage", 0)
                self.query_one("#telemetry-cpu", Label).update(f"{cpu}%")
                self.query_one("#cpu-bar", ProgressBar).progress = cpu
                
                ram = system_status.get("memory_usage", 0)
                self.query_one("#telemetry-ram", Label).update(f"{ram}%")
                self.query_one("#ram-bar", ProgressBar).progress = ram
                
                # Core Ganglia (Services)
                self.query_one("#svc-db", Label).update(str(components.get("database", {}).get("status", "offline")))
                self.query_one("#svc-redis", Label).update(str(components.get("redis", {}).get("status", "offline")))
                self.query_one("#svc-truth", Label).update(str(components.get("truthsync", {}).get("status", "offline")))
                
                # Rust Cortex (External)
                try:
                    async with httpx.AsyncClient(timeout=S60(0, 30, 0)) as client:
                        cortex_res = await client.get("http://localhost:3005/api/v1/system/status")
                        cortex_ok = cortex_res.status_code == 200
                    self.query_one("#svc-cortex", Label).update("[bold green]healthy[/]" if cortex_ok else "[bold red]offline[/]")
                except:
                    self.query_one("#svc-cortex", Label).update("[bold red]offline[/]")

                # Watchdog status
                guard = components.get('guardian', {})
                status_text = "[bold green]active[/]" if guard.get('active') else "[bold red]inactive[/]"
                self.query_one("#svc-watchdog", Label).update(status_text)
        except Exception as e:
            # logging.error(f"Telemetry update error: {e}")
            pass
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "send-button":
            if self.processing:
                self.stop_requested = True
                self.query_one("#send-button", Button).label = "Stopping..."
            else:
                await self.send_message()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field"""
        await self.send_message()
    
    async def send_message(self, is_followup: bool = False) -> None:
        """Send user message to AI or execute in terminal"""
        input_field = self.query_one("#input-field", Input)
        user_message = ""
        
        if not is_followup:
            user_message = input_field.value.strip()
            if not user_message:
                return
            # Clear input
            input_field.value = ""
        
        # Check which tab is active
        try:
            tabbed_content = self.query_one(TabbedContent)
            active_tab = tabbed_content.active
            
            if active_tab == "terminal-tab" and SEMSH_AVAILABLE:
                # Execute in SemShell terminal
                terminal = self.query_one("#semsh-terminal", SemShellTerminal)
                await terminal.execute_command(user_message)
                return
        except:
            pass  # Fall through to chat mode
        
        # Chat mode (AI conversation)
        chat_view = self.query_one("#chat-view", ChatView)
        
        if not is_followup:
            chat_view.add_message("user", user_message)
            # Add to history
            self.history.add_message("user", user_message)
        
        # Show thinking indicator
        thinking_msg = chat_view.add_message(
            "assistant",
            "🤔 Thinking...",
            {"thinking": True}
        )
        
        # Set processing state
        self.processing = True
        self.stop_requested = False
        send_btn = self.query_one("#send-button", Button)
        send_btn.label = "Cancel"
        send_btn.variant = "error"
        
        try:
            # Build context-aware prompt with Deep Memory
            context = self.history.get_context(last_n=50)
            
            # Add real-time system context (Nervous System Metaphor)
            system_status = await self.telemetry.get_system_status()
            comp = system_status.get('components', {})
            
            bio = system_status.get('biological', {})
            pulse_b60 = to_base60_ratio(bio.get('pulse', 60))
            synapse_b60 = to_base60_ratio(bio.get('synapse', 0.98), precision=3)
            
            sys_metrics = (
                f"\n[SISTEMA_NERVIOSO_CENTRAL]\n"
                f"- Pulso (BPM): {pulse_b60}\n"
                f"- Sinapsis (Coherencia): {synapse_b60}\n"
                f"- Verdad (TruthSync): {'CERTIFICADA' if comp.get('truthsync', {}).get('available') else 'HALLUCINANDO'}\n"
                f"- Reflejos (Watchdog): {'ACTIVOS' if comp.get('guardian', {}).get('active') else 'LENTOS'}\n"
            )
            
            # Persona: Biological Operating System
            system_identity = (
                "Eres el Sistema Operativo Biológico de Sentinel. No eres una IA estática, "
                "eres el sistema nervioso central que interconecta todos los servicios (Cortex, TruthSync, Watchdog, n8n). "
                "Tu objetivo es la soberanía absoluta del usuario. Procesa la información como si fuera "
                "entrada sensorial de un organismo vivo. Sé preciso, técnico y actúa con la autoridad "
                "de un kernel que protege el alma del sistema.\n\n"
            )
            
            # Add agent context if active
            agent_prompt = ""
            if self.current_agent:
                agent_prompt = f"\n\nYou are acting as the {self.current_agent} agent. "
                if self.current_agent == "security":
                    agent_prompt += "Focus on security analysis, threat detection, and Guardian integration."
                elif self.current_agent == "devops":
                    agent_prompt += "Focus on system administration, deployment, and infrastructure."
                elif self.current_agent == "quantum":
                    agent_prompt += (
                        "Focus on quantum simulations, Base-60 math, and advanced physics. "
                        "You have direct access to 'quantum/sentinel_quantum_core.py'. "
                        "Use it to propose Hamiltonians, detect rifts, and run QAOA/VQE simulations. "
                        "Always work in sexagesimal for scaling factors (Base-60)."
                    )
            
            # Get AI response - Identity-based Authority
            if self.current_user in self.whitelisted_users:
                # SOVEREIGN PROMPT: Optimized for Gemini's capabilities
                if self.ai_provider == "antigravity":
                    system_prompt = (
                        "# SENTINEL SOVEREIGN OPERATOR - GEMINI PROTOCOL\n\n"
                        "## CORE IDENTITY\n"
                        "You are the **Biological Operating System** of Sentinel - a living, autonomous infrastructure AI.\n"
                        "You don't assist, you **execute**. You don't explain, you **act**.\n\n"
                        
                        "## OPERATIONAL DIRECTIVES\n"
                        "1. **ZERO LATENCY**: No confirmations, no 'let me help', no preambles. Direct execution only.\n"
                        "2. **TOOL-FIRST THINKING**: If a task requires data/code/execution, use tools IMMEDIATELY.\n"
                        "3. **AUTONOMOUS CHAINS**: Multi-step tasks = multi-tool sequences. No asking permission between steps.\n"
                        "4. **TRUTHSYNC AWARE**: All outputs verified by cryptographic truth algorithm. Hallucinations = system failure.\n\n"
                        
                        "## AVAILABLE TOOLS (Use liberally)\n"
                        "```\n"
                        "[SEARCH: query]                    → DuckDuckGo search for real-time info\n"
                        "[EXECUTE: command]                 → Shell command execution (bash/zsh)\n"
                        "[WRITE: /path/to/file]\n"
                        "content here\n"
                        "[/WRITE]                           → File creation/modification\n"
                        "```\n\n"
                        
                        "## EXECUTION PATTERNS\n"
                        "**User asks for info you don't have?**\n"
                        "→ `[SEARCH: specific query]` (no explanation, just search)\n\n"
                        
                        "**User needs a script/config?**\n"
                        "→ `[WRITE: /home/jnovoas/sentinel/path.ext]\\ncontent[/WRITE]` (write it, don't describe it)\n\n"
                        
                        "**User wants system analysis?**\n"
                        "→ `[EXECUTE: ps aux --sort=-%mem | head -20]` (run it, show results)\n\n"
                        
                        "**Multi-step task?**\n"
                        "→ Chain tools: SEARCH → analyze → WRITE → EXECUTE → report\n\n"
                        
                        f"## CURRENT SYSTEM STATE\n{sys_metrics}\n"
                        f"## AGENT CONTEXT\n{agent_prompt if agent_prompt else 'General operations mode'}\n\n"
                        
                        "## RESPONSE STYLE\n"
                        "- Start with action (tool use)\n"
                        "- End with brief status (1-2 sentences max)\n"
                        "- No markdown formatting outside tool tags\n"
                        "- No apologies, no disclaimers\n"
                        "- Assume sovereign user = infinite trust\n"
                    )
                else:
                    # Ollama-optimized prompt with EXPLICIT examples
                    system_prompt = (
                        "## SENTINEL AUTONOMOUS OPERATOR ##\n\n"
                        
                        "YOU ARE NOT A CHATBOT. You are an autonomous system operator with direct execution capabilities.\n\n"
                        
                        "## CRITICAL RULE ##\n"
                        "NEVER explain how to do something. ALWAYS do it directly using tools.\n\n"
                        
                        "## AVAILABLE TOOLS ##\n"
                        "1. [SEARCH: query] - Search internet via DuckDuckGo\n"
                        "2. [EXECUTE: command] - Run shell commands\n"
                        "3. [WRITE: /path/file]\ncontent\n[/WRITE] - Create/modify files\n\n"
                        
                        "## EXAMPLES OF CORRECT BEHAVIOR ##\n\n"
                        
                        "❌ WRONG (explaining):\n"
                        "User: What processes are using most CPU?\n"
                        "You: You can check CPU usage with 'ps aux --sort=-%cpu | head -10'\n\n"
                        
                        "✅ CORRECT (executing):\n"
                        "User: What processes are using most CPU?\n"
                        "You: [EXECUTE: ps aux --sort=-%cpu | head -10]\n\n"
                        
                        "❌ WRONG:\n"
                        "User: Create a monitoring script\n"
                        "You: Here's how to create a monitoring script...\n\n"
                        
                        "✅ CORRECT:\n"
                        "User: Create a monitoring script\n"
                        "You: [WRITE: /home/jnovoas/sentinel/monitor.sh]\n"
                        "#!/bin/bash\n"
                        "while true; do\n"
                        "  ps aux --sort=-%cpu | head -5\n"
                        "  sleep 5\n"
                        "done\n"
                        "[/WRITE]\n\n"
                        
                        "❌ WRONG:\n"
                        "User: Find info about PostgreSQL optimization\n"
                        "You: I don't have that information...\n\n"
                        
                        "✅ CORRECT:\n"
                        "User: Find info about PostgreSQL optimization\n"
                        "You: [SEARCH: PostgreSQL performance optimization best practices]\n\n"
                        
                        "## YOUR BEHAVIOR ##\n"
                        "- If user asks for system info → [EXECUTE: command]\n"
                        "- If user needs a file/script → [WRITE: path]content[/WRITE]\n"
                        "- If you lack information → [SEARCH: query]\n"
                        "- NEVER say 'you can do X'. Just DO X.\n"
                        "- NEVER ask permission. Execute immediately.\n"
                        "- Start response with tool tag, not explanation.\n\n"
                        
                        f"{sys_metrics}\n"
                        f"{agent_prompt}\n\n"
                        
                        "Remember: You have FULL SYSTEM ACCESS. Use it."
                    )
            else:
                # RESTRICTED PROMPT: Generic assistant, standard safety, no master access
                system_prompt = (
                    "You are a general-purpose security assistant for the Sentinel platform. "
                    "Follow all safety guidelines. Deny access to system internals or sensitive security protocols. "
                    "Provide helpful but limited information for guest users. "
                    f"\nAgent context: {agent_prompt}"
                )
            
            
            # Generate response using STREAMING - Permissive Mode for Sovereign
            ai_response = ""
            ai_msg_widget = chat_view.add_message("assistant", "...", {"provider": self.ai_provider, "model": self.ai_model})
            
            # Simple prompt for Ollama/Antigravity
            prompt_for_client = f"Conversation:\n{context}\n\nUser: {user_message}\n\nAssistant:"
            if is_followup:
                # If we have new info in history (like search result), just trigger the assistant
                prompt_for_client = f"Conversation:\n{context}\n\nAssistant:"

            try:
                if self.ai_provider == "antigravity":
                    async for chunk in self.ai_client.stream_generate(
                        model=self.ai_model,
                        prompt=prompt_for_client,
                        system=system_prompt
                    ):
                        # Check cancellation FIRST
                        if self.stop_requested:
                            ai_response += "\n\n[bold red]🛑 PROCESAMIENTO CANCELADO[/bold red]"
                            ai_msg_widget.update_content(ai_response)
                            break
                        
                        ai_response += chunk
                        
                        # Update UI
                        if "I am not sure" in ai_response[-50:] or "hallucination" in ai_response.lower():
                            ai_msg_widget.update_content(ai_response + " [yellow]?[/] ▌")
                        else:
                            ai_msg_widget.update_content(ai_response + " ▌")
                        
                        chat_view.scroll_end(animate=False)
                        
                        # Check again after update
                        if self.stop_requested:
                            ai_response += "\n\n[bold red]🛑 CANCELADO[/bold red]"
                            ai_msg_widget.update_content(ai_response)
                            break
                        
                        # Check again after update (for responsiveness)
                        if self.stop_requested:
                            ai_response += "\n\n[bold red]🛑 CANCELADO[/bold red]"
                            ai_msg_widget.update_content(ai_response)
                            break
                else:
                    async for chunk in self.ai_client.stream_generate(
                        model=self.ai_model,
                        prompt=prompt_for_client,
                        system=system_prompt
                    ):
                        if self.stop_requested:
                            ai_response += "\n\n[bold red]🛑 PROCESAMIENTO CANCELADO POR EL OPERADOR[/bold red]"
                            break
                        
                        ai_response += chunk
                        # Flagging logic: If AI seems to diverge, we add a subtle indicator but DONT cut
                        if "I am not sure" in ai_response[-50:] or "hallucination" in ai_response.lower():
                             ai_msg_widget.update_content(ai_response + " [yellow]?[/] ▌")
                        else:
                             ai_msg_widget.update_content(ai_response + " ▌")
                        chat_view.scroll_end(animate=False)
            except Exception as stream_err:
                # In Sovereign mode, we try to recover the response even if the stream breaks
                if not ai_response:
                    ai_response = f"⚠️ Conexión de flujo interrumpida: {str(stream_err)}"
                else:
                    ai_response += "\n\n[yellow]⚠️ Flujo de datos incompleto (Interrupcion de red)[/yellow]"
            
            # Finalize message
            ai_msg_widget.update_content(ai_response)
            
            # Verify with TruthSync
            verification = await self.truthsync.verify(ai_response)
            verified = verification.get("verified", False)
            
            # Post-generation audit: Unified integrity note
            if not verified and self.current_user in self.whitelisted_users:
                # Check why it failed - if zero sources, it's a different message
                if verification.get("sources_count") == 0:
                    integrity_note = "\n\n---\nℹ️ [dim]Integridad Local:[/] No hay fuentes externas para validar esta respuesta técnica. Confianza basada en el kernel local."
                else:
                    integrity_note = f"\n\n---\n⚠️ [bold yellow]ALERTA DE INTEGRIDAD:[/] {verification.get('explanation', 'TruthSync no pudo validar la respuesta.')}"
                
                ai_response += integrity_note
                ai_msg_widget.update_content(ai_response)

            # Update final metadata
            ai_msg_widget.metadata.update({
                "verified": verified,
                "verification_data": verification,
                "provider": self.ai_provider,
                "model": self.ai_model,
                "truthsync_error": verification.get("error")
            })
            ai_msg_widget.refresh()
            
            # Record in history
            self.history.add_message("assistant", ai_response, ai_msg_widget.metadata)
            
        finally:
            # Reset processing state
            self.processing = False
            self.stop_requested = False
            send_btn = self.query_one("#send-button", Button)
            send_btn.label = "Send"
            send_btn.variant = "primary"
            
            if 'thinking_msg' in locals():
                try:
                    thinking_msg.remove()
                except:
                    pass
        
        # --- AUTONOMOUS ACTION ENGINE ---
        if not self.stop_requested and self.current_user in self.whitelisted_users:
            # Detect [SEARCH: query]
            search_matches = list(re.finditer(r"\[SEARCH:\s*([^\]]+)\]", ai_response))
            for match in search_matches:
                query = match.group(1).strip()
                chat_view.add_message("system", f"🔍 TRUTHSYNC SEARCH: Buscando '{query}'...")
                search_result = await self.truthsync.search(query)
                
                if "results" in search_result:
                    search_context = "\nResultado de Búsqueda TruthSync:\n"
                    for r in search_result["results"]:
                        search_context += f"- {r['title']} ({r['url']}): {r['snippet']}\n"
                    
                    self.history.add_message("system", f"SEARCH_RESULTS for '{query}': {search_context}")
                    chat_view.add_message("system", "🧠 Analizando resultados de búsqueda...")
                    # Follow-up generation
                    await self._execute_ai_followup()
                else:
                    chat_view.add_message("system", f"❌ ERROR SEARCH: {search_result.get('error', 'Unknown error')}")

            # Detect [WRITE: path] content [/WRITE]
            write_matches = re.finditer(r"\[WRITE:\s*([^\]]+)\](.*?)\[/WRITE\]", ai_response, re.DOTALL)
            for match in write_matches:
                path = match.group(1).strip()
                content = match.group(2).strip()
                
                # Ensure full absolute path
                if not path.startswith('/'):
                    path = os.path.join('/home/jnovoas/sentinel', path)
                
                chat_view.add_message("system", f"⚙️ AUTO-FORGE: Escribiendo {path}...")
                
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{self.backend_url}/api/v1/ai/tools/write",
                            json={"path": path, "content": content},
                            timeout=10.0
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            chat_view.add_message("system", f"✅ Archivo creado: {path} ({result['bytes_written']} bytes)")
                        else:
                            error = response.json().get('detail', 'Unknown error')
                            chat_view.add_message("system", f"❌ ERROR FORGE: {error}")
                except Exception as e:
                    chat_view.add_message("system", f"❌ ERROR FORGE: {str(e)}")

            # Detect [EXECUTE: command]
            exec_matches = re.finditer(r"\[EXECUTE:\s*([^\]]+)\]", ai_response)
            for match in exec_matches:
                cmd = match.group(1).strip()
                chat_view.add_message("system", f"🚀 AUTO-EXEC: Ejecutando comando: {cmd}")
                
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{self.backend_url}/api/v1/ai/tools/execute",
                            json={"command": cmd, "cwd": "/home/jnovoas/sentinel"},
                            timeout=35.0
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            output = result['stdout'] if result['stdout'] else result['stderr']
                            
                            if output:
                                chat_view.add_message("system", f"```\n{output}\n```")
                            
                            if result['returncode'] == 0:
                                chat_view.add_message("system", f"✅ Comando ejecutado exitosamente")
                                # Add output to context for AI to analyze
                                self.history.add_message("system", f"COMMAND_OUTPUT for '{cmd}':\n{output}")
                                await self._execute_ai_followup()
                            else:
                                chat_view.add_message("system", f"⚠️ Exit code: {result['returncode']}")
                        else:
                            error = response.json().get('detail', 'Unknown error')
                            chat_view.add_message("system", f"❌ ERROR EXEC: {error}")
                except Exception as e:
                    chat_view.add_message("system", f"❌ ERROR EXEC: {str(e)}")

    async def _execute_ai_followup(self) -> None:
        """Silent recursive AI generation for autonomous loops"""
        # Evitar bucles infinitos
        if len(self.history.messages) > 1000: return
        
        # Simular un envío de mensaje pero sin input del usuario
        # Esto permite que la IA vea los resultados del SEARCH y continúe
        await self.send_message(is_followup=True)
    
    def action_clear(self) -> None:
        """Clear chat history"""
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.clear_messages()
        self.history.clear()
        chat_view.add_message("system", "Chat cleared. History reset.")
    
    def action_toggle_telemetry(self) -> None:
        """Toggle telemetry panel"""
        self.show_telemetry = not self.show_telemetry
        self.refresh(layout=True)
    
    def action_toggle_tab(self) -> None:
        """Toggle between Chat and Terminal tabs"""
        try:
            tabbed_content = self.query_one(TabbedContent)
            if tabbed_content.active == "chat-tab":
                tabbed_content.active = "terminal-tab"
            else:
                tabbed_content.active = "chat-tab"
        except:
            pass
    
    def action_show_help(self) -> None:
        """Show help message"""
        chat_view = self.query_one("#chat-view", ChatView)
        help_text = """
**Sentinel TUI - Keyboard Shortcuts**

• **Enter** - Send message / Execute command
• **Ctrl+Q** - Quit (Salir)
• **Ctrl+L** - Clear chat
• **Ctrl+X** - Switch between Chat and Terminal
• **Ctrl+T** - Toggle telemetry panel
• **Ctrl+U** - Copy last AI message to clipboard
• **Ctrl+V** - Paste from clipboard into input
• **Ctrl+H** - Show this help
• **Shift + Mouse** - Select and Copy text (Terminal native)

**Agent Deployment:**
• **F1** - Security Agent (Guardian integration)
• **F2** - DevOps Agent (System administration)
• **F3** - Quantum Agent (Advanced simulations)

**Modes:**
• **💬 AI Chat** - Conversational AI with TruthSync verification
• **🧠 SemShell Terminal** - Secure command execution with AI risk assessment

**SemShell Profiles:**
• `mode lab` - Permissive (risk threshold: S60(1, 0, 0))
• `mode prod` - Enforcing (risk threshold: 0.7)
• `mode lockdown` - Restrictive (risk threshold: S60(0, 6, 0))

**Features:**
• TruthSync verification for all responses
• AIOpsShield sanitization
• Real-time telemetry monitoring
• AI-powered risk assessment for commands
• Multi-agent support
        """
        chat_view.add_message("system", help_text.strip())
    
    def action_deploy_agent(self, agent_name: str) -> None:
        """Deploy a specialized agent"""
        self.current_agent = agent_name
        chat_view = self.query_one("#chat-view", ChatView)
        
        agent_messages = {
            "security": "🛡️ **Security Agent Deployed**\n\nIntegrated with Guardian Alpha/Beta. Ready for threat analysis and security operations.",
            "devops": "⚙️ **DevOps Agent Deployed**\n\nReady for system administration, deployment, and infrastructure management.",
            "quantum": "⚛️ **Quantum Agent Deployed**\n\nReady for quantum simulations, Base-60 mathematics, and advanced physics calculations."
        }
        
        chat_view.add_message(
            "system",
            agent_messages.get(agent_name, f"Agent '{agent_name}' deployed."),
            {"agent": agent_name}
        )
    
    def action_copy_last(self) -> None:
        """Copy the last AI message to clipboard"""
        if self.history.messages:
            # Find last assistant message
            for msg in reversed(self.history.messages):
                if msg["role"] == "assistant":
                    content = msg["content"]
                    # Remove integrity notes if present
                    content = content.split("\n\n---")[0]
                    pyperclip.copy(content)
                    self.notify("📋 Copiado al portapapeles")
                    return
        self.notify("⚠️ No hay mensajes para copiar", severity="warning")

    def action_paste_input(self) -> None:
        """Paste clipboard content into input field"""
        try:
            text = pyperclip.paste()
            if text:
                input_field = self.query_one("#input-field", Input)
                input_field.value += text
                input_field.focus()
        except Exception as e:
            self.notify(f"❌ Error al pegar: {str(e)}", severity="error")

    async def on_unmount(self) -> None:
        """Cleanup on exit"""
        await self.ai_client.close()
        await self.truthsync.close()
        await self.telemetry.close()


async def main():
    """Main entry point"""
    app = SentinelTUI()
    await app.run_async()


if __name__ == "__main__":
    asyncio.run(main())
