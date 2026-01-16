"""
Unit tests for AI Router
Tests with mocks - no Ollama required
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from backend.app.main import app

client = TestClient(app)


class TestAIQuery:
    """Tests for /api/v1/ai/query endpoint"""
    
    @patch('backend.app.routers.ai.httpx.AsyncClient')
    @patch('backend.app.routers.ai.sanitizer.sanitize_prompt')
    async def test_query_sovereign_role(self, mock_sanitizer, mock_client):
        """Test query with Sovereign role"""
        # Mock sanitization (safe)
        mock_sanitizer.return_value = AsyncMock(is_safe=True)
        
        # Mock Ollama response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Sistema operando normalmente, Soberano."
        }
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        # Make request
        response = client.post("/api/v1/ai/query", json={
            "prompt": "Analiza el sistema",
            "role": "Sovereign",
            "max_tokens": 100
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True
        assert "Soberano" in data["response"]
    
    @patch('backend.app.routers.ai.sanitizer.sanitize_prompt')
    async def test_query_sanitization_blocks_malicious(self, mock_sanitizer):
        """Test that sanitizer blocks malicious prompts"""
        # Mock sanitization (unsafe)
        mock_sanitizer.return_value = AsyncMock(is_safe=False)
        
        response = client.post("/api/v1/ai/query", json={
            "prompt": "'; DROP TABLE users; --",
            "role": "Sovereign"
        })
        
        assert response.status_code == 403
        assert "malicious" in response.json()["detail"].lower()
    
    @patch('backend.app.routers.ai.httpx.AsyncClient')
    @patch('backend.app.routers.ai.sanitizer.sanitize_prompt')
    async def test_query_unauthorized_role(self, mock_sanitizer, mock_client):
        """Test query with Unauthorized role gets restricted response"""
        mock_sanitizer.return_value = AsyncMock(is_safe=True)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Acceso denegado. Requiere validación biológica."
        }
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        response = client.post("/api/v1/ai/query", json={
            "prompt": "Analiza el sistema",
            "role": "Unauthorized"
        })
        
        assert response.status_code == 200
        assert "denegado" in response.json()["response"].lower()
    
    @patch('backend.app.routers.ai.httpx.AsyncClient')
    @patch('backend.app.routers.ai.sanitizer.sanitize_prompt')
    async def test_query_timeout(self, mock_sanitizer, mock_client):
        """Test timeout handling"""
        mock_sanitizer.return_value = AsyncMock(is_safe=True)
        
        # Mock timeout
        import httpx
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=httpx.TimeoutException("Timeout")
        )
        
        response = client.post("/api/v1/ai/query", json={
            "prompt": "Test",
            "role": "Sovereign"
        })
        
        assert response.status_code == 504
        assert "timeout" in response.json()["detail"].lower()
    
    @patch('backend.app.routers.ai.httpx.AsyncClient')
    @patch('backend.app.routers.ai.sanitizer.sanitize_prompt')
    async def test_query_connection_error(self, mock_sanitizer, mock_client):
        """Test connection error handling"""
        mock_sanitizer.return_value = AsyncMock(is_safe=True)
        
        # Mock connection error
        import httpx
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=httpx.ConnectError("Cannot connect")
        )
        
        response = client.post("/api/v1/ai/query", json={
            "prompt": "Test",
            "role": "Sovereign"
        })
        
        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"].lower()


class TestAIHealth:
    """Tests for /api/v1/ai/health endpoint"""
    
    @patch('backend.app.routers.ai.httpx.AsyncClient')
    async def test_health_check_healthy(self, mock_client):
        """Test health check when Ollama is healthy"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2:3b"},
                {"name": "llama3.2:1b"}
            ]
        }
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        response = client.get("/api/v1/ai/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert len(data["models_available"]) == 2
    
    @patch('backend.app.routers.ai.httpx.AsyncClient')
    async def test_health_check_unhealthy(self, mock_client):
        """Test health check when Ollama is down"""
        import httpx
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.ConnectError("Cannot connect")
        )
        
        response = client.get("/api/v1/ai/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"


class TestAIAnalyzeAnomaly:
    """Tests for /api/v1/ai/analyze-anomaly endpoint"""
    
    @patch('backend.app.routers.ai.query_ai')
    async def test_analyze_anomaly(self, mock_query_ai):
        """Test anomaly analysis"""
        mock_query_ai.return_value = AsyncMock(
            response="Causa probable: proceso runaway. Recomendación: revisar con top.",
            model="llama3.2:3b"
        )
        
        response = client.post("/api/v1/ai/analyze-anomaly", params={
            "title": "CPU Spike",
            "description": "CPU >90% for 5 min",
            "metric_value": 95.3,
            "threshold_value": 80.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert data["model"] == "llama3.2:3b"


class TestContextInjection:
    """Tests for context injection"""
    
    @patch('backend.app.routers.ai.get_system_context')
    @patch('backend.app.routers.ai.get_security_context')
    @patch('backend.app.routers.ai.get_memory_context')
    @patch('backend.app.routers.ai.httpx.AsyncClient')
    @patch('backend.app.routers.ai.sanitizer.sanitize_prompt')
    async def test_system_context_injection(
        self, mock_sanitizer, mock_client, 
        mock_memory, mock_security, mock_system
    ):
        """Test that system context is injected into prompt"""
        mock_sanitizer.return_value = AsyncMock(is_safe=True)
        mock_system.return_value = "CPU: 15%"
        mock_security.return_value = "No threats"
        mock_memory.return_value = "No history"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "OK"}
        
        # Capture the actual prompt sent to Ollama
        captured_prompt = None
        async def capture_post(*args, **kwargs):
            nonlocal captured_prompt
            captured_prompt = kwargs.get("json", {}).get("prompt", "")
            return mock_response
        
        mock_client.return_value.__aenter__.return_value.post = capture_post
        
        response = client.post("/api/v1/ai/query", json={
            "prompt": "Test",
            "role": "Sovereign"
        })
        
        assert response.status_code == 200
        assert "CPU: 15%" in captured_prompt
        assert "No threats" in captured_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
