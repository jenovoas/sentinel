"""
Sentinel Vault - Finance Service
Aggregates Crypto + Manual Assets for Unified Dashboard
"""
import logging
from sqlalchemy.orm import Session
from database import Asset
from crypto_service import CryptoService
from typing import Dict, List, Optional
from datetime import datetime

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinanceService:
    def __init__(self, db: Session):
        self.db = db
        self.crypto_service = CryptoService()
        self.user_id = "test-user" # Placeholder for auth

    async def get_dashboard_summary(self) -> Dict:
        """Get total Net Worth and asset distribution"""
        # 1. Get Crypto Portfolio
        wallet_data = await self.crypto_service.get_wallet_status(self.user_id)
        
        crypto_total_usd = 0.0
        crypto_breakdown = {}
        
        if wallet_data and "wallets" in wallet_data:
            for chain, data in wallet_data["wallets"].items():
                val = data.get("balance_usd", 0.0) or 0.0
                if val > 0:
                    crypto_total_usd += val
                    crypto_breakdown[chain] = val

        # 2. Get Manual Assets
        manual_assets = self.db.query(Asset).filter(Asset.user_id == self.user_id).all()
        
        manual_total_usd = 0.0
        asset_list = []
        
        for asset in manual_assets:
            manual_total_usd += asset.value_usd
            asset_list.append({
                "id": asset.id,
                "name": asset.name,
                "category": asset.category,
                "value_usd": asset.value_usd,
                "currency": asset.currency
            })

        # 3. Calculate Total Net Worth
        total_net_worth = crypto_total_usd + manual_total_usd

        # 4. Prepare Chart Data (Distribution)
        distribution = {
            "Crypto": crypto_total_usd,
            "Fiat": 0.0, 
            "Real Estate": 0.0,
            "Stock": 0.0, 
            "Gold": 0.0,
            "Other": 0.0
        }
        
        for asset in manual_assets:
            cat = asset.category.title().replace("_", " ")
            if cat in distribution:
                distribution[cat] += asset.value_usd
            else:
                if "Real Estate" in cat: distribution["Real Estate"] += asset.value_usd
                else: distribution["Other"] += asset.value_usd

        # Format for Recharts
        chart_data = [
            {"name": k, "value": v} for k, v in distribution.items() if v > 0
        ]

        return {
            "net_worth": total_net_worth,
            "crypto_total": crypto_total_usd,
            "manual_total": manual_total_usd,
            "assets": asset_list,
            "crypto_breakdown": crypto_breakdown,
            "chart_data": chart_data
        }

    def add_asset(self, name: str, category: str, value_usd: float) -> Asset:
        """Add a manual asset"""
        asset = Asset(
            user_id=self.user_id,
            name=name,
            category=category,
            value_usd=value_usd,
            amount=1.0 
        )
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def delete_asset(self, asset_id: int):
        """Delete a manual asset"""
        asset = self.db.query(Asset).filter(Asset.id == asset_id, Asset.user_id == self.user_id).first()
        if asset:
            self.db.delete(asset)
            self.db.commit()
            return True
        return False
