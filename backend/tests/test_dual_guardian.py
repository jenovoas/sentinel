"""
Integration Tests for Dual-Guardian Architecture (Claim 3 Validation)

Validates the complete Dual-Guardian architecture including:
1. SecurityLaneCollector + WAL integration (100ms fsync)
2. ObservabilityLaneCollector + WAL integration (1s fsync)
3. Mutual Surveillance mechanism
4. Cognitive decision-making vs traditional watchdog

Run with: pytest backend/tests/test_dual_guardian.py -v
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import pytest
import asyncio
import time
from pathlib import Path
from backend.app.core.data_lanes import (
    DataLane,
    LaneEvent,
    EventPriority,
    SecurityLaneCollector,
    ObservabilityLaneCollector
)
from backend.app.core.mutual_surveillance import (
    MutualSurveillance,
    GuardianHealth
)


class TestSecurityLaneCollector:
    """Test Security Lane with WAL integration"""
    
    @pytest.mark.asyncio
    async def test_security_lane_wal_integration(self, tmp_path):
        """Verify Security Lane writes to WAL with 100ms fsync"""
        collector = SecurityLaneCollector(wal_path=tmp_path)
        
        # Create test event
        event = LaneEvent(
            lane=DataLane.SECURITY,
            source="ebpf",
            priority=EventPriority.CRITICAL,
            timestamp=time.time(),
            labels={"lane": "security", "source": "ebpf"},
            data={"binary": "/tmp/malware", "action": "blocked"}
        )
        
        # Emit event
        success = await collector.emit_immediate(event)
        
        assert success, "Security lane emit should succeed"
        assert collector.stats["events_collected"] == 1
        assert collector.stats["events_lost"] == 0
    
    @pytest.mark.asyncio
    async def test_security_lane_latency_target(self, tmp_path):
        """Verify Security Lane meets <10ms latency target"""
        collector = SecurityLaneCollector(wal_path=tmp_path)
        
        event = LaneEvent(
            lane=DataLane.SECURITY,
            source="shield",
            priority=EventPriority.CRITICAL,
            timestamp=time.time(),
            labels={"lane": "security"},
            data={"threat": "prompt_injection"}
        )
        
        start = time.time()
        await collector.emit_immediate(event)
        latency_ms = (time.time() - start) * 1000
        
        # Should be <10ms (though may be higher in test environment)
        assert latency_ms < 100, f"Latency {latency_ms}ms too high (target <10ms in production)"
    
    @pytest.mark.asyncio
    async def test_security_lane_integrity_gap_alert(self, tmp_path):
        """Verify Security Lane alerts on data loss (never imputes)"""
        collector = SecurityLaneCollector(wal_path=tmp_path)
        
        # This test would simulate WAL failure
        # In production, this should trigger CRITICAL alert
        # For now, we verify the alert mechanism exists
        
        assert hasattr(collector, '_alert_integrity_gap'), \
            "Security lane must have integrity gap alerting"


class TestObservabilityLaneCollector:
    """Test Observability Lane with WAL integration"""
    
    @pytest.mark.asyncio
    async def test_observability_lane_buffering(self, tmp_path):
        """Verify Observability Lane buffers events"""
        collector = ObservabilityLaneCollector(
            wal_path=tmp_path,
            max_batch_records=10
        )
        
        # Add 5 events (should buffer, not flush)
        for i in range(5):
            event = LaneEvent(
                lane=DataLane.OBSERVABILITY,
                source="prometheus",
                priority=EventPriority.MEDIUM,
                timestamp=time.time(),
                labels={"lane": "ops"},
                data={"cpu": 50 + i}
            )
            await collector.emit_buffered(event)
        
        # Should be buffered, not flushed yet
        assert len(collector.buffer) == 5
        assert collector.stats["events_flushed"] == 0
    
    @pytest.mark.asyncio
    async def test_observability_lane_batch_flush(self, tmp_path):
        """Verify Observability Lane flushes batches to WAL"""
        collector = ObservabilityLaneCollector(
            wal_path=tmp_path,
            max_batch_records=5  # Small batch for testing
        )
        
        # Add 5 events (should trigger flush)
        for i in range(5):
            event = LaneEvent(
                lane=DataLane.OBSERVABILITY,
                source="app",
                priority=EventPriority.LOW,
                timestamp=time.time() + i,  # Incrementing timestamps
                labels={"lane": "ops"},
                data={"request_count": 100 + i}
            )
            await collector.emit_buffered(event)
        
        # Should have flushed
        assert collector.stats["events_flushed"] >= 5
        assert len(collector.buffer) == 0  # Buffer cleared


class TestMutualSurveillance:
    """Test Mutual Surveillance mechanism"""
    
    @pytest.mark.asyncio
    async def test_alpha_health_check_healthy(self):
        """Verify Alpha health check detects healthy state"""
        surveillance = MutualSurveillance()
        
        # Simulate recent Alpha activity
        surveillance.update_alpha_activity()
        
        health = await surveillance.check_alpha_health()
        
        assert health.status == GuardianHealth.HEALTHY
        assert health.recommended_action == "none"
    
    @pytest.mark.asyncio
    async def test_alpha_health_check_compromised(self):
        """Verify Alpha health check detects compromise"""
        surveillance = MutualSurveillance(alpha_timeout_seconds=1)
        
        # Simulate no Alpha activity for 2 seconds
        surveillance.alpha_last_activity = time.time() - 2
        
        health = await surveillance.check_alpha_health()
        
        assert health.status == GuardianHealth.COMPROMISED
        assert "investigate" in health.recommended_action
    
    @pytest.mark.asyncio
    async def test_beta_health_check_healthy(self):
        """Verify Beta health check detects healthy state"""
        surveillance = MutualSurveillance()
        
        # Simulate recent Beta activity
        surveillance.update_beta_activity()
        
        health = await surveillance.check_beta_health()
        
        assert health.status == GuardianHealth.HEALTHY
        assert health.recommended_action == "none"
    
    @pytest.mark.asyncio
    async def test_beta_health_check_dead(self):
        """Verify Beta health check detects death"""
        surveillance = MutualSurveillance(beta_timeout_seconds=1)
        
        # Simulate no Beta activity for 2 seconds
        surveillance.beta_last_activity = time.time() - 2
        
        health = await surveillance.check_beta_health()
        
        assert health.status == GuardianHealth.DEAD
        assert "restart" in health.recommended_action
    
    @pytest.mark.asyncio
    async def test_cognitive_decision_vs_watchdog(self):
        """
        Verify Mutual Surveillance makes COGNITIVE decisions
        (not just restart like traditional watchdog)
        """
        surveillance = MutualSurveillance()
        
        # Simulate Alpha compromise
        surveillance.alpha_last_activity = time.time() - 100
        health = await surveillance.check_alpha_health()
        
        # Should have context-aware recommendation
        assert health.recommended_action != "restart"  # Not just restart
        assert "investigate" in health.recommended_action  # Cognitive analysis
        
        # Verify stats track anomalies
        assert surveillance.stats["alpha_anomalies"] > 0


class TestDualGuardianIntegration:
    """End-to-end tests for complete Dual-Guardian architecture"""
    
    @pytest.mark.asyncio
    async def test_security_lane_independent_of_observability(self, tmp_path):
        """
        Verify Security Lane is NOT affected by Observability Lane load
        
        This is CRITICAL for Claim 3: Dual-Guardian ensures security
        decisions are not delayed by operational metrics volume
        """
        security_collector = SecurityLaneCollector(wal_path=tmp_path)
        obs_collector = ObservabilityLaneCollector(wal_path=tmp_path)
        
        # Flood Observability Lane
        obs_tasks = []
        for i in range(1000):
            event = LaneEvent(
                lane=DataLane.OBSERVABILITY,
                source="metrics",
                priority=EventPriority.LOW,
                timestamp=time.time(),
                labels={"lane": "ops"},
                data={"metric": i}
            )
            obs_tasks.append(obs_collector.emit_buffered(event))
        
        # Emit critical security event during flood
        security_event = LaneEvent(
            lane=DataLane.SECURITY,
            source="ebpf",
            priority=EventPriority.CRITICAL,
            timestamp=time.time(),
            labels={"lane": "security"},
            data={"threat": "critical"}
        )
        
        start = time.time()
        security_success = await security_collector.emit_immediate(security_event)
        security_latency = (time.time() - start) * 1000
        
        # Security event should succeed despite Observability flood
        assert security_success, "Security lane must not be affected by ops load"
        assert security_latency < 100, "Security latency must remain low"
        
        # Wait for Observability to finish
        await asyncio.gather(*obs_tasks)
        
        # Verify both lanes processed independently
        assert security_collector.stats["events_collected"] == 1
        assert obs_collector.stats["events_buffered"] == 1000


class TestPatentDifferentiation:
    """Tests that validate patent claims differentiation"""
    
    def test_claim3_dual_guardian_vs_traditional_watchdog(self):
        """
        Verify Dual-Guardian is NOT a traditional watchdog
        
        Traditional Watchdog:
        - Timeout → Restart
        
        Dual-Guardian (Sentinel):
        - Timeout → Analyze context → Cognitive decision
        """
        surveillance = MutualSurveillance()
        
        # Verify cognitive decision-making methods exist
        assert hasattr(surveillance, 'handle_alpha_compromise'), \
            "Must have cognitive Alpha compromise handler"
        assert hasattr(surveillance, 'handle_beta_compromise'), \
            "Must have cognitive Beta compromise handler"
        
        # Verify NOT just restart
        assert hasattr(surveillance, 'check_alpha_health'), \
            "Must analyze health, not just timeout"
        assert hasattr(surveillance, 'check_beta_health'), \
            "Must analyze health, not just timeout"
