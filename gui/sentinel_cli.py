#!/home/jnovoas/proyectos/sentinel/.venv/bin/python3
"""
Sentinel CLI - Command-line interface for quick queries
Complements the TUI for direct command-line usage

Usage:
    sentinel-cli "analyze system logs"
    sentinel-cli --agent security "check for vulnerabilities"
    sentinel-cli --verify "some data to verify with TruthSync"
    sentinel-cli --status  # Show system status
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# Add backend to path (repo root is one level above gui/)
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.safe_ollama import SafeOllamaClient
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import httpx


console = Console()


class SentinelCLI:
    """Command-line interface for Sentinel AI"""
    
    def __init__(self):
        self.ollama = SafeOllamaClient(base_url="http://localhost:11434")
        self.backend_url = "http://localhost:8000"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def query(self, question: str, agent: str = None) -> None:
        """Ask Sentinel AI a question"""
        
        # Build agent-specific prompt
        agent_context = ""
        if agent == "security":
            agent_context = "\n\nYou are a security expert. Focus on Guardian integration, threat detection, and eBPF security."
        elif agent == "devops":
            agent_context = "\n\nYou are a DevOps expert. Focus on system administration, Docker, and infrastructure."
        elif agent == "quantum":
            agent_context = "\n\nYou are a quantum physics expert. Focus on Base-60 math, ZPE, and quantum simulations."
        
        system_prompt = (
            "You are Sentinel AI, an advanced system administration assistant. "
            "Provide concise, accurate, and actionable responses. "
            "When suggesting commands, explain security implications."
            f"{agent_context}"
        )
        
        full_prompt = f"{system_prompt}\n\nUser: {question}\n\nAssistant:"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🤔 Thinking...", total=None)
            
            try:
                response = await self.ollama.generate(
                    model="llama3.2:3b",
                    prompt=full_prompt
                )
                
                progress.remove_task(task)
                
                ai_response = response.get("response", "")
                sanitization = response.get("sanitization", {})
                
                # Display response
                console.print()
                console.print(Panel(
                    Markdown(ai_response),
                    title="🤖 Sentinel AI",
                    border_style="green",
                    padding=(1, 2)
                ))
                
                # Show metadata if sanitized
                if sanitization:
                    threat_level = sanitization.get("threat_level", "safe")
                    if threat_level != "safe":
                        console.print(f"\n⚠️  Threat Level: {threat_level}", style="yellow")
                        patterns = sanitization.get("patterns_detected", [])
                        if patterns:
                            console.print(f"Patterns: {', '.join(patterns)}", style="dim")
                
            except Exception as e:
                progress.remove_task(task)
                console.print(f"\n❌ Error: {str(e)}", style="red")
    
    async def verify(self, data: str) -> None:
        """Verify data with TruthSync"""
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🔍 Verifying with TruthSync...", total=None)
            
            try:
                response = await self.client.post(
                    f"{self.backend_url}/api/v1/truthsync/verify",
                    json={"data": data, "timestamp": datetime.utcnow().isoformat()}
                )
                
                progress.remove_task(task)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    console.print()
                    if result.get("verified"):
                        console.print("✅ TruthSync Verification: PASSED", style="green bold")
                    else:
                        console.print("❌ TruthSync Verification: FAILED", style="red bold")
                    
                    # Show details
                    table = Table(title="Verification Details")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value", style="white")
                    
                    for key, value in result.items():
                        table.add_row(key, str(value))
                    
                    console.print(table)
                else:
                    console.print(f"\n❌ TruthSync unavailable (HTTP {response.status_code})", style="red")
                    
            except Exception as e:
                progress.remove_task(task)
                console.print(f"\n❌ Error: {str(e)}", style="red")
    
    async def status(self) -> None:
        """Show Sentinel system status"""
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("📊 Fetching system status...", total=None)
            
            try:
                # Get health status
                health_response = await self.client.get(f"{self.backend_url}/api/v1/health")
                
                # Get metrics
                metrics_response = await self.client.get(
                    f"{self.backend_url}/api/v1/analytics/statistics?hours=1"
                )
                
                progress.remove_task(task)
                
                if health_response.status_code == 200:
                    health = health_response.json()
                    
                    console.print()
                    console.print(Panel.fit(
                        "🛡️ Sentinel System Status",
                        style="bold cyan"
                    ))
                    
                    # Create status table
                    table = Table(show_header=True, header_style="bold magenta")
                    table.add_column("Component", style="cyan", width=20)
                    table.add_column("Status", width=15)
                    table.add_column("Details", style="dim")
                    
                    # System status
                    status = health.get("status", "unknown")
                    status_style = "green" if status == "healthy" else "red"
                    table.add_row(
                        "System",
                        f"[{status_style}]{status.upper()}[/{status_style}]",
                        f"Uptime: {health.get('uptime', 'N/A')}"
                    )
                    
                    # Guardian status
                    guardian = health.get("guardian", {})
                    guardian_active = guardian.get("active", False)
                    guardian_style = "green" if guardian_active else "yellow"
                    table.add_row(
                        "Guardian",
                        f"[{guardian_style}]{'ACTIVE' if guardian_active else 'INACTIVE'}[/{guardian_style}]",
                        f"eBPF hooks: {guardian.get('hooks', 0)}"
                    )
                    
                    # TruthSync status
                    truthsync = health.get("truthsync", {})
                    truthsync_ok = truthsync.get("available", False)
                    truthsync_style = "green" if truthsync_ok else "yellow"
                    table.add_row(
                        "TruthSync",
                        f"[{truthsync_style}]{'AVAILABLE' if truthsync_ok else 'UNAVAILABLE'}[/{truthsync_style}]",
                        f"Verified: {truthsync.get('verified_count', 0)}"
                    )
                    
                    # Cortex status
                    cortex = health.get("cortex", {})
                    cortex_ok = cortex.get("running", False)
                    cortex_style = "green" if cortex_ok else "yellow"
                    table.add_row(
                        "Cortex",
                        f"[{cortex_style}]{'RUNNING' if cortex_ok else 'STOPPED'}[/{cortex_style}]",
                        f"Decisions: {cortex.get('decisions', 0)}"
                    )
                    
                    console.print(table)
                    
                    # Show metrics if available
                    if metrics_response.status_code == 200:
                        metrics = metrics_response.json()
                        
                        console.print()
                        console.print("📈 System Metrics (Last Hour)", style="bold yellow")
                        
                        metrics_table = Table(show_header=False)
                        metrics_table.add_column("Metric", style="cyan")
                        metrics_table.add_column("Value", style="white")
                        
                        if "cpu" in metrics:
                            metrics_table.add_row("CPU Average", f"{metrics['cpu'].get('avg', 0):.1f}%")
                        if "memory" in metrics:
                            metrics_table.add_row("Memory Average", f"{metrics['memory'].get('avg', 0):.1f}%")
                        if "anomalies_count" in metrics:
                            metrics_table.add_row("Anomalies Detected", str(metrics.get('anomalies_count', 0)))
                        
                        console.print(metrics_table)
                else:
                    console.print(f"\n❌ Backend unavailable (HTTP {health_response.status_code})", style="red")
                    
            except Exception as e:
                progress.remove_task(task)
                console.print(f"\n❌ Error: {str(e)}", style="red")
                console.print("\n💡 Make sure Sentinel backend is running:", style="yellow")
                console.print("   docker-compose up -d backend", style="dim")
    
    async def close(self):
        """Cleanup"""
        await self.ollama.close()
        await self.client.aclose()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Sentinel CLI - AI-powered system administration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sentinel-cli "analyze system logs"
  sentinel-cli --agent security "check for vulnerabilities"
  sentinel-cli --verify "data to verify"
  sentinel-cli --status
        """
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Question to ask Sentinel AI"
    )
    
    parser.add_argument(
        "--agent",
        choices=["security", "devops", "quantum"],
        help="Deploy specific agent"
    )
    
    parser.add_argument(
        "--verify",
        metavar="DATA",
        help="Verify data with TruthSync"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status"
    )
    
    args = parser.parse_args()
    
    cli = SentinelCLI()
    
    try:
        if args.status:
            await cli.status()
        elif args.verify:
            await cli.verify(args.verify)
        elif args.query:
            await cli.query(args.query, agent=args.agent)
        else:
            parser.print_help()
            console.print("\n💡 Tip: Use 'sentinel-tui' for interactive mode", style="cyan")
    finally:
        await cli.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\n👋 Goodbye!", style="cyan")
        sys.exit(0)
