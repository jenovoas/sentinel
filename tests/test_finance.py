import sys
import os
import asyncio
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend/poc to path
sys.path.append(os.path.join(os.getcwd(), 'backend/poc'))

from database import Base, Asset
from finance_service import FinanceService

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_finance.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestFinanceService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./test_finance.db"):
            os.remove("./test_finance.db")

    def setUp(self):
        self.db = TestingSessionLocal()
        self.service = FinanceService(self.db)

    def tearDown(self):
        self.db.close()

    def test_finance_flow(self):
        # We need to run async methods in a sync test wrapper
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        print("\n💰 Testing Finance Service (Unittest)...")

        # 1. Add Asset
        print("1. Adding 'Gold Bar'...")
        asset = self.service.add_asset("Gold Bar", "gold", 2000.0)
        self.assertIsNotNone(asset.id)
        self.assertEqual(asset.value_usd, 2000.0)
        print("   ✅ Asset added.")

        # 2. Get Summary
        print("2. Fetching Summary...")
        summary = loop.run_until_complete(self.service.get_dashboard_summary())
        
        print(f"   Net Worth: ${summary['net_worth']}")
        print(f"   Manual Total: ${summary['manual_total']}")
        
        self.assertEqual(summary['manual_total'], 2000.0)
        self.assertGreaterEqual(summary['net_worth'], 2000.0)
        self.assertEqual(len(summary['assets']), 1)
        print("   ✅ Summary correct.")

        # 3. Delete Asset
        print("3. Deleting Asset...")
        res = self.service.delete_asset(asset.id)
        self.assertTrue(res)
        
        summary_after = loop.run_until_complete(self.service.get_dashboard_summary())
        self.assertEqual(summary_after['manual_total'], 0.0)
        print("   ✅ Asset deleted.")
        
        loop.close()

if __name__ == "__main__":
    unittest.main()
