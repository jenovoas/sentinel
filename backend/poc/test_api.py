"""
Test script para Sentinel Vault POC API
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health check"""
    print("\n=== Test 1: Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200


def test_vault_flow():
    """Test complete vault flow"""
    print("\n=== Test 2: Vault Flow ===")
    
    master_password = "my-super-secret-master-password-123"
    
    # 1. Unlock vault
    print("\n1. Unlocking vault...")
    response = requests.post(
        f"{BASE_URL}/vault/unlock",
        json={"master_password": master_password}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    
    # 2. Save password
    print("\n2. Saving password...")
    response = requests.post(
        f"{BASE_URL}/vault/save",
        json={
            "master_password": master_password,
            "service": "github",
            "username": "jnovoas",
            "password": "github-secret-password-456"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    
    # 3. List passwords
    print("\n3. Listing passwords...")
    response = requests.get(f"{BASE_URL}/vault/list")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    
    # 4. Get password
    print("\n4. Getting password...")
    response = requests.post(
        f"{BASE_URL}/vault/get",
        json={
            "master_password": master_password,
            "service": "github"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json()["password"] == "github-secret-password-456"


def test_password_analysis():
    """Test Ollama password analysis"""
    print("\n=== Test 3: Password Analysis (Ollama) ===")
    
    test_passwords = [
        "password123",
        "MyDog2024",
        "MyP@ssw0rd2024",
        "Xk9$mQ2#vL8@pR4&nT6"
    ]
    
    for pwd in test_passwords:
        print(f"\nAnalyzing: {pwd}")
        response = requests.post(
            f"{BASE_URL}/analyze/password",
            json={"password": pwd}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Score: {result['score']}/100")
            print(f"  Issues: {', '.join(result['issues']) if result['issues'] else 'None'}")
            print(f"  Has patterns: {result.get('has_patterns', False)}")
        else:
            print(f"  Error: {response.status_code}")


def test_crypto_wallet():
    """Test crypto wallet generation"""
    print("\n=== Test 4: Crypto Wallet Generation ===")
    
    # 1. Generate wallet
    print("\n1. Generating wallet...")
    response = requests.post(f"{BASE_URL}/crypto/generate")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        wallet = response.json()
        print(f"\n⚠️  SEED PHRASE (save this!):")
        print(f"   {wallet['seed_phrase']}")
        print(f"\nBitcoin: {wallet['bitcoin']['address']}")
        print(f"Ethereum: {wallet['ethereum']['address']}")
        
        # 2. Recover wallet
        print("\n2. Recovering wallet from seed phrase...")
        response = requests.post(
            f"{BASE_URL}/crypto/recover",
            params={"seed_phrase": wallet['seed_phrase']}
        )
        
        if response.status_code == 200:
            recovered = response.json()
            assert recovered['bitcoin']['address'] == wallet['bitcoin']['address']
            assert recovered['ethereum']['address'] == wallet['ethereum']['address']
            print("✅ Recovery successful!")
    else:
        print(f"Error: {response.status_code}")


def test_benchmarks():
    """Test benchmarks"""
    print("\n=== Test 5: Benchmarks ===")
    
    # 1. Encryption benchmark
    print("\n1. Encryption benchmark...")
    response = requests.get(f"{BASE_URL}/benchmark/encryption")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Key derivation avg: {result['key_derivation']['average_ms']:.2f}ms")
        print(f"Encryption avg: {result['encryption']['encryption']['average_ms']:.3f}ms")
        print(f"Decryption avg: {result['encryption']['decryption']['average_ms']:.3f}ms")
    
    # 2. Ollama benchmark
    print("\n2. Ollama benchmark...")
    response = requests.get(f"{BASE_URL}/benchmark/ollama")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Overall average: {result['overall_average_ms']:.2f}ms")


if __name__ == "__main__":
    print("🧪 Sentinel Vault POC - API Tests")
    print("=" * 50)
    
    try:
        test_health()
        test_vault_flow()
        test_password_analysis()
        test_crypto_wallet()
        test_benchmarks()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: API not running. Start with: python main.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
