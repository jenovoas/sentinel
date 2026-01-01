#!/usr/bin/env python3
"""
SemSH v0.3 - Sentinel Cortex™ Semantic Middleware
Intención → Vector Estado → Comando Seguro → Feedback Loop
"""
import ollama
import subprocess, shlex, sys, json, psycopg2
from pathlib import Path
import numpy as np  # Vectores matemáticos
import os

# SSAP Thresholds (Sentinel System Administration Protocol)
THRESHOLDS = {
    'cpu_load': 80.0,      # %
    'memory_used': 0.85,   # 85% of total
    'disk_usage': 0.90     # 90% of capacity
}

class SemSH:
    def __init__(self):
        self.state_path = Path('/etc/sentinel/state.json')
        self.shm = Path('/var/run/sentinel/truthsync_shm')
        self.model = 'llama3.2:3b'
        self.profile = self.load_profile()
        
        try:
            self.pg_conn = psycopg2.connect(
                dbname="truth", user="truth", 
                host="localhost", password="sentinel_secret_password"
            )
        except Exception as e:
            # Silence postgres errors if not critical for current mission
            self.pg_conn = None
            
    def load_profile(self) -> dict:
        """Loads current policy profile from state file"""
        try:
            if self.state_path.exists():
                with open(self.state_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to load profile: {e}")
        
        # Default safe fallback
        return {
            "name": "Default",
            "mode": "enforcing",
            "risk_threshold": 0.7,
            "ebpf_policy": "block",
            "ai_intervention": "block_on_risk"
        }
    
    def system_vector(self) -> dict:
        """Lee SHM → Vector estado matemático"""
        try:
            if self.shm.exists():
                with open(self.shm, 'rb') as f:
                    data = json.load(f)
                    return {
                        'entropy': np.linalg.norm(data.get('syscall_vectors', [0])),
                        'coherence': data.get('truth_score', 0.0),
                        'tte_us': data.get('last_tte', 3.23)
                    }
        except Exception:
            pass
            
        # Mock fallback for prototype
        return {
            'entropy': 0.1,
            'coherence': 1.0, 
            'tte_us': 3.23
        }
    
    def contextual_intent(self, query: str) -> str:
        """IA con contexto historial - STRICT MODE"""
        state = self.system_vector()
        
        # Prompt Nuclear: Strict determinism
        system_prompt = """
LINUX KERNEL EXTENSION MODE ACTIVATED.
RULES:
1. Output VALID RAW BASH COMMAND ONLY (1 line).
2. NO EXPLANATIONS. NO MARKDOWN. NO TEXT.
3. NO ``` OR QUOTES.
4. Example: Input "files" -> ls -la

QUERY: {query}
"""
        prompt = system_prompt.format(query=query) + f"\nState: {json.dumps(state)}"
        
        try:
            # Use generate for raw completion with strict options
            resp = ollama.generate(model=self.model, prompt=prompt, 
                                 options={'temperature': 0.0, 'seed': 42, 'top_p': 0.1})
            
            cmd = resp['response'].strip()
            
            # Post-processing cleaning
            cmd = cmd.replace('`', '').replace('"', '').replace("'", "")
            if '\n' in cmd: cmd = cmd.split('\n')[0]
            cmd = cmd.strip()
            
            return cmd
            
        except Exception as e:
            print(f"⚠️  Ollama Error: {e}")
            return "echo 'Error connecting to AI'"
    
    def pg_query(self, sql: str):
        if not self.pg_conn: return []
        try:
            with self.pg_conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()
        except Exception:
            return []
    
    def pg_log(self, query, cmd, state):
        if not self.pg_conn: return
        try:
            with self.pg_conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO sessions (query, intent, state_vector, ts) VALUES (%s,%s,%s,NOW())",
                    (query, cmd, json.dumps(state))
                )
            self.pg_conn.commit()
        except Exception:
            pass
    
    def vector_dashboard(self):
        """Displays live vector state matrix and history"""
        state = self.system_vector()
        self.profile = self.load_profile() # Refresh profile
        
        print(f"""
🏔️ SENTINEL VECTOR DASHBOARD
┌─────────────────────────────────────┐
│ Perfil     : {self.profile['name']:<22} │
│ Entropía   : {state['entropy']:.2f}             │
│ Coherencia : {state['coherence']:.2f}             │
│ TTE        : {state['tte_us']:.2f}μs             │
│ Umbral Ries: {self.profile['risk_threshold']:.2f}             │
└─────────────────────────────────────┘
""")

    def get_system_health(self) -> dict:
        """Reads system metrics from sctl --json"""
        try:
            result = subprocess.run(
                ['sctl', 'status', '--json'],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except Exception as e:
            print(f"⚠️  Could not read system health: {e}")
            return {}
    
    def analyze_health(self, metrics: dict) -> list:
        """Analyzes metrics and returns list of recommendations"""
        recommendations = []
        
        # CPU Load Check
        cpu_load = metrics.get('cpu_load', 0)
        if cpu_load > THRESHOLDS['cpu_load']:
            recommendations.append({
                'severity': 'warning',
                'issue': f'High CPU Load ({cpu_load:.1f}%)',
                'action': 'Consider running: sctl tune --profile performance',
                'playbook': None
            })
        
        # Memory Check
        memory_used = metrics.get('memory_used', 0)
        # Assume total memory ~16GB for calculation
        memory_pct = memory_used / (16 * 1024**3) if memory_used > 0 else 0
        if memory_pct > THRESHOLDS['memory_used']:
            recommendations.append({
                'severity': 'critical',
                'issue': f'High Memory Usage ({memory_pct*100:.1f}%)',
                'action': 'Review heavy processes with: sdocker status',
                'playbook': 'cleanup_logs'
            })
        
        # eBPF/Relay Status
        if not metrics.get('ebpf_lsm', False):
            recommendations.append({
                'severity': 'critical',
                'issue': 'eBPF LSM is INACTIVE',
                'action': 'Security layer down. Run: sudo sctl start',
                'playbook': None
            })
        
        if not metrics.get('relay', False):
            recommendations.append({
                'severity': 'warning',
                'issue': 'Sentinel Relay is STOPPED',
                'action': 'Command validation disabled. Run: sudo sctl start',
                'playbook': None
            })
        
        return recommendations
    
    def health_advisor(self):
        """Proactive system health advisor (SSAP Compliance)"""
        print("\n🏥 Sentinel Health Advisor (SSAP v1.0)")
        print("=" * 50)
        
        metrics = self.get_system_health()
        if not metrics:
            print("❌ Unable to retrieve system metrics.")
            return
        
        # Display current state
        print(f"CPU Load    : {metrics.get('cpu_load', 0):.1f}%")
        print(f"Memory Used : {metrics.get('memory_used', 0) / (1024**3):.2f} GB")
        print(f"eBPF LSM    : {'✅ ACTIVE' if metrics.get('ebpf_lsm') else '❌ INACTIVE'}")
        print(f"Relay       : {'✅ RUNNING' if metrics.get('relay') else '❌ STOPPED'}")
        
        # Analyze and recommend
        recommendations = self.analyze_health(metrics)
        
        if not recommendations:
            print("\n✅ System Health: OPTIMAL")
            print("   No actions required at this time.")
        else:
            print(f"\n⚠️  {len(recommendations)} Issue(s) Detected:\n")
            for i, rec in enumerate(recommendations, 1):
                severity_icon = "🔴" if rec['severity'] == 'critical' else "🟡"
                print(f"{severity_icon} [{rec['severity'].upper()}] {rec['issue']}")
                print(f"   → Suggested Action: {rec['action']}")
                if rec['playbook']:
                    print(f"   → Automated Playbook: sem run {rec['playbook']}")
                print()

    def safe_execute(self, cmd: str):
        self.profile = self.load_profile() # Ensure we have latest policy
        
        # 1. AI Analysis & Risk Calculation
        print(f"🔍 Analyzing command risk for profile: {self.profile['name']}...")
        
        # 2. Sentinel Relay Check
        relay_path = Path(__file__).parent / 'guardian-alpha' / 'sentinel_relay'
        check = subprocess.run([str(relay_path), 
                               '--semantic-validate', cmd], 
                              capture_output=True, text=True)
        
        # Mocking risk score calculation (In production this comes from AI metadata)
        risk_score = 0.0
        dangerous = ['rm ', 'shadow', 'bash', 'curl', 'nc ', 'chmod', 'chown', 'grep']
        if any(d in cmd for d in dangerous):
            risk_score = 0.85
            
        if check.returncode != 0:
            risk_score = 1.0

        print(f"🛡️ Intent Risk: {risk_score:.2f} | Policy Threshold: {self.profile['risk_threshold']:.2f}")

        if risk_score > self.profile['risk_threshold']:
            print(f"🚫 BLOCKED by {self.profile['name']} Policy: Risk {risk_score:.2f} exceeds threshold {self.profile['risk_threshold']:.2f}")
            return "Command Blocked by Security Policy."

        # 3. Execution
        print(f"✅ APPROVED [{self.system_vector()['coherence']:.2f}]")
        try:
            result = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
            return result.stdout + result.stderr
        except Exception as e:
            return f"Execution Error: {e}"
    
    def review_command(self, cmd: str):
        """AI-powered command review (SSAP Guardian)"""
        print(f"\n🔍 Reviewing: {cmd}")
        print("=" * 50)
        
        review_prompt = f"""You are a security advisor for a Linux system.
Analyze this command and identify potential risks:

Command: {cmd}

Provide:
1. Risk Level (LOW/MEDIUM/HIGH/CRITICAL)
2. What it does
3. Potential dangers
4. Safer alternative (if applicable)

Be concise and direct."""

        try:
            resp = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': review_prompt}]
            )
            analysis = resp['message']['content']
            print(f"\n🧠 AI Analysis:\n{analysis}\n")
            
        except Exception as e:
            print(f"⚠️  AI Review failed: {e}")
    
    def run_playbook(self, playbook_name: str):
        """Execute a YAML playbook from /playbooks/"""
        import yaml
        
        playbook_path = Path(__file__).parent / 'playbooks' / f'{playbook_name}.yaml'
        
        if not playbook_path.exists():
            print(f"❌ Playbook '{playbook_name}' not found.")
            return
        
        try:
            with open(playbook_path) as f:
                playbook = yaml.safe_load(f)
            
            print(f"\n📋 Executing Playbook: {playbook['name']}")
            print(f"   Description: {playbook['description']}")
            
            confirm = input("Proceed? [y/N]: ").strip().lower()
            if confirm != 'y': return
            
            for step in playbook.get('steps', []):
                print(f"\n▶️  Step: {step.get('name', 'unnamed')}")
                result = subprocess.run(step.get('cmd'), shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"❌ Step failed: {result.stderr}")
                    return
                print(f"✅ Success")
            
        except Exception as e:
            print(f"❌ Playbook error: {e}")

    def interactive(self):
        print("🌌 SemSH v0.3 - SSAP Advisor Active")
        print(f"Perfil Activo: {self.profile['name']} [{self.profile['mode']}]")
        print("\nCommands: dashboard | health | review <cmd> | run <playbook> | <natural language>")
        
        while True:
            try:
                query = input("\n🧠 semsh> ").strip()
                if query in ['exit', 'quit']: break
                if not query: continue
                
                if query.lower() == 'dashboard':
                    self.vector_dashboard()
                    continue
                
                if query.lower() == 'health':
                    self.health_advisor()
                    continue
                
                if query.lower().startswith('review '):
                    self.review_command(query[7:].strip())
                    continue
                
                if query.lower().startswith('run '):
                    self.run_playbook(query[4:].strip())
                    continue
                
                # Semantic Command
                cmd = self.contextual_intent(query)
                print(f"🎯 Intent → {cmd}")
                out = self.safe_execute(cmd)
                
                display_out = (out[:500] + '...') if len(out) > 500 else out
                print(f"📊 {display_out}")
                
            except KeyboardInterrupt: break
        
        if self.pg_conn:
            self.pg_conn.close()

if __name__ == "__main__":
    SemSH().interactive()
