#!/usr/bin/env python3
"""
Prometheus Client for Quantum Cooling

Fetches real-time metrics from Prometheus for buffer optimization.
"""

import requests
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BufferMetrics:
    """Real-time buffer metrics from Prometheus"""
    timestamp: float
    utilization: float  # 0.0-1.0
    drop_rate: float    # drops per second
    traffic_rate: float # packets per second
    buffer_size: int    # current size in bytes


class PrometheusClient:
    """
    Client for fetching buffer metrics from Prometheus.
    
    Queries:
    - Buffer utilization
    - Packet drop rate
    - Traffic rate
    """
    
    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        self.prometheus_url = prometheus_url
        self.query_url = f"{prometheus_url}/api/v1/query"
        
    def _query(self, promql: str) -> Optional[float]:
        """Execute PromQL query and return single value."""
        try:
            response = requests.get(
                self.query_url,
                params={'query': promql},
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'success':
                return None
            
            result = data['data']['result']
            if not result:
                return None
            
            # Get the most recent value
            value = float(result[0]['value'][1])
            return value
            
        except Exception as e:
            print(f"Prometheus query error: {e}")
            return None
    
    def get_buffer_utilization(self) -> Optional[float]:
        """
        Get current buffer utilization (0.0-1.0).
        
        PromQL: buffer_used_bytes / buffer_total_bytes
        """
        # Adjust this query to match your actual metrics
        query = 'node_network_receive_bytes_total / node_network_receive_buffer_bytes'
        return self._query(query)
    
    def get_drop_rate(self) -> Optional[float]:
        """
        Get packet drop rate (drops per second).
        
        PromQL: rate(node_network_receive_drop_total[1m])
        """
        query = 'rate(node_network_receive_drop_total[1m])'
        return self._query(query)
    
    def get_traffic_rate(self) -> Optional[float]:
        """
        Get traffic rate (packets per second).
        
        PromQL: rate(node_network_receive_packets_total[1m])
        """
        query = 'rate(node_network_receive_packets_total[1m])'
        return self._query(query)
    
    def get_buffer_size(self) -> Optional[int]:
        """
        Get current buffer size in bytes.
        
        PromQL: node_network_receive_buffer_bytes
        """
        query = 'node_network_receive_buffer_bytes'
        result = self._query(query)
        return int(result) if result else None
    
    def get_current_metrics(self) -> Optional[BufferMetrics]:
        """
        Fetch all current metrics in one call.
        
        Returns BufferMetrics or None if any metric fails.
        """
        utilization = self.get_buffer_utilization()
        drop_rate = self.get_drop_rate()
        traffic_rate = self.get_traffic_rate()
        buffer_size = self.get_buffer_size()
        
        # If any metric is missing, return None
        if any(x is None for x in [utilization, drop_rate, traffic_rate, buffer_size]):
            return None
        
        return BufferMetrics(
            timestamp=time.time(),
            utilization=utilization,
            drop_rate=drop_rate,
            traffic_rate=traffic_rate,
            buffer_size=buffer_size
        )
    
    def health_check(self) -> bool:
        """Check if Prometheus is reachable."""
        try:
            response = requests.get(
                f"{self.prometheus_url}/-/healthy",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False


# ============================================================================
# DEMO: Test Prometheus connection
# ============================================================================

def demo_prometheus_client():
    """Test Prometheus client with real metrics."""
    print("="*70)
    print("🔍 PROMETHEUS CLIENT - DEMO")
    print("="*70)
    print()
    
    client = PrometheusClient()
    
    # Health check
    print("Checking Prometheus health...")
    if client.health_check():
        print("✅ Prometheus is reachable")
    else:
        print("❌ Prometheus is not reachable")
        print("   Make sure Prometheus is running on localhost:9090")
        return
    
    print()
    
    # Fetch metrics
    print("Fetching current metrics...")
    metrics = client.get_current_metrics()
    
    if metrics:
        print("✅ Metrics fetched successfully:")
        print(f"   Timestamp: {datetime.fromtimestamp(metrics.timestamp)}")
        print(f"   Buffer utilization: {metrics.utilization:.2%}")
        print(f"   Drop rate: {metrics.drop_rate:.2f} drops/sec")
        print(f"   Traffic rate: {metrics.traffic_rate:.2f} packets/sec")
        print(f"   Buffer size: {metrics.buffer_size:,} bytes")
    else:
        print("⚠️  Could not fetch all metrics")
        print("   Check your Prometheus queries")
    
    print()
    print("="*70)


if __name__ == '__main__':
    demo_prometheus_client()
