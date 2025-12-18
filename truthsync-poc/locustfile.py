"""
Locust Load Testing Script for TruthSync
Uses synthetic dataset to simulate realistic traffic patterns
"""

from locust import HttpUser, task, between, events
import random
import json
import time


# Load synthetic dataset
with open('synthetic_claims_10k.json', 'r') as f:
    dataset = json.load(f)

CLAIMS = dataset['claims']
ACCESS_PATTERN = dataset['access_pattern']
current_request = 0


class TruthSyncUser(HttpUser):
    """Simulates a TruthSync API user"""
    
    wait_time = between(0.001, 0.01)  # 1-10ms between requests
    
    def on_start(self):
        """Initialize user session"""
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
    
    @task(100)
    def verify_claim(self):
        """Verify a single claim (realistic access pattern)"""
        global current_request
        
        # Get claim from access pattern (simulates cache behavior)
        claim_id = ACCESS_PATTERN[current_request % len(ACCESS_PATTERN)]
        claim = CLAIMS[claim_id]
        
        current_request += 1
        self.request_count += 1
        
        # Make request
        with self.client.post(
            "/verify",
            json={"text": claim['text']},
            catch_response=True,
            name="verify_claim"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                
                # Track cache performance
                if result.get('cache_hit'):
                    self.cache_hits += 1
                else:
                    self.cache_misses += 1
                
                # Validate response
                if 'claims' not in result:
                    response.failure("Missing 'claims' in response")
                elif 'confidence' not in result:
                    response.failure("Missing 'confidence' in response")
                else:
                    response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(10)
    def verify_batch(self):
        """Verify batch of claims"""
        batch_size = random.randint(10, 100)
        batch_claims = random.sample(CLAIMS, min(batch_size, len(CLAIMS)))
        
        requests = [{"text": claim['text']} for claim in batch_claims]
        
        with self.client.post(
            "/verify/batch",
            json=requests,
            catch_response=True,
            name="verify_batch"
        ) as response:
            if response.status_code == 200:
                results = response.json()
                if len(results) == len(requests):
                    response.success()
                else:
                    response.failure(f"Expected {len(requests)} results, got {len(results)}")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/health", name="health_check")
    
    @task(1)
    def get_stats(self):
        """Get system stats"""
        self.client.get("/stats", name="get_stats")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print final statistics"""
    print("\n" + "="*70)
    print("LOAD TEST SUMMARY")
    print("="*70)
    
    stats = environment.stats
    
    print(f"\n📊 Request Statistics:")
    print(f"  Total requests: {stats.total.num_requests:,}")
    print(f"  Failures: {stats.total.num_failures:,}")
    print(f"  Success rate: {(1 - stats.total.fail_ratio)*100:.2f}%")
    
    print(f"\n⚡ Performance:")
    print(f"  RPS: {stats.total.total_rps:.0f}")
    print(f"  Median latency: {stats.total.median_response_time:.2f}ms")
    print(f"  P95 latency: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"  P99 latency: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    
    print(f"\n🎯 Success Criteria:")
    criteria = [
        ("Success rate > 99%", (1 - stats.total.fail_ratio) > 0.99),
        ("P99 latency < 10ms", stats.total.get_response_time_percentile(0.99) < 10),
        ("RPS > 1000", stats.total.total_rps > 1000),
    ]
    
    for criterion, passed in criteria:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {criterion}")
