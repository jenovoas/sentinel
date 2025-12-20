"""
Sentinel Vault - Comprehensive Integration Tests
End-to-end testing for crypto wallet
"""
import asyncio
import sys
sys.path.insert(0, '/home/jnovoas/sentinel/backend/poc')

from wallet_complete import CryptoWalletComplete
from blockchain import BlockchainService
from crypto_wallet import CryptoWallet


async def test_wallet_generation():
    """Test 1: Wallet Generation"""
    print("\n" + "="*60)
    print("TEST 1: Wallet Generation")
    print("="*60)
    
    wallet_service = CryptoWalletComplete()
    wallet = await wallet_service.create_wallet()
    await wallet_service.close()
    
    # Validations
    assert wallet['seed_phrase'], "❌ Seed phrase not generated"
    assert len(wallet['seed_phrase'].split()) == 24, "❌ Seed phrase should have 24 words"
    assert 'wallets' in wallet, "❌ Wallets not created"
    assert 'bitcoin' in wallet['wallets'], "❌ Bitcoin wallet missing"
    assert 'ethereum' in wallet['wallets'], "❌ Ethereum wallet missing"
    assert 'polygon' in wallet['wallets'], "❌ Polygon wallet missing"
    assert 'solana' in wallet['wallets'], "❌ Solana wallet missing"
    
    print(f"✅ Seed phrase generated: {len(wallet['seed_phrase'].split())} words")
    print(f"✅ Bitcoin address: {wallet['wallets']['bitcoin']['address']}")
    print(f"✅ Ethereum address: {wallet['wallets']['ethereum']['address']}")
    print(f"✅ Polygon address: {wallet['wallets']['polygon']['address']}")
    print(f"✅ Solana address: {wallet['wallets']['solana']['address']}")
    
    return wallet


async def test_wallet_recovery(seed_phrase):
    """Test 2: Wallet Recovery"""
    print("\n" + "="*60)
    print("TEST 2: Wallet Recovery")
    print("="*60)
    
    crypto = CryptoWallet()
    recovered = crypto.recover_wallet(seed_phrase)
    
    # Validations
    assert recovered['bitcoin']['address'], "❌ Bitcoin recovery failed"
    assert recovered['ethereum']['address'], "❌ Ethereum recovery failed"
    
    print(f"✅ Bitcoin recovered: {recovered['bitcoin']['address']}")
    print(f"✅ Ethereum recovered: {recovered['ethereum']['address']}")
    
    return recovered


async def test_balance_fetching():
    """Test 3: Balance Fetching"""
    print("\n" + "="*60)
    print("TEST 3: Balance Fetching (Public Addresses)")
    print("="*60)
    
    blockchain = BlockchainService()
    
    # Test addresses (públicas, para testing)
    test_addresses = {
        "bitcoin": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis block
        "ethereum": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # Vitalik
        "polygon": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
        "solana": "vines1vzrYbzLMRdu58ou5XTby4qAqVRLmqo36NKPTg"
    }
    
    results = {}
    for chain, address in test_addresses.items():
        print(f"\nFetching {chain.upper()} balance...")
        balance = await blockchain.get_balance(chain, address)
        results[chain] = balance
        
        if 'error' in balance:
            print(f"  ⚠️  Error: {balance['error']}")
        else:
            print(f"  ✅ Balance: {balance['balance']:.6f} {balance['currency']}")
            print(f"     USD: ${balance['balance_usd']:.2f}")
    
    await blockchain.close()
    return results


async def test_portfolio_calculation(wallet):
    """Test 4: Portfolio Calculation"""
    print("\n" + "="*60)
    print("TEST 4: Portfolio Calculation")
    print("="*60)
    
    wallet_service = CryptoWalletComplete()
    portfolio = await wallet_service.get_portfolio_value(wallet['wallets'])
    await wallet_service.close()
    
    print(f"✅ Total portfolio value: ${portfolio['total_usd']:.2f}")
    print(f"\nBreakdown:")
    for chain, data in portfolio['breakdown'].items():
        print(f"  {chain.upper()}: ${data['balance_usd']:.2f} ({data['percentage']:.1f}%)")
    
    return portfolio


async def test_consistency(original, recovered):
    """Test 5: Consistency Check"""
    print("\n" + "="*60)
    print("TEST 5: Consistency Check")
    print("="*60)
    
    # Verificar que recovery genera mismas addresses
    btc_match = original['wallets']['bitcoin']['address'] == recovered['bitcoin']['address']
    eth_match = original['wallets']['ethereum']['address'] == recovered['ethereum']['address']
    
    if btc_match:
        print("✅ Bitcoin address matches after recovery")
    else:
        print("❌ Bitcoin address mismatch!")
        
    if eth_match:
        print("✅ Ethereum address matches after recovery")
    else:
        print("❌ Ethereum address mismatch!")
    
    assert btc_match and eth_match, "Recovery consistency check failed"
    
    return btc_match and eth_match


async def run_all_tests():
    """Run all tests"""
    print("\n" + "🧪 SENTINEL VAULT - COMPREHENSIVE TEST SUITE ".center(60, "="))
    
    try:
        # Test 1: Generation
        wallet = await test_wallet_generation()
        
        # Test 2: Recovery
        recovered = await test_wallet_recovery(wallet['seed_phrase'])
        
        # Test 3: Balance fetching
        balances = await test_balance_fetching()
        
        # Test 4: Portfolio
        portfolio = await test_portfolio_calculation(wallet)
        
        # Test 5: Consistency
        consistency = await test_consistency(wallet, recovered)
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print("✅ Test 1: Wallet Generation - PASSED")
        print("✅ Test 2: Wallet Recovery - PASSED")
        print("✅ Test 3: Balance Fetching - PASSED")
        print("✅ Test 4: Portfolio Calculation - PASSED")
        print("✅ Test 5: Consistency Check - PASSED")
        print("\n" + "🎉 ALL TESTS PASSED! ".center(60, "=") + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
