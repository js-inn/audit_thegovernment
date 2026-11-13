#!/usr/bin/env python3
import sqlite3
import unittest

class TestFullFederalAudit(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.db_path = "core_audit.db"
        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        cls.tables = [row[0] for row in cursor.fetchall()]
        conn.close()

    def test_all_portfolios_present(self):
        """Ensure Intergovernmental, FINTRAC, and Prior Art registries are loaded."""
        self.assertIn("portfolios", self.tables)
        self.assertIn("fintrac_portfolios", self.tables)
        self.assertIn("sovereign_prior_art_registry", self.tables)
        self.assertIn("ministerial_enforcement_log", self.tables)

    def test_ministerial_ban_enforced(self):
        """Confirm Dominic LeBlanc's portfolio remains banned pending verification."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT pipeline_status FROM portfolios WHERE portfolio_id = 'P_INT_01';")
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "AUTOMATED_BAN_PENDING_VERIFICATION")

    def test_fintrac_authorities_and_intelligence(self):
        """Verify FINTRAC financial authorities and compliance breakdown."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fintrac_portfolios WHERE entity_id = 'FINTRAC-INT-01';")
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["total_authorities_cad"], 128276000.0)
        self.assertEqual(row["planned_ftes"], 581)

if __name__ == "__main__":
    unittest.main()
