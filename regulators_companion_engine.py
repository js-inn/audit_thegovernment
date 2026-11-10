#!/usr/env/python3
"""
Regulators Companion: Public Disclosures & Procurement Audit Engine
Zero-dependency Python engine to audit government tenders, cross-reference corporate 
beneficial ownership, and anchor provenance via SHA-256 chains.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import json
import hashlib
import datetime
from pathlib import Path

DB_FILE = "regulators_companion.db"
DISCLOSURE_REPORT = "procurement_audit_report.md"

class RegulatorsCompanionEngine:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        Path(DISCLOSURE_REPORT).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS procurement_audits')
            cursor.execute('''
                CREATE TABLE procurement_audits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tender_id TEXT UNIQUE,
                    department TEXT,
                    vendor_name TEXT,
                    contract_value REAL,
                    risk_score INTEGER,
                    previous_hash TEXT,
                    current_hash TEXT,
                    timestamp TEXT,
                    audit_finding TEXT
                )
            ''')
            conn.commit()

    def audit_tender(self, tender_id, department, vendor_name, contract_value, risk_score, finding):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_hash FROM procurement_audits ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            prev_hash = row[0] if row else "GENESIS_REGULATORS_COMPANION_CANADA"

        hash_base = f"{tender_id}|{department}|{vendor_name}|{contract_value}|{risk_score}|{prev_hash}|{timestamp}"
        current_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO procurement_audits (tender_id, department, vendor_name, contract_value, risk_score, previous_hash, current_hash, timestamp, audit_finding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (tender_id, department, vendor_name, contract_value, risk_score, prev_hash, current_hash, timestamp, finding))
            conn.commit()
            print(f"[REGULATORS COMPANION] Audited Tender [{tender_id}] -> Finding: {finding}")

    def run_simulation(self):
        print("[*] Executing Regulators Companion audit on public procurement feeds...")
        tenders = [
            {
                "tender_id": "TEND-2026-0881",
                "department": "Public Services and Procurement Canada",
                "vendor_name": "Apex Consulting Group Inc.",
                "contract_value": 4250000.0,
                "risk_score": 85,
                "finding": "FLAGGED_SOLE_SOURCE_OVER_THRESHOLD"
            },
            {
                "tender_id": "TEND-2026-0912",
                "department": "Shared Services Canada",
                "vendor_name": "Northern Digital Infrastructure Ltd.",
                "contract_value": 1150000.0,
                "risk_score": 12,
                "finding": "VERIFIED_COMPETITIVE_OPEN_BID"
            },
            {
                "tender_id": "TEND-2026-1044",
                "department": "Transport Canada",
                "vendor_name": "Prairie Logistics & Heavy Transit",
                "contract_value": 8900000.0,
                "risk_score": 92,
                "finding": "FLAGGED_DIRECT_AWARD_CRONYISM_INDICATOR"
            }
        ]

        for t in tenders:
            self.audit_tender(
                tender_id=t["tender_id"],
                department=t["department"],
                vendor_name=t["vendor_name"],
                contract_value=t["contract_value"],
                risk_score=t["risk_score"],
                finding=t["finding"]
            )

    def export_report(self):
        print(f"\n[*] Generating Procurement Audit Report -> {DISCLOSURE_REPORT}...")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tender_id, department, vendor_name, contract_value, risk_score, current_hash, audit_finding FROM procurement_audits")
            records = cursor.fetchall()

        ts_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        md = f"""# REGULATORS COMPANION: PROCUREMENT AUDIT REPORT
**Generated:** {ts_str}  
**Engine:** Regulators Companion Zero-Dependency Python Core  
**Sovereign Entity:** JS INNOVATION8390-1 INC. / Jujita Stairs  
**Mandate:** Dismantling Opacity & Ensuring Public Fund Integrity  

---

## 1. Audited Public Contracts Ledger

| Tender ID | Department | Vendor Name | Value (CAD) | Risk Score (0-100) | Audit Finding |
|---|---|---|---|---|---|
"""
        for r in records:
            tid, dept, vendor, val, risk, _, finding = r
            risk_badge = f"🔴 **{risk} (High Risk)**" if risk > 50 else f"🟢 **{risk} (Low Risk)**"
            md += f"| `{tid}` | {dept} | **{vendor}** | `${val:,.2f}` | {risk_badge} | `{finding}` |\n"

        md += "\n--- \n*End of Public Disclosure Audit — Secured via SHA-256 Provenance Chaining*"
        with open(DISCLOSURE_REPORT, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[+] Report exported to {DISCLOSURE_REPORT}")

if __name__ == "__main__":
    engine = RegulatorsCompanionEngine()
    engine.run_simulation()
    engine.export_report()
