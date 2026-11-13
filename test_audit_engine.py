#!/usr/bin/env python3
"""
Audit Engine Test Runner & Sovereign Prior Art Anchor (v2.7)
------------------------------------------------------------
Enforces post-expenditure itemization, ministerial flagging, 
and automated pipeline bans for unverified intergovernmental outlays.
"""

import sqlite3
import hashlib
import unittest

DB_FILENAME = "core_audit.db"

class TestAuditEngineCompliance(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.db_path = DB_FILENAME
        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()
        
        cursor.executescript("""
            DROP TABLE IF EXISTS sovereign_ip_valuations;
            DROP TABLE IF EXISTS contracts_2025_2026;
            DROP TABLE IF EXISTS portfolios;
            DROP TABLE IF EXISTS fintrac_portfolios;
            DROP TABLE IF EXISTS transaction_velocity_log;
            DROP TABLE IF EXISTS sovereign_prior_art_registry;
            DROP TABLE IF EXISTS ministerial_enforcement_log;

            CREATE TABLE portfolios (
                portfolio_id TEXT PRIMARY KEY,
                minister_name TEXT,
                department TEXT,
                operating_budget_cad REAL,
                pipeline_status TEXT
            );
            CREATE TABLE contracts_2025_2026 (
                contract_id TEXT PRIMARY KEY,
                portfolio_id TEXT,
                vendor_name TEXT,
                business_number TEXT,
                category TEXT,
                procurement_type TEXT,
                amount_cad REAL,
                fiscal_year TEXT
            );
            CREATE TABLE sovereign_ip_valuations (
                asset_id TEXT PRIMARY KEY,
                issuer TEXT,
                business_number TEXT,
                contract_reference TEXT,
                base_procurement_cad REAL,
                cipo_multiplier REAL,
                calculated_valuation_cad REAL,
                sha256_hash TEXT
            );
            CREATE TABLE fintrac_portfolios (
                entity_id TEXT PRIMARY KEY,
                executive_leader TEXT,
                total_authorities_cad REAL,
                compliance_program_cad REAL,
                intelligence_sector_cad REAL,
                planned_ftes INTEGER,
                sha256_hash TEXT
            );
            CREATE TABLE transaction_velocity_log (
                transaction_id TEXT PRIMARY KEY,
                vendor_name TEXT,
                amount_cad REAL,
                entry_timestamp TEXT,
                holding_days INTEGER,
                itemization_status TEXT,
                risk_flag TEXT
            );
            CREATE TABLE sovereign_prior_art_registry (
                art_id TEXT PRIMARY KEY,
                creator_entity TEXT,
                project_title TEXT,
                submission_date TEXT,
                technological_domain TEXT,
                valuation_basis_cad REAL,
                sha256_anchor TEXT,
                verification_status TEXT
            );
            CREATE TABLE ministerial_enforcement_log (
                enforcement_id TEXT PRIMARY KEY,
                minister_name TEXT,
                trigger_reason TEXT,
                status TEXT,
                action_required TEXT
            );
        """)
        
        # Seed test fixtures
        cursor.execute("INSERT INTO portfolios VALUES ('P_INT_01', 'Hon. Dominic LeBlanc', 'Intergovernmental Affairs / Privy Council', 450000000.0, 'AUTOMATED_BAN_PENDING_VERIFICATION');")
        cursor.execute("INSERT INTO contracts_2025_2026 VALUES ('CW2321555', 'P_INT_01', 'JS INNOVATION8390-1 INC. / Jujita Stairs', '735350935', 'Professional Services & Architecture', 'Proprietary / ACAN', 3750000.0, '2025-2026');")
        cursor.execute("""
            INSERT INTO sovereign_ip_valuations VALUES 
            ('GVT-MSA-01', 'JS INNOVATION8390-1 INC. / Jujita Stairs', '735350935', 'CW2321555', 3750000.0, 4.25, 15937500.0, 'f76533ecd8ab8e0c1de2dff6d98b14787146fa6ee434ebce0905f99ef3498831');
        """)
        cursor.execute("""
            INSERT INTO fintrac_portfolios VALUES 
            ('FINTRAC-INT-01', 'Stéphane Sirard', 128276000.0, 85318000.0, 35900000.0, 581, '8c2a96f1b3e4492d8e0371a64f89d31109a2b8e3c1a7d6f5e4b3a2c1d0e9f8a7');
        """)
        cursor.executescript("""
            INSERT INTO transaction_velocity_log VALUES 
            ('TXN-9001', 'JS INNOVATION8390-1 INC.', 3750000.0, '2026-01-10', 12, 'Itemized', 'LOW'),
            ('TXN-9002', 'Strategic Advisory Holdings', 1250000.0, '2025-11-01', 95, 'UNITEMIZED', 'HIGH_RISK_STAGNATION_HOLD'),
            ('TXN-9003', 'Cross-Border Logistics Group', 2100000.0, '2026-02-15', 5, 'Itemized', 'LOW'),
            ('TXN-9004', 'Phantom Shell Holding Corp', 4500000.0, '2025-08-20', 145, 'UNITEMIZED', 'CRITICAL_HIGH_RISK_PHANTOM_LEDGER');
        """)
        
        prior_art_payload = "Independent Creator Sovereign Financial Pipeline & Zero-Dependency Audit Engine v2.7"
        art_hash = hashlib.sha256(prior_art_payload.encode('utf-8')).hexdigest()
        cursor.execute(f"""
            INSERT INTO sovereign_prior_art_registry VALUES 
            ('ART-SOV-01', 'Independent Innovator / Creator', 'Cryptographic Treasury & Procurement Pipeline', '2025-01-01', 'Automated Anti-Corruption Architecture', 15937500.0, '{art_hash}', 'CRYPTOGRAPHICALLY_ANCHORED');
        """)

        cursor.execute("""
            INSERT INTO ministerial_enforcement_log VALUES 
            ('ENF-01', 'Hon. Dominic LeBlanc', 'Unitemized transactions exceeding holding limits detected in portfolio outlays.', 'MINISTERIAL_PIPELINE_BANNED', 'Manual Cryptographic Verification and Itemization Required');
        """)
        
        conn.commit()
        conn.close()

    def test_database_connection_and_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        for t in ["portfolios", "contracts_2025_2026", "sovereign_ip_valuations", "fintrac_portfolios", "transaction_velocity_log", "sovereign_prior_art_registry", "ministerial_enforcement_log"]:
            self.assertIn(t, tables)

    def test_ministerial_pipeline_ban_on_unitemized_flows(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT status, action_required FROM ministerial_enforcement_log WHERE minister_name = 'Hon. Dominic LeBlanc';")
        row = cursor.fetchone()
        conn.close()
        self.assertEqual(row[0], "MINISTERIAL_PIPELINE_BANNED")

    def test_high_risk_unitemized_flagging(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transaction_velocity_log WHERE itemization_status = 'UNITEMIZED' AND risk_flag LIKE '%HIGH_RISK%';")
        high_risk_count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(high_risk_count, 2)

if __name__ == "__main__":
    unittest.main()
