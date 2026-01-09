from quantum.sentinel_quantum_core import SentinelQuantumCore, SentinelConfig, SentinelQAOA
from quantum.yatra_core import S60

def test_qaoa_optimization():
    print("🧪 Testing QAOA Optimization (S60)...")
    config = SentinelConfig(N_membranes=2)
    core = SentinelQuantumCore(config)
    qaoa = SentinelQAOA(core)
    
    # Run optimization for 5 steps
    result = qaoa.optimize(steps=5)
    
    print(f"   Optimal Params: {result['optimal_params']}")
    print(f"   Min Cost: {result['min_cost']}")
    
    assert result['success'] is True
    assert result['min_cost'] <= S60(0), "QAOA should find some negative cost for 'W' state target"
    print("✅ QAOA Optimization OK")

if __name__ == "__main__":
    try:
        test_qaoa_optimization()
        print("\n🏆 QAOA TEST PASSED")
    except Exception as e:
        print(f"❌ QAOA TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
