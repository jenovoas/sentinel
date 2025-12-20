"""
Sentinel Vault - Blockchain Integration
Balance and transaction tracking para crypto wallets
"""
import httpx
from typing import Optional, Dict, List


class BlockchainService:
    """Service para interactuar con blockchains"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=10.0)
    
    # ========================================================================
    # Bitcoin
    # ========================================================================
    
    async def get_bitcoin_balance(self, address: str) -> Dict:
        """
        Obtener balance de Bitcoin usando Blockchain.info API
        
        Args:
            address: Bitcoin address (P2PKH)
        
        Returns:
            Dict con balance en BTC y USD
        """
        try:
            # Balance en satoshis
            url = f"https://blockchain.info/q/addressbalance/{address}"
            response = await self.http_client.get(url)
            satoshis = int(response.text)
            btc = satoshis / 100_000_000  # Convertir a BTC
            
            # Precio actual de BTC
            price_url = "https://blockchain.info/ticker"
            price_response = await self.http_client.get(price_url)
            price_data = price_response.json()
            usd_price = price_data["USD"]["last"]
            
            return {
                "chain": "bitcoin",
                "address": address,
                "balance": btc,
                "balance_usd": btc * usd_price,
                "currency": "BTC"
            }
        
        except Exception as e:
            print(f"Error fetching Bitcoin balance: {e}")
            return {
                "chain": "bitcoin",
                "address": address,
                "balance": 0,
                "balance_usd": 0,
                "currency": "BTC",
                "error": str(e)
            }
    
    async def get_bitcoin_transactions(self, address: str, limit: int = 10) -> List[Dict]:
        """
        Obtener transacciones de Bitcoin
        
        Args:
            address: Bitcoin address
            limit: Número máximo de transacciones
        
        Returns:
            Lista de transacciones
        """
        try:
            url = f"https://blockchain.info/rawaddr/{address}?limit={limit}"
            response = await self.http_client.get(url)
            data = response.json()
            
            transactions = []
            for tx in data.get("txs", []):
                # Calcular si es incoming o outgoing
                value = 0
                tx_type = "unknown"
                
                for output in tx.get("out", []):
                    if output.get("addr") == address:
                        value += output.get("value", 0)
                        tx_type = "incoming"
                
                for input_tx in tx.get("inputs", []):
                    prev_out = input_tx.get("prev_out", {})
                    if prev_out.get("addr") == address:
                        value -= prev_out.get("value", 0)
                        tx_type = "outgoing"
                
                transactions.append({
                    "hash": tx.get("hash"),
                    "type": tx_type,
                    "value": abs(value) / 100_000_000,  # BTC
                    "timestamp": tx.get("time"),
                    "confirmations": tx.get("block_height", 0)
                })
            
            return transactions
        
        except Exception as e:
            print(f"Error fetching Bitcoin transactions: {e}")
            return []
    
    # ========================================================================
    # Ethereum (también funciona para Polygon)
    # ========================================================================
    
    async def get_ethereum_balance(
        self, 
        address: str, 
        chain: str = "ethereum",
        rpc_url: Optional[str] = None
    ) -> Dict:
        """
        Obtener balance de Ethereum o Polygon
        
        Args:
            address: Ethereum address (0x...)
            chain: 'ethereum' o 'polygon'
            rpc_url: RPC URL (opcional, usa público si no se provee)
        
        Returns:
            Dict con balance en ETH/MATIC y USD
        """
        try:
            # RPC URLs públicos
            if not rpc_url:
                if chain == "ethereum":
                    rpc_url = "https://eth.llamarpc.com"
                elif chain == "polygon":
                    rpc_url = "https://polygon-rpc.com"
            
            # Llamada RPC para obtener balance
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [address, "latest"],
                "id": 1
            }
            
            response = await self.http_client.post(rpc_url, json=payload)
            data = response.json()
            
            # Balance en wei
            wei = int(data["result"], 16)
            eth = wei / 1e18  # Convertir a ETH/MATIC
            
            # Precio actual (usar CoinGecko)
            coin_id = "ethereum" if chain == "ethereum" else "matic-network"
            price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            price_response = await self.http_client.get(price_url)
            price_data = price_response.json()
            usd_price = price_data[coin_id]["usd"]
            
            currency = "ETH" if chain == "ethereum" else "MATIC"
            
            return {
                "chain": chain,
                "address": address,
                "balance": eth,
                "balance_usd": eth * usd_price,
                "currency": currency
            }
        
        except Exception as e:
            print(f"Error fetching {chain} balance: {e}")
            return {
                "chain": chain,
                "address": address,
                "balance": 0,
                "balance_usd": 0,
                "currency": "ETH" if chain == "ethereum" else "MATIC",
                "error": str(e)
            }
    
    # ========================================================================
    # Solana
    # ========================================================================
    
    async def get_solana_balance(self, address: str) -> Dict:
        """
        Obtener balance de Solana
        
        Args:
            address: Solana address (Base58)
        
        Returns:
            Dict con balance en SOL y USD
        """
        try:
            # RPC público de Solana
            rpc_url = "https://api.mainnet-beta.solana.com"
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [address]
            }
            
            response = await self.http_client.post(rpc_url, json=payload)
            data = response.json()
            
            # Balance en lamports
            lamports = data["result"]["value"]
            sol = lamports / 1e9  # Convertir a SOL
            
            # Precio actual
            price_url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
            price_response = await self.http_client.get(price_url)
            price_data = price_response.json()
            usd_price = price_data["solana"]["usd"]
            
            return {
                "chain": "solana",
                "address": address,
                "balance": sol,
                "balance_usd": sol * usd_price,
                "currency": "SOL"
            }
        
        except Exception as e:
            print(f"Error fetching Solana balance: {e}")
            return {
                "chain": "solana",
                "address": address,
                "balance": 0,
                "balance_usd": 0,
                "currency": "SOL",
                "error": str(e)
            }
    
    # ========================================================================
    # Multi-chain helper
    # ========================================================================
    
    async def get_balance(self, chain: str, address: str) -> Dict:
        """
        Obtener balance para cualquier chain
        
        Args:
            chain: 'bitcoin', 'ethereum', 'polygon', 'solana'
            address: Wallet address
        
        Returns:
            Dict con balance
        """
        if chain == "bitcoin":
            return await self.get_bitcoin_balance(address)
        elif chain == "ethereum":
            return await self.get_ethereum_balance(address, chain="ethereum")
        elif chain == "polygon":
            return await self.get_ethereum_balance(address, chain="polygon")
        elif chain == "solana":
            return await self.get_solana_balance(address)
        else:
            raise ValueError(f"Unsupported chain: {chain}")
    
    async def close(self):
        """Cerrar HTTP client"""
        await self.http_client.aclose()


# ============================================================================
# Testing
# ============================================================================

async def main():
    print("🔗 Blockchain Service - Testing\n")
    
    blockchain = BlockchainService()
    
    # Test addresses (públicas, para testing)
    test_addresses = {
        "bitcoin": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis block
        "ethereum": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # Vitalik
        "polygon": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # Same as ETH
        "solana": "vines1vzrYbzLMRdu58ou5XTby4qAqVRLmqo36NKPTg"  # Random
    }
    
    for chain, address in test_addresses.items():
        print(f"Testing {chain.upper()}...")
        balance = await blockchain.get_balance(chain, address)
        
        if "error" in balance:
            print(f"  ❌ Error: {balance['error']}")
        else:
            print(f"  ✅ Balance: {balance['balance']:.6f} {balance['currency']}")
            print(f"     USD: ${balance['balance_usd']:.2f}")
        print()
    
    # Test Bitcoin transactions
    print("Testing Bitcoin transactions...")
    txs = await blockchain.get_bitcoin_transactions(test_addresses["bitcoin"], limit=5)
    print(f"  Found {len(txs)} transactions")
    for tx in txs[:3]:
        print(f"    - {tx['type']}: {tx['value']:.6f} BTC")
    
    await blockchain.close()
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
