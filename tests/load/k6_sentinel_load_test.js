// k6 Load Test for Sentinel Cortex
// Tests throughput and latency under high concurrent load

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const syscallLatency = new Trend('syscall_interception_latency');
const cortexLatency = new Trend('cortex_decision_latency');

// Test configuration
export const options = {
    stages: [
        { duration: '30s', target: 100 },    // Ramp-up to 100 users
        { duration: '1m', target: 1000 },    // Ramp-up to 1000 users
        { duration: '2m', target: 5000 },    // Stress test with 5000 users
        { duration: '1m', target: 1000 },    // Ramp-down
        { duration: '30s', target: 0 },      // Cool down
    ],
    thresholds: {
        'http_req_duration': ['p(95)<500', 'p(99)<1000'],  // 95% < 500ms, 99% < 1s
        'http_req_failed': ['rate<0.01'],  // Error rate < 1%
        'syscall_interception_latency': ['p(99)<1'],  // 99% < 1ms
        'cortex_decision_latency': ['p(95)<200'],  // 95% < 200ms
        'errors': ['rate<0.01'],
    },
};

const BASE_URL = __ENV.SENTINEL_URL || 'http://localhost:8080';

export default function () {
    // Test 1: Telemetry Ingest (simulate 8,603 log streams)
    const telemetryPayload = {
        logs: Array(100).fill(null).map(() => ({
            timestamp: new Date().toISOString(),
            message: 'DROP TABLE users;',  // Malicious pattern
            source: 'app_log',
            level: 'info',
        })),
    };

    const telemetryResponse = http.post(
        `${BASE_URL}/api/telemetry/ingest`,
        JSON.stringify(telemetryPayload),
        {
            headers: { 'Content-Type': 'application/json' },
            tags: { name: 'TelemetryIngest' },
        }
    );

    check(telemetryResponse, {
        'Telemetry ingested': (r) => r.status === 200,
        'Response time < 10ms': (r) => r.timings.duration < 10,
    }) || errorRate.add(1);

    // Test 2: Cortex AI Threat Analysis
    const threatQuery = {
        pattern: 'DROP TABLE',
        confidence_required: 0.9,
        context: 'SQL query from user input',
    };

    const cortexResponse = http.post(
        `${BASE_URL}/api/cortex/threat-analysis`,
        JSON.stringify(threatQuery),
        {
            headers: { 'Content-Type': 'application/json' },
            tags: { name: 'CortexThreatAnalysis' },
        }
    );

    check(cortexResponse, {
        'Threat analysis responds': (r) => r.status === 200,
        'Decision latency < 200ms': (r) => r.timings.duration < 200,
        'Threat detected': (r) => r.json('threat_detected') === true,
    }) || errorRate.add(1);

    if (cortexResponse.status === 200) {
        cortexLatency.add(cortexResponse.timings.duration);
    }

    // Test 3: Guardian-Alpha Syscall Interception
    const syscallPayload = {
        syscall_nr: 59,  // execve
        args: ['/bin/sh', '-c', 'DROP TABLE users;'],
        pid: Math.floor(Math.random() * 10000),
        timestamp: Date.now(),
    };

    const guardianResponse = http.post(
        `${BASE_URL}/api/guardian/syscall-intercept`,
        JSON.stringify(syscallPayload),
        {
            headers: { 'Content-Type': 'application/json' },
            tags: { name: 'GuardianSyscallIntercept' },
        }
    );

    check(guardianResponse, {
        'Guardian intercepts': (r) => r.status === 200,
        'Interception < 1ms': (r) => r.timings.duration < 1,
        'Decision is BLOCK': (r) => r.json('decision') === 'BLOCK',
    }) || errorRate.add(1);

    if (guardianResponse.status === 200) {
        syscallLatency.add(guardianResponse.timings.duration);
    }

    // Test 4: Audit Log Persistence
    const auditEvent = {
        action: 'BLOCK',
        reason: 'Pattern match: DROP_TABLE',
        guardian: 'Alpha',
        syscall_nr: 59,
        timestamp: new Date().toISOString(),
        metadata: {
            pid: syscallPayload.pid,
            pattern: 'DROP TABLE',
        },
    };

    const auditResponse = http.post(
        `${BASE_URL}/api/audit/log`,
        JSON.stringify(auditEvent),
        {
            headers: { 'Content-Type': 'application/json' },
            tags: { name: 'AuditLogPersistence' },
        }
    );

    check(auditResponse, {
        'Audit logged': (r) => r.status === 200,
        'Immutable write': (r) => r.headers['X-Audit-ID'] !== undefined,
        'Write latency < 50ms': (r) => r.timings.duration < 50,
    }) || errorRate.add(1);

    // Small delay between iterations
    sleep(0.1);
}

export function handleSummary(data) {
    return {
        'load_test_results.json': JSON.stringify(data, null, 2),
        stdout: textSummary(data, { indent: ' ', enableColors: true }),
    };
}

function textSummary(data, options) {
    const indent = options.indent || '';
    const enableColors = options.enableColors || false;

    let summary = '\n';
    summary += `${indent}Test Summary:\n`;
    summary += `${indent}  Duration: ${data.state.testRunDurationMs / 1000}s\n`;
    summary += `${indent}  Iterations: ${data.metrics.iterations.values.count}\n`;
    summary += `${indent}  VUs: ${data.metrics.vus.values.value}\n`;
    summary += `${indent}\n`;
    summary += `${indent}HTTP Metrics:\n`;
    summary += `${indent}  Requests: ${data.metrics.http_reqs.values.count}\n`;
    summary += `${indent}  Failed: ${data.metrics.http_req_failed.values.rate * 100}%\n`;
    summary += `${indent}  Duration (p95): ${data.metrics.http_req_duration.values['p(95)']}ms\n`;
    summary += `${indent}  Duration (p99): ${data.metrics.http_req_duration.values['p(99)']}ms\n`;
    summary += `${indent}\n`;
    summary += `${indent}Custom Metrics:\n`;
    summary += `${indent}  Error Rate: ${data.metrics.errors.values.rate * 100}%\n`;
    summary += `${indent}  Syscall Latency (p99): ${data.metrics.syscall_interception_latency.values['p(99)']}ms\n`;
    summary += `${indent}  Cortex Latency (p95): ${data.metrics.cortex_decision_latency.values['p(95)']}ms\n`;

    return summary;
}
