"""
Sentinel Vault - Terminal Service
Command palette for vault operations
"""
import re
from typing import Dict, List, Optional
from datetime import datetime


class TerminalService:
    """Service for executing vault commands"""
    
    def __init__(self):
        self.command_history = []
        
    def parse_command(self, command: str) -> Dict:
        """
        Parse command into action and arguments
        
        Args:
            command: Command string (e.g., "vault balance btc")
        
        Returns:
            Dict with action and args
        """
        parts = command.strip().split()
        
        if len(parts) == 0:
            return {"action": "empty", "args": []}
        
        # Remove 'vault' prefix if present
        if parts[0].lower() == "vault":
            parts = parts[1:]
        
        if len(parts) == 0:
            return {"action": "empty", "args": []}
        
        action = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        return {"action": action, "args": args}
    
    def execute(self, command: str, context: Dict = None) -> Dict:
        """
        Execute vault command
        
        Args:
            command: Command string
            context: Optional context (user_id, etc.)
        
        Returns:
            Dict with success, output, and metadata
        """
        # Add to history
        self.command_history.append({
            "command": command,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Parse command
        parsed = self.parse_command(command)
        action = parsed["action"]
        args = parsed["args"]
        
        # Execute based on action
        if action == "help":
            return self._help()
        
        elif action == "balance":
            return self._balance(args)
        
        elif action == "address":
            return self._address(args)
        
        elif action == "get":
            return self._get_password(args)
        
        elif action == "list":
            return self._list(args)
        
        elif action == "search":
            return self._search(args)
        
        elif action == "status":
            return self._status()
        
        elif action == "history":
            return self._history()
        
        elif action == "generate":
            return self._generate_password(args)
        
        elif action == "empty":
            return {
                "success": True,
                "output": "",
                "type": "empty"
            }
        
        else:
            return {
                "success": False,
                "output": f"Unknown command: {action}\nType 'vault help' for available commands",
                "type": "error"
            }
    
    def _help(self) -> Dict:
        """Show help"""
        output = """
🔐 Sentinel Vault - Available Commands

CRYPTO WALLET:
  vault balance              Show all wallet balances
  vault balance <chain>      Show specific chain balance (btc, eth, matic, sol)
  vault address <chain>      Show wallet address for chain

PASSWORDS:
  vault get <service>        Get password for service
  vault list passwords       List all saved passwords
  vault generate <length>    Generate random password

DOCUMENTS:
  vault list documents       List all documents

NOTES:
  vault list notes           List all notes
  vault search <query>       Search notes by content

SYSTEM:
  vault status               Show vault status
  vault history              Show command history
  vault help                 Show this help message

Examples:
  $ vault balance btc
  $ vault get github
  $ vault generate 32
  $ vault search "crypto"
"""
        return {
            "success": True,
            "output": output.strip(),
            "type": "help"
        }
    
    def _balance(self, args: List[str]) -> Dict:
        """Show wallet balance"""
        if len(args) == 0:
            # Show all balances
            output = """
💰 Wallet Balances:

Bitcoin (BTC):    0.00000000 BTC  ($0.00)
Ethereum (ETH):   0.00000000 ETH  ($0.00)
Polygon (MATIC):  0.00000000 MATIC ($0.00)
Solana (SOL):     0.00000000 SOL  ($0.00)

Total Portfolio: $0.00

Note: Connect wallet to see real balances
"""
            return {
                "success": True,
                "output": output.strip(),
                "type": "balance"
            }
        else:
            chain = args[0].lower()
            if chain in ["btc", "bitcoin"]:
                output = "Bitcoin (BTC): 0.00000000 BTC ($0.00)"
            elif chain in ["eth", "ethereum"]:
                output = "Ethereum (ETH): 0.00000000 ETH ($0.00)"
            elif chain in ["matic", "polygon"]:
                output = "Polygon (MATIC): 0.00000000 MATIC ($0.00)"
            elif chain in ["sol", "solana"]:
                output = "Solana (SOL): 0.00000000 SOL ($0.00)"
            else:
                output = f"Unknown chain: {chain}\nSupported: btc, eth, matic, sol"
            
            return {
                "success": True,
                "output": output,
                "type": "balance"
            }
    
    def _address(self, args: List[str]) -> Dict:
        """Show wallet address"""
        if len(args) == 0:
            return {
                "success": False,
                "output": "Usage: vault address <chain>\nExample: vault address btc",
                "type": "error"
            }
        
        chain = args[0].lower()
        # In production, get from database
        output = f"{chain.upper()} Address: (connect wallet to see address)"
        
        return {
            "success": True,
            "output": output,
            "type": "address"
        }
    
    def _get_password(self, args: List[str]) -> Dict:
        """Get password for service"""
        if len(args) == 0:
            return {
                "success": False,
                "output": "Usage: vault get <service>\nExample: vault get github",
                "type": "error"
            }
        
        service = " ".join(args)
        # In production, query database
        output = f"Password for '{service}': (not found)\nUse password manager to save passwords"
        
        return {
            "success": True,
            "output": output,
            "type": "password"
        }
    
    def _list(self, args: List[str]) -> Dict:
        """List items"""
        if len(args) == 0:
            return {
                "success": False,
                "output": "Usage: vault list <type>\nTypes: passwords, documents, notes",
                "type": "error"
            }
        
        item_type = args[0].lower()
        
        if item_type == "passwords":
            output = "📝 Saved Passwords:\n\n(No passwords saved yet)"
        elif item_type == "documents":
            output = "📄 Documents:\n\n(No documents uploaded yet)"
        elif item_type == "notes":
            output = "📝 Notes:\n\n(No notes created yet)"
        else:
            output = f"Unknown type: {item_type}\nSupported: passwords, documents, notes"
        
        return {
            "success": True,
            "output": output,
            "type": "list"
        }
    
    def _search(self, args: List[str]) -> Dict:
        """Search notes"""
        if len(args) == 0:
            return {
                "success": False,
                "output": "Usage: vault search <query>\nExample: vault search \"crypto\"",
                "type": "error"
            }
        
        query = " ".join(args).strip('"')
        # In production, search database
        output = f"🔍 Search results for '{query}':\n\n(No results found)"
        
        return {
            "success": True,
            "output": output,
            "type": "search"
        }
    
    def _status(self) -> Dict:
        """Show vault status"""
        output = """
🔐 Sentinel Vault Status

Vault: Unlocked ✅
Encryption: AES-256-GCM
Key Derivation: Argon2id

Features:
  ✅ Password Manager
  ✅ Crypto Wallet (4 chains)
  ✅ Document Vault
  ✅ Encrypted Notes
  ✅ Command Terminal

Last Activity: Just now
"""
        return {
            "success": True,
            "output": output.strip(),
            "type": "status"
        }
    
    def _history(self) -> Dict:
        """Show command history"""
        if len(self.command_history) == 0:
            output = "No command history"
        else:
            output = "📜 Command History:\n\n"
            for i, entry in enumerate(self.command_history[-10:], 1):
                output += f"{i}. {entry['command']}\n"
        
        return {
            "success": True,
            "output": output.strip(),
            "type": "history"
        }
    
    def _generate_password(self, args: List[str]) -> Dict:
        """Generate random password"""
        import secrets
        import string
        
        length = 32
        if len(args) > 0:
            try:
                length = int(args[0])
                if length < 8 or length > 128:
                    length = 32
            except:
                length = 32
        
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(chars) for _ in range(length))
        
        output = f"🔑 Generated Password ({length} chars):\n\n{password}\n\n⚠️  Save this password securely!"
        
        return {
            "success": True,
            "output": output,
            "type": "generate"
        }


# ============================================================================
# Testing
# ============================================================================

def test_terminal_service():
    print("💻 Terminal Service - Testing\n")
    
    service = TerminalService()
    
    # Test commands
    commands = [
        "vault help",
        "vault balance",
        "vault balance btc",
        "vault address eth",
        "vault get github",
        "vault list passwords",
        "vault search crypto",
        "vault status",
        "vault generate 16",
        "vault history",
        "unknown command"
    ]
    
    for cmd in commands:
        print(f"\n{'='*60}")
        print(f"Command: {cmd}")
        print('='*60)
        result = service.execute(cmd)
        print(result['output'])
        if not result['success']:
            print(f"\n❌ Error")
    
    print("\n\n🎉 All tests completed!")


if __name__ == "__main__":
    test_terminal_service()
