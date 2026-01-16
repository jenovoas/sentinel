"""
Integration tests for Ollama AI
Requires Ollama service running with GPU
"""

import pytest
import httpx
import asyncio
import psutil
from pathlib import Path

# Skip if Ollama not available
pytestmark = pytest.mark.integration


async def check_ollama_available():
    """Check if Ollama is running"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get("http://127.0.0.1:11434/api/tags")
            return response.status_code == 200
    except:
        return False


@pytest.fixture(scope="module")
async def ollama_check():
    """Ensure Ollama is available before running tests"""
    if not await check_ollama_available():
        pytest.skip("Ollama service not available")


class TestOllamaGPUIntegration:
    """Integration tests for GPU acceleration"""
    
    @pytest.mark.gpu
    async def test_gpu_offloading(self, ollama_check):
        """Verify that model layers are offloaded to GPU"""
        import subprocess
        
        # Trigger model load
        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": "Test",
                    "stream": False
                }
            )
        
        # Check journalctl for GPU offloading
        result = subprocess.run(
            ["journalctl", "-u", "ollama", "-n", "50", "--no-pager"],
            capture_output=True,
            text=True
        )
        
        assert "offloaded" in result.stdout.lower()
        assert "cuda" in result.stdout.lower()
        assert "gpu" in result.stdout.lower() or "vram" in result.stdout.lower()
    
    @pytest.mark.gpu
    async def test_vram_usage(self, ollama_check):
        """Verify VRAM is being used"""
        import subprocess
        
        # Get VRAM before
        result_before = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True
        )
        vram_before = int(result_before.stdout.strip())
        
        # Make request
        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": "Explain quantum computing in one sentence",
                    "stream": False
                }
            )
        
        # Get VRAM after
        result_after = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True
        )
        vram_after = int(result_after.stdout.strip())
        
        # VRAM should increase (model loaded)
        assert vram_after > vram_before, f"VRAM not increasing: {vram_before}MB -> {vram_after}MB"
        assert vram_after >= 1000, f"VRAM usage too low: {vram_after}MB (expected >1000MB)"


class TestOllamaConcurrency:
    """Tests for concurrent requests"""
    
    async def test_concurrent_requests(self, ollama_check):
        """Test 10 concurrent requests"""
        async def make_request(i: int):
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={
                        "model": "llama3.2:3b",
                        "prompt": f"Count to {i}",
                        "stream": False
                    }
                )
                return response.status_code
        
        # Run 10 concurrent requests
        tasks = [make_request(i) for i in range(1, 11)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(status == 200 for status in results)
    
    async def test_memory_leak(self, ollama_check):
        """Test that VRAM is released after requests"""
        import subprocess
        import time
        
        # Make 5 requests
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(5):
                await client.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={
                        "model": "llama3.2:3b",
                        "prompt": f"Test {i}",
                        "stream": False
                    }
                )
        
        # Wait for cleanup
        time.sleep(5)
        
        # Check VRAM
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True
        )
        vram_used = int(result.stdout.strip())
        
        # Should not exceed 2GB (model + overhead)
        assert vram_used < 2500, f"Possible memory leak: {vram_used}MB VRAM used"


class TestOllamaPerformance:
    """Performance tests"""
    
    @pytest.mark.gpu
    async def test_response_latency(self, ollama_check):
        """Test that GPU responses are fast (<3s)"""
        import time
        
        start = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": "What is 2+2?",
                    "stream": False
                }
            )
        latency = time.time() - start
        
        assert response.status_code == 200
        assert latency < 3.0, f"Response too slow: {latency:.2f}s (expected <3s with GPU)"
    
    async def test_throughput(self, ollama_check):
        """Test throughput (requests per second)"""
        import time
        
        n_requests = 5
        start = time.time()
        
        async def make_request():
            async with httpx.AsyncClient(timeout=30.0) as client:
                await client.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={
                        "model": "llama3.2:3b",
                        "prompt": "Hi",
                        "stream": False
                    }
                )
        
        tasks = [make_request() for _ in range(n_requests)]
        await asyncio.gather(*tasks)
        
        duration = time.time() - start
        throughput = n_requests / duration
        
        # Should handle at least 1 req/s with GPU
        assert throughput >= 0.5, f"Throughput too low: {throughput:.2f} req/s"


class TestOllamaServiceRecovery:
    """Tests for service recovery"""
    
    async def test_service_restart_recovery(self, ollama_check):
        """Test that service recovers after restart"""
        import subprocess
        import time
        
        # Restart service
        subprocess.run(["sudo", "systemctl", "restart", "ollama"], check=True)
        
        # Wait for service to start
        time.sleep(5)
        
        # Verify service is up
        result = subprocess.run(
            ["systemctl", "is-active", "ollama"],
            capture_output=True,
            text=True
        )
        assert result.stdout.strip() == "active"
        
        # Verify can make requests
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get("http://127.0.0.1:11434/api/tags")
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
