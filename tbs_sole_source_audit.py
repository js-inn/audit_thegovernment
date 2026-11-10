#!/usr/env/python3
"""
Treasury Board Secretariat (TBS) Sole-Source Procurement Audit Engine: audit_thegovernment
Audits federal procurement contracts including specific MSA contracts and business numbers,
securing all transactional records with SHA-256 provenance chains.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import hashlib
import datetime
from pathlib import Path

DB_FILE = "tbs_sole_source_vault.db"
REPORT_FILE = "tbs_sole_source_audit_report.md"

class TBSSoleSourceAuditor:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        Path(REPORT_FILE).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS tbs_procurement_contracts')
            cursor.execute('''
                CREATE TABLE tbs_procurement_contracts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_id TEXT UNIQUE,
                    business_number TEXT,
                    project_title TEXT,
                    supplier_name TEXT,
                    procurement_method TEXT,
                    total_value_cad REAL,
                    risk_score INTEGER,
                    previous_hash TEXT,
                    current_hash TEXT,
                    timestamp TEXT,
                    audit_finding TEXT
                )
            ''')
            conn.commit()

    def audit_contract(self, contract_id, business_number, title, supplier, method, value, risk_score, finding):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_hash FROM tbs_procurement_contracts ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            prev_hash = row[0] if row else "GENESIS_TBS_VAULT"

        hash_base = f"{contract_id}|{business_number}|{title}|{supplier}|{method}|{value}|{risk_score}|{prev_hash}|{timestamp}"
        current_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tbs_procurement_contracts (contract_id, business_number, project_title, supplier_name, procurement_method, total_value_cad, risk_score, previous_hash, current_hash, timestamp, audit_finding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (contract_id, business_number, title, supplier, method, value, risk_score, prev_hash, current_hash, timestamp, finding))
            conn.commit()
            print(f"[TBS AUDIT] Recorded [{contract_id}] (BN: {business_number}) -> ${value:,.2f} | Finding: {finding}")

    def run_simulation(self):
        print("[*] Executing targeted audit on TBS procurement files including MSA Contract ID CW2321555...")
        records = [
            {
                "contract_id": "CW2321555",
                "business_number": "735350936",
                "project_title": "Master Services Agreement (MSA) Professional Advisory & Specialized Task Authorization",
                "supplier_name": "Registered Federal Vendor (BN: 735350936)",
                "procurement_method": "Non-Competitive Sole-Source Task Authorization under MSA",
                "value": 3750000.0,
                "risk_score": 85,
                "finding": "FLAGGED_HIGH_VALUE_MSA_SOLE_SOURCE_ALLOCATION"
            },
            {
                "contract_id": "TBS-2026-9014",
                "business_number": "123456789",
                "project_title": "Core IT Enterprise Architecture Modernization Advisory",
                "supplier_name": "McKinsey & Company Canada",
                "procurement_method": "Non-Competitive (Sole-Source Task Authorization)",
                "value": 4850000.0,
                "risk_score": 89,
                "finding": "FLAGGED_HIGH_RISK_SOLE_SOURCE_CONSULTING"
            },
            {
                "contract_id": "TBS-2026-9022",
                "business_number": "987654321",
                "project_title": "Cloud Security Infrastructure Compliance Review",
                "supplier_name": "Deloitte LLP Ottawa",
                "procurement_method": "Competitive Open Tender (PWGSC)",
                "value": 1250000.0,
                "risk_score": 24,
                "finding": "VERIFIED_COMPETITIVE_AGREEMENT"
            }
        ]

        for r in records:
            self.audit_contract(
                contract_id=r["contract_id"],
                business_number=r["business_number"],
                title=r["project_title"],
                supplier=r["supplier_name"],
                method=r["procurement_method"],
                value=r["value"],
                risk_score=r["risk_score"],
                finding=r["finding"]
            )

    def export_report(self):
        print(f"\n[*] Generating TBS Sole-Source Audit Report -> {REPORT_FILE}...")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT contract_id, business_number, project_title, supplier_name, procurement_method, total_value_cad, risk_score, current_hash, audit_finding FROM tbs_procurement_contracts")
            records = cursor.fetchall()

        ts_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        md = f"""# TREASURY BOARD OF CANADA SECRETARIAT (TBS) SOLE-SOURCE PROCUREMENT AUDIT REPORT
**Generated:** {ts_str}  
**Engine:** TBS Sole-Source Auditor (Zero-Dependency Python Core)  
**Sovereign Entity:** JS INNOVATION8390-1 INC. / Jujita Stairs  
**Scope:** Federal Professional Services, MSA Tracking (ID: CW2321555), and Business Number Registry Analysis  

---

## 1. Audited Procurement & Contract Ledger

| Contract ID | Business No. | Project Title | Supplier Name | Procurement Method | Total Value (CAD) | Risk Score | Audit Finding | SHA-256 Fingerprint |
|---|---|---|---|---|---|---|---|---|
"""
        total_contract_value = 0.0
        for r in records:
            cid, bnum, title, supplier, method, value, risk, chash, finding = r
            total_contract_value += value
            risk_badge = f"🔴 **{risk} (High Risk)**" if risk > 50 else f"🟢 **{risk} (Low Risk)**"
            md += f"| `{cid}` | `{bnum}` | {title} | **{supplier}** | {method} | `${value:,.2f}` | {risk_badge} | `{finding}` | `{chash[:12]}...` |\n"

        md += f"\n### Summary Statistics\n"
        md += f"- **Total Audited Procurement Value:** `${total_contract_value:,.2f} CAD`\n"
        md += f"- **Cryptographic Integrity:** Secured via SHA-256 Provenance Chaining (`tbs_sole_source_vault.db`)\n\n"
        md += "---\n*End of Treasury Board Secretariat Sovereign Audit — JS INNOVATION8390-1 INC.*"

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[+] Report exported to {REPORT_FILE}")

if __name__ == "__main__":
    auditor = TBSSoleSourceAuditor()
    auditor.run_simulation()
    auditor.export_report()
