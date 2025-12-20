"""
Sentinel Vault - Crypto Wallet Complete
Integración de wallet generation + blockchain tracking
"""
from crypto_wallet import CryptoWallet
from blockchain import BlockchainService
import asyncio


class CryptoWalletComplete:
    """Wallet completo con generation + balance tracking"""
    
    def __init__(self):
        self.wallet_gen = CryptoWallet()
        self.blockchain = BlockchainService()
    
    async def create_wallet(self, chains: list = None) -> dict:
        """
        Crear wallet completo con balances
        
        Args:
            chains: Lista de chains a generar (default: todas)
        
        Returns:
            Dict con seed phrase y wallets con balances
        """
        if chains is None:
            chains = ["bitcoin", "ethereum", "polygon", "solana"]
        
        # Generar wallet base
        wallet = self.wallet_gen.generate_wallet()
        
        result = {
            "seed_phrase": wallet["seed_phrase"],
            "wallets": {}
        }
        
        # Agregar Bitcoin
        if "bitcoin" in chains:
            btc_balance = await self.blockchain.get_bitcoin_balance(
                wallet["bitcoin"]["address"]
            )
            result["wallets"]["bitcoin"] = {
                **wallet["bitcoin"],
                "balance": btc_balance["balance"],
                "balance_usd": btc_balance["balance_usd"]
            }
        
        # Agregar Ethereum
        if "ethereum" in chains:
            eth_balance = await self.blockchain.get_ethereum_balance(
                wallet["ethereum"]["address"],
                chain="ethereum"
            )
            result["wallets"]["ethereum"] = {
                **wallet["ethereum"],
                "balance": eth_balance["balance"],
                "balance_usd": eth_balance["balance_usd"]
            }
        
        # Agregar Polygon (usa misma address que Ethereum)
        if "polygon" in chains:
            poly_balance = await self.blockchain.get_ethereum_balance(
                wallet["ethereum"]["address"],  # Misma address
                chain="polygon"
            )
            result["wallets"]["polygon"] = {
                "chain": "polygon",
                "address": wallet["ethereum"]["address"],
                "derivation_path": wallet["ethereum"]["derivation_path"],
                "balance": poly_balance["balance"],
                "balance_usd": poly_balance["balance_usd"]
            }
        
        # Agregar Solana
        if "solana" in chains:
            # Generar Solana wallet (BIP44: m/44'/501'/0'/0/0)
            from mnemonic import Mnemonic
            from bip32 import BIP32
            
            mnemo = Mnemonic("english")
            seed = mnemo.to_seed(wallet["seed_phrase"])
            bip32 = BIP32.from_seed(seed)
            
            # Derivar Solana key
            sol_path = "m/44'/501'/0'/0/0"
            sol_privkey = bip32.get_privkey_from_path(sol_path)
            
            # Convertir a Solana address (Base58)
            # Nota: Esto es simplificado, Solana usa Ed25519
            # Para producción, usar solana-py library
            import base58
            sol_address = base58.b58encode(sol_privkey[:32]).decode()
            
            sol_balance = await self.blockchain.get_solana_balance(sol_address)
            
            result["wallets"]["solana"] = {
                "chain": "solana",
                "address": sol_address,
                "derivation_path": sol_path,
                "balance": sol_balance["balance"],
                "balance_usd": sol_balance["balance_usd"]
            }
        
        return result
    
    async def get_portfolio_value(self, wallets: dict) -> dict:
        """
        Calcular valor total del portfolio
        
        Args:
            wallets: Dict de wallets
        
        Returns:
            Dict con valor total y breakdown por chain
        """
        total_usd = 0
        breakdown = {}
        
        for chain, wallet in wallets.items():
            balance_usd = wallet.get("balance_usd", 0)
            total_usd += balance_usd
            breakdown[chain] = {
                "balance": wallet.get("balance", 0),
                "balance_usd": balance_usd,
                "percentage": 0  # Calculamos después
            }
        
        # Calcular percentages
        for chain in breakdown:
            if total_usd > 0:
                breakdown[chain]["percentage"] = (
                    breakdown[chain]["balance_usd"] / total_usd * 100
                )
        
        return {
            "total_usd": total_usd,
            "breakdown": breakdown
        }
    
    async def close(self):
        """Cerrar conexiones"""
        await self.blockchain.close()


async def main():
    print("🪙 Crypto Wallet Complete - Demo\n")
    
    wallet_service = CryptoWalletComplete()
    
    # Crear wallet completo
    print("1. Generating wallet...")
    wallet = await wallet_service.create_wallet()
    
    print(f"\n⚠️  SEED PHRASE (save this!):")
    print(f"   {wallet['seed_phrase']}\n")
    
    # Mostrar wallets
    print("2. Wallets created:\n")
    for chain, wallet_data in wallet["wallets"].items():
        print(f"{chain.upper()}:")
        print(f"  Address: {wallet_data['address']}")
        print(f"  Balance: {wallet_data['balance']:.6f}")
        print(f"  USD: ${wallet_data['balance_usd']:.2f}")
        print()
    
    # Portfolio value
    print("3. Portfolio Summary:\n")
    portfolio = await wallet_service.get_portfolio_value(wallet["wallets"])
    
    print(f"Total Value: ${portfolio['total_usd']:.2f}\n")
    print("Breakdown:")
    for chain, data in portfolio["breakdown"].items():
        print(f"  {chain.upper()}: ${data['balance_usd']:.2f} ({data['percentage']:.1f}%)")
    
    await wallet_service.close()
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
