import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Mock dependencies that may fail to import or run in sandbox environment
sys.modules['me60os_core'] = MagicMock()
mock_sr_module = MagicMock()
sys.modules['semantic_router'] = mock_sr_module
sys.modules['quantum.semantic_router'] = mock_sr_module

from quantum.semantic_shell import SemanticShell

class TestSemanticShellSecurity(unittest.TestCase):
    @patch("quantum.semantic_shell.subprocess.run")
    def test_query_oracle_command_injection_prevented(self, mock_subprocess_run):
        shell = SemanticShell()
        user_input = 'test"; echo "HACKED'

        # Mock classify_intent async method
        async def mock_classify(inp):
            return ("QUERY_ORACLE", "reason")
        shell.router.classify_intent = mock_classify

        import asyncio
        asyncio.run(shell.process_command(user_input))

        # Verify subprocess.run was called with argument list, avoiding shell injection
        mock_subprocess_run.assert_called_once_with(
            [sys.executable, "quantum/quantum_oracle_cli.py", user_input],
            check=False
        )

    @patch("quantum.semantic_shell.subprocess.run")
    def test_execute_system_action_secure(self, mock_subprocess_run):
        shell = SemanticShell()

        shell.execute_system_action("open dashboard; injection", "reason")
        mock_subprocess_run.assert_called_with(
            [sys.executable, "quantum/sentinel_dashboard.py"],
            check=False
        )

        shell.execute_system_action("scan", "reason")
        mock_subprocess_run.assert_called_with(
            [sys.executable, "quantum/quantum_scanner.py", "quantum/RESONANT_ARCH_SPECS.md"],
            check=False
        )

        shell.execute_system_action("lattice", "reason")
        mock_subprocess_run.assert_called_with(
            [sys.executable, "quantum/quantum_lattice.py"],
            check=False
        )

        shell.execute_system_action("audit", "reason")
        mock_subprocess_run.assert_called_with(
            [sys.executable, "quantum/TRUTHSYNC_FULL_SYSTEM_AUDIT.py"],
            check=False
        )

if __name__ == "__main__":
    unittest.main()
