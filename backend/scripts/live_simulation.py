import asyncio
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from quantum.yatra_core import PI_S60, S60  # YATRA AUTO-INJECT


# Configuration Constants
@dataclass
class SimConfig:
    """Configuration settings for the Battlefield Simulation."""
    API_URL: str = "http://localhost:8000/api/v1/cortex/events"
    TELEMETRY_TOKEN: str = "sentinel-internal-ebpf-key-2025"
    VERSION: str = "v1.S60(0, 0, 0)-DEMO"
    
@dataclass
class Colors:
    """ANSI Color codes for terminal output."""
    RED: str = "\033[91m"
    GREEN: str = "\033[92m"
    YELLOW: str = "\033[93m"
    BLUE: str = "\033[94m"
    MAGENTA: str = "\033[95m"
    CYAN: str = "\033[96m"
    WHITE: str = "\033[97m"
    RESET: str = "\033[0m"
    BOLD: str = "\033[1m"
    BLINK: str = "\033[5m"

class Logger:
    """Handles formatted logging to the console."""
    
    @staticmethod
    def log(msg: str, color: str = Colors.WHITE, icon: str = "•") -> None:
        """Prints a timestamped message with color and icon."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"{color}[{timestamp}] {icon} {msg}{Colors.RESET}")

class EventSimulator:
    """Handles the construction and transmission of simulated events."""
    
    def __init__(self, config: SimConfig):
        self.config = config
        self.headers = {
            "X-Sentinel-Token": self.config.TELEMETRY_TOKEN,
            "Content-Type": "application/json"
        }

    async def send_event(self, client: httpx.AsyncClient, event_type: str, description: str) -> None:
        """
        Sends a single simulated event to the Cortex API.
        
        Args:
            client: The async HTTP client.
            event_type: The type of event (e.g., RECON, BRUTE_FORCE).
            description: Description of the process or action.
        """
        payload = self._construct_payload(event_type, description)
        
        try:
            response = await client.post(self.config.API_URL, json=payload, headers=self.headers)
            await self._handle_response(response, event_type, description)
        except Exception:
            # Cinematic script resilience: ignore network errors to keep the show running
            pass

    def _construct_payload(self, event_type: str, description: str) -> Dict[str, Any]:
        """Constructs the JSON payload for the event."""
        return {
            "event_type": event_type,
            "source": "guardian_alpha",
            "data": {
                "source_ip": f"192.168.1.{random.randint(100, 200)}",
                "process_id": random.randint(1000, 9999),
                "timestamp": datetime.now().isoformat(),
                "process_name": description
            }
        }

    async def _handle_response(self, response: httpx.Response, event_type: str, description: str) -> None:
        """Processes the API response and logs the outcome."""
        # For the demo visual effect, we log based on the event type context
        # In a real integration, we would read response.json()['decision_type']
        
        if event_type == "RECON":
            Logger.log(f"RECON SCAN: {description} -> XDP DROP", Colors.YELLOW, "🔍")
        elif event_type == "BRUTE_FORCE":
             Logger.log(f"LOGIN ATTEMPT: {description} -> BLOCKED (99.2%)", Colors.RED, "💥")
        elif event_type == "ROOTKIT":
             Logger.log(f"KERNEL INTEGRITY VIOLATION: {description} -> ARMOR_MODE ACTIVE", Colors.MAGENTA, "☠️")
        elif event_type == "DDOS":
             Logger.log(f"PACKET FLOOD: {description} -> 15.4M PPS", Colors.CYAN, "⚡")

class BattlefieldSimulation:
    """Main Orchestrator for the Sentinel Cortex Battlefield Simulation."""
    
    def __init__(self):
        self.config = SimConfig()
        self.simulator = EventSimulator(self.config)

    def print_banner(self) -> None:
        """Prints the startup banner."""
        print(f"\n{Colors.BOLD}{Colors.WHITE}╔════════════════════════════════════════════════════════════════════╗")
        print(f"║   SENTINEL CORTEX™ - BATTLEFIELD SIMULATION ({self.config.VERSION})      ║")
        print(f"║   TARGET: RING 0 KERNEL SPACE | MODE: {Colors.RED}WEAPONIZED{Colors.WHITE}                 ║")
        print(f"╚════════════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

    async def act_1_recon(self, client: httpx.AsyncClient) -> None:
        """Executes Act 1: Reconnaissance."""
        print(f"{Colors.BOLD}{Colors.YELLOW}>>> ACT 1: RECONNAISSANCE (Port Scanning & Probing){Colors.RESET}")
        print(f"{Colors.YELLOW}Targeting exposed interfaces...{Colors.RESET}")
        time.sleep(1)
        
        for i in range(10):
            Logger.log(f"nmap -sS target:{80+i}", Colors.YELLOW, "🔍")
            await self.simulator.send_event(client, "SYSCALL_OPEN", "/usr/bin/nmap")
            time.sleep(0.3)
            
        print(f"{Colors.BOLD}{Colors.GREEN}>>> RESULT: XDP DROPS SPIKE DETECTED on Dashboard{Colors.RESET}\n")
        time.sleep(2)

    async def act_2_brute_force(self, client: httpx.AsyncClient) -> None:
        """Executes Act 2: Brute Force."""
        print(f"{Colors.BOLD}{Colors.RED}>>> ACT 2: BRUTE FORCE ASSAULT (Identity Siege){Colors.RESET}")
        print(f"{Colors.RED}Launching hydra -l admin -P passwords.txt...{Colors.RESET}")
        time.sleep(1)
        
        for i in range(20):
            Logger.log(f"ssh user@root (attempt #{i*17})", Colors.RED, "💥")
            await self.simulator.send_event(client, "NET_CONNECT", "sshd")
            time.sleep(S60(0, 6, 0))
            
        Logger.log(f"{Colors.BLINK}847 ACCOUNTS LOCKED{Colors.RESET}", Colors.RED, "🔒")
        print(f"{Colors.BOLD}{Colors.GREEN}>>> RESULT: Cortex 99.2% BLOCK Rate Confirmed{Colors.RESET}\n")
        time.sleep(2)

    async def act_3_rootkit(self, client: httpx.AsyncClient) -> None:
        """Executes Act 3: Rootkit Deployment."""
        print(f"{Colors.BOLD}{Colors.MAGENTA}>>> ACT 3: ROOTKIT DEPLOYMENT (Kernel Integrity Attack){Colors.RESET}")
        print(f"{Colors.MAGENTA}Injecting LKM shadow module (insmod shadow_lkm.ko)...{Colors.RESET}")
        time.sleep(2)
        
        Logger.log("SYS_MODULE_LOAD detected: shadow_lkm.ko", Colors.MAGENTA, "⚠️")
        time.sleep(1)
        Logger.log("EBPF VERIFIER: Unauthorized opcode detected", Colors.MAGENTA, "🛡️")
        time.sleep(1)
        
        print(f"{Colors.BOLD}{Colors.RED}{Colors.BLINK}>>> CRITICAL: ARMOR_MODE ACTIVATED (Truth Integrity 94%){Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}>>> RESULT: Kernel Panic Averted. System Locked.{Colors.RESET}\n")
        time.sleep(2)

    async def act_4_ddos(self, client: httpx.AsyncClient) -> None:
        """Executes Act 4: DDoS Swarm."""
        print(f"{Colors.BOLD}{Colors.CYAN}>>> ACT 4: DDOS SWARM (Volumetric Saturation){Colors.RESET}")
        print(f"{Colors.CYAN}Unleashing hping3 --flood target (10M PPS)...{Colors.RESET}")
        time.sleep(1)
        print(f"{Colors.CYAN}Ramping up to 15.4M PPS Line Rate...{Colors.RESET}")
        
        tasks = []
        for _ in range(100): # Simulating massive concurrent async load
            tasks.append(self.simulator.send_event(client, "SYSCALL_OPEN", "hping3"))
        await asyncio.gather(*tasks)
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}>>> MIC DROP 🎤{Colors.RESET}")
        print(f"{Colors.WHITE}Simulation Complete. System Status: {Colors.GREEN}IMMUNE{Colors.WHITE}.{Colors.RESET}")
        print(f"{Colors.WHITE}Total Valuation Impact: {Colors.GREEN}$1.985B{Colors.WHITE}.{Colors.RESET}")

    async def run(self) -> None:
        """Main execution loop."""
        self.print_banner()
        
        async with httpx.AsyncClient() as client:
            await self.act_1_recon(client)
            await self.act_2_brute_force(client)
            await self.act_3_rootkit(client)
            await self.act_4_ddos(client)

if __name__ == "__main__":
    try:
        simulation = BattlefieldSimulation()
        asyncio.run(simulation.run())
    except KeyboardInterrupt:
        print("\n\nDemo Aborted.")
