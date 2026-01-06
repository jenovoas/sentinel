#!/usr/bin/env python3
"""
Sentinel Performance Profiler
==============================

Advanced performance profiling and analysis tool for Sentinel.

Usage:
    python performance_profiler.py --duration 60 --output report.html
    
Features:
    - Real-time performance monitoring
    - Latency analysis
    - Resource utilization tracking
    - Bottleneck detection
    - HTML report generation
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import argparse
import time
import json
import statistics
from datetime import datetime
from typing import List, Dict, Any
import requests
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    timestamp: float
    endpoint: str
    latency_ms: float
    status_code: int
    success: bool
    error: str = None


class PerformanceProfiler:
    """Main performance profiler class"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.metrics: List[PerformanceMetric] = []
        self.start_time = None
        self.end_time = None
    
    def profile_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None) -> PerformanceMetric:
        """Profile a single endpoint request"""
        url = f"{self.base_url}{endpoint}"
        start = time.time()
        error = None
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            latency = (time.time() - start) * 1000
            success = response.status_code == 200
            status_code = response.status_code
            
        except Exception as e:
            latency = (time.time() - start) * 1000
            success = False
            status_code = 0
            error = str(e)
        
        metric = PerformanceMetric(
            timestamp=time.time(),
            endpoint=endpoint,
            latency_ms=latency,
            status_code=status_code,
            success=success,
            error=error
        )
        
        self.metrics.append(metric)
        return metric
    
    def run_profiling_session(self, duration_seconds: int = 60, interval: float = S60(1, 0, 0)):
        """Run a profiling session"""
        print(f"Starting profiling session for {duration_seconds} seconds...")
        print(f"Interval: {interval}s")
        print()
        
        self.start_time = time.time()
        end_time = self.start_time + duration_seconds
        
        # Endpoints to profile
        endpoints = [
            ("/api/v1/health", "GET", None),
            ("/api/v1/dashboard/status", "GET", None),
            ("/api/v1/ai/health", "GET", None),
        ]
        
        iteration = 0
        while time.time() < end_time:
            iteration += 1
            print(f"Iteration {iteration}:")
            
            for endpoint, method, data in endpoints:
                metric = self.profile_endpoint(endpoint, method, data)
                status = "✓" if metric.success else "✗"
                print(f"  {status} {endpoint}: {metric.latency_ms:.2f}ms")
            
            time.sleep(interval)
        
        self.end_time = time.time()
        print(f"\n✅ Profiling session completed: {len(self.metrics)} measurements")
    
    def analyze_metrics(self) -> Dict[str, Any]:
        """Analyze collected metrics"""
        if not self.metrics:
            return {}
        
        # Group by endpoint
        by_endpoint = defaultdict(list)
        for metric in self.metrics:
            by_endpoint[metric.endpoint].append(metric)
        
        analysis = {
            "session": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
                "duration_seconds": self.end_time - self.start_time,
                "total_requests": len(self.metrics),
                "successful_requests": sum(1 for m in self.metrics if m.success),
                "failed_requests": sum(1 for m in self.metrics if not m.success)
            },
            "endpoints": {}
        }
        
        for endpoint, metrics in by_endpoint.items():
            latencies = [m.latency_ms for m in metrics if m.success]
            
            if latencies:
                analysis["endpoints"][endpoint] = {
                    "total_requests": len(metrics),
                    "successful": len(latencies),
                    "failed": len(metrics) - len(latencies),
                    "latency": {
                        "mean": statistics.mean(latencies),
                        "median": statistics.median(latencies),
                        "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0,
                        "min": min(latencies),
                        "max": max(latencies),
                        "p50": sorted(latencies)[int(len(latencies) * 0.50)],
                        "p95": sorted(latencies)[int(len(latencies) * 0.95)],
                        "p99": sorted(latencies)[int(len(latencies) * 0.99)]
                    }
                }
        
        return analysis
    
    def detect_bottlenecks(self, analysis: Dict) -> List[Dict]:
        """Detect performance bottlenecks"""
        bottlenecks = []
        
        for endpoint, data in analysis.get("endpoints", {}).items():
            latency = data.get("latency", {})
            
            # High average latency
            if latency.get("mean", 0) > 100:
                bottlenecks.append({
                    "type": "high_latency",
                    "endpoint": endpoint,
                    "severity": "warning",
                    "message": f"Average latency {latency['mean']:.2f}ms exceeds 100ms threshold",
                    "value": latency["mean"]
                })
            
            # High P95 latency
            if latency.get("p95", 0) > 500:
                bottlenecks.append({
                    "type": "high_p95",
                    "endpoint": endpoint,
                    "severity": "critical",
                    "message": f"P95 latency {latency['p95']:.2f}ms exceeds 500ms threshold",
                    "value": latency["p95"]
                })
            
            # High failure rate
            failure_rate = data.get("failed", 0) / data.get("total_requests", 1)
            if failure_rate > 0.05:  # 5% threshold
                bottlenecks.append({
                    "type": "high_failure_rate",
                    "endpoint": endpoint,
                    "severity": "critical",
                    "message": f"Failure rate {failure_rate:.1%} exceeds 5% threshold",
                    "value": failure_rate
                })
        
        return bottlenecks
    
    def generate_html_report(self, output_file: str = "performance_report.html"):
        """Generate HTML performance report"""
        analysis = self.analyze_metrics()
        bottlenecks = self.detect_bottlenecks(analysis)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Sentinel Performance Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #0a0e1a;
            color: #e0e0e0;
        }}
        h1, h2, h3 {{
            color: #00d9ff;
        }}
        .metric-card {{
            background: #1a1f2e;
            border: 1px solid #2a3f5f;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .metric-item {{
            background: #0f1419;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #00d9ff;
        }}
        .metric-label {{
            font-size: 12px;
            color: #888;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #00d9ff;
        }}
        .bottleneck {{
            background: #2a1a1a;
            border-left: 4px solid #ff4444;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .bottleneck.warning {{
            border-left-color: #ffaa00;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #2a3f5f;
        }}
        th {{
            background: #1a1f2e;
            color: #00d9ff;
            font-weight: bold;
        }}
        .success {{ color: #10b981; }}
        .error {{ color: #ef4444; }}
    </style>
</head>
<body>
    <h1>🔬 Sentinel Performance Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="metric-card">
        <h2>Session Summary</h2>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-label">Duration</div>
                <div class="metric-value">{analysis['session']['duration_seconds']:.1f}s</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Total Requests</div>
                <div class="metric-value">{analysis['session']['total_requests']}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Successful</div>
                <div class="metric-value success">{analysis['session']['successful_requests']}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Failed</div>
                <div class="metric-value error">{analysis['session']['failed_requests']}</div>
            </div>
        </div>
    </div>
    
    <div class="metric-card">
        <h2>Endpoint Performance</h2>
        <table>
            <tr>
                <th>Endpoint</th>
                <th>Requests</th>
                <th>Success Rate</th>
                <th>Mean Latency</th>
                <th>P95 Latency</th>
                <th>P99 Latency</th>
            </tr>
"""
        
        for endpoint, data in analysis.get("endpoints", {}).items():
            success_rate = data['successful'] / data['total_requests'] * 100
            latency = data.get('latency', {})
            
            html += f"""
            <tr>
                <td><code>{endpoint}</code></td>
                <td>{data['total_requests']}</td>
                <td class="{'success' if success_rate > 95 else 'error'}">{success_rate:.1f}%</td>
                <td>{latency.get('mean', 0):.2f}ms</td>
                <td>{latency.get('p95', 0):.2f}ms</td>
                <td>{latency.get('p99', 0):.2f}ms</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
"""
        
        if bottlenecks:
            html += """
    <div class="metric-card">
        <h2>⚠️ Detected Bottlenecks</h2>
"""
            for bottleneck in bottlenecks:
                severity_class = bottleneck['severity']
                html += f"""
        <div class="bottleneck {severity_class}">
            <strong>{bottleneck['type'].upper()}</strong>: {bottleneck['message']}
            <br><small>Endpoint: <code>{bottleneck['endpoint']}</code></small>
        </div>
"""
            html += """
    </div>
"""
        
        html += """
    <div class="metric-card">
        <h2>📊 Raw Data</h2>
        <p>Total measurements collected: {}</p>
        <details>
            <summary>View JSON</summary>
            <pre>{}</pre>
        </details>
    </div>
</body>
</html>
""".format(len(self.metrics), json.dumps(analysis, indent=2))
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        print(f"\n✅ HTML report generated: {output_file}")
    
    def save_json_report(self, output_file: str = "performance_data.json"):
        """Save raw data as JSON"""
        analysis = self.analyze_metrics()
        
        report = {
            "analysis": analysis,
            "bottlenecks": self.detect_bottlenecks(analysis),
            "raw_metrics": [asdict(m) for m in self.metrics]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ JSON report saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Sentinel Performance Profiler")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL")
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    parser.add_argument("--interval", type=float, default=S60(1, 0, 0), help="Sampling interval")
    parser.add_argument("--output", default="performance_report.html", help="Output HTML file")
    parser.add_argument("--json", default="performance_data.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    print("="*80)
    print("SENTINEL PERFORMANCE PROFILER")
    print("="*80)
    print()
    
    profiler = PerformanceProfiler(args.url)
    profiler.run_profiling_session(args.duration, args.interval)
    
    # Generate reports
    profiler.generate_html_report(args.output)
    profiler.save_json_report(args.json)
    
    # Print summary
    analysis = profiler.analyze_metrics()
    bottlenecks = profiler.detect_bottlenecks(analysis)
    
    print("\n" + "="*80)
    print("PERFORMANCE SUMMARY")
    print("="*80)
    print(f"\nTotal Requests: {analysis['session']['total_requests']}")
    print(f"Success Rate: {analysis['session']['successful_requests'] / analysis['session']['total_requests'] * 100:.1f}%")
    
    if bottlenecks:
        print(f"\n⚠️  {len(bottlenecks)} bottleneck(s) detected:")
        for b in bottlenecks:
            print(f"  - {b['type']}: {b['message']}")
    else:
        print("\n✅ No bottlenecks detected!")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
