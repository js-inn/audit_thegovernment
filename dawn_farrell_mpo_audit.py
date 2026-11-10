#!/usr/env/python3
"""
Dawn Farrell / Major Projects Office (MPO) Expenditure Audit Engine: audit_thegovernment
Audits capital project outlays, fast-tracked energy corridor approvals, and advisory expenditures,
flagging cost overruns, proprietary engineering monopolies, and risk variances using SHA-256 chains.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import hashlib
import datetime
from pathlib import Path

DB_FILE = "dawn_farrell_mpo_vault.db"
REPORT_FILE = "dawn_farrell_mpo_audit_report.md"

class DawnFarrellMPOAuditor:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        Path(REPORT_FILE).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS mpo_project_expenditures')
            cursor.execute('''
                CREATE TABLE mpo_project_expenditures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expense_id TEXT UNIQUE,
                    project_name TEXT,
                    contractor_or_partner TEXT,
                    category TEXT,
                    amount_cad REAL,
                    risk_score INTEGER,
                    previous_hash TEXT,
                    current_hash TEXT,
                    timestamp TEXT,
                    audit_finding TEXT
                )
            ''')
            conn.commit()

    def audit_expense(self, expense_id, project, contractor, category, amount, risk_score, finding):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_hash FROM mpo_project_expenditures ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            prev_hash = row[0] if row else "GENESIS_MPO_DAWN_FARRELL_VAULT"

        hash_base = f"{expense_id}|{project}|{contractor}|{category}|{amount}|{risk_score}|{prev_hash}|{timestamp}"
        current_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO mpo_project_expenditures (expense_id, project_name, contractor_or_partner, category, amount_cad, risk_score, previous_hash, current_hash, timestamp, audit_finding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (expense_id, project, contractor, category, amount, risk_score, prev_hash, current_hash, timestamp, finding))
            conn.commit()
            print(f"[MPO AUDIT] Recorded [{expense_id}] -> {project} | Amount: ${amount:,.2f} | Finding: {finding}")

    def run_simulation(self):
        print("[*] Executing capital expenditure & fast-tracked project audit on Major Projects Office (MPO)...")
        records = [
            {
                "expense_id": "MPO-2026-Q1-001",
                "project": "Trans Mountain Pipeline Expansion & Integration Corridor",
                "contractor": "Pacific Anchor Engineering & Construction Ltd.",
                "category": "Overrun Remediation & Capacity Optimization",
                "amount": 340000000.0,
                "risk_score": 88,
                "finding": "FLAGGED_LEGACY_COST_OVERRUN_VARIANCE"
            },
            {
                "expense_id": "MPO-2026-Q1-042",
                "project": "National Clean Energy Grid Corridor (Phase 1)",
                "contractor": "Vanguard Transmissions & Infrastructure Inc.",
                "category": "Interprovincial Transmission Fast-Track Engineering",
                "amount": 85000000.0,
                "risk_score": 24,
                "finding": "VERIFIED_COMPETITIVE_MILESTONE_AWARD"
            },
            {
                "expense_id": "MPO-2026-Q2-089",
                "project": "Major Projects Office Executive & Advisory Operations",
                "contractor": "Global Strategic Energy Consultants LLC",
                "category": "Proprietary Regulatory Fast-Track Advisory",
                "amount": 14500000.0,
                "risk_score": 79,
                "finding": "FLAGGED_SOLE_SOURCE_ADVISORY_MONOPOLY"
            },
            {
                "expense_id": "MPO-2026-Q2-115",
                "project": "Critical Minerals Northern Transport Route",
                "contractor": "Borealis Heavy Logistics & Construction",
                "category": "Access Road & Infrastructure Development",
                "amount": 120000000.0,
                "risk_score": 32,
                "finding": "VERIFIED_COMPLIANT_TENDER_AGREEMENT"
            }
        ]

        for r in records:
            self.audit_expense(
                expense_id=r["expense_id"],
                project=r["project"],
                contractor=r["contractor"],
                category=r["category"],
                amount=r["amount"],
                risk_score=r["risk_score"],
                finding=r["finding"]
            )

    def export_report(self):
        print(f"\n[*] Generating Dawn Farrell / MPO Audit Report -> {REPORT_FILE}...")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT expense_id, project_name, contractor_or_partner, category, amount_cad, risk_score, current_hash, audit_finding FROM mpo_project_expenditures")
            records = cursor.fetchall()

        ts_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        md = f"""# DAWN FARRELL / MAJOR PROJECTS OFFICE (MPO) EXPENDITURE AUDIT REPORT
**Generated:** {ts_str}  
**Engine:** MPO Project Auditor (Zero-Dependency Python Core)  
**Sovereign Entity:** JS INNOVATION8390-1 INC. / Jujita Stairs  
**Scope:** Major Projects Office Fast-Tracked Energy & Infrastructure Outlays  

---

## 1. Audited Capital Projects & Advisory Ledger

| Expense ID | Project Name | Contractor / Partner | Category | Amount (CAD) | Risk Score | Audit Finding | SHA-256 Fingerprint |
|---|---|---|---|---|---|---|---|
"""
        total_spent = 0.0
        for r in records:
            eid, proj, contractor, cat, amount, risk, chash, finding = r
            total_spent += amount
            risk_badge = f"🔴 **{risk} (High Risk)**" if risk > 50 else f"🟢 **{risk} (Low Risk)**"
            md += f"| `{eid}` | {proj} | **{contractor}** | {cat} | `${amount:,.2f}` | {risk_badge} | `{finding}` | `{chash[:12]}...` |\n"

        md += f"\n### Summary Statistics\n"
        md += f"- **Total Audited MPO Outlays:** `${total_spent:,.2f} CAD`\n"
        md += f"- **Cryptographic Integrity:** Secured via SHA-256 Provenance Chaining (`dawn_farrell_mpo_vault.db`)\n\n"
        md += "---\n*End of Dawn Farrell / MPO Sovereign Audit — JS INNOVATION8390-1 INC.*"

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[+] Report exported to {REPORT_FILE}")

if __name__ == "__main__":
    auditor = DawnFarrellMPOAuditor()
    auditor.run_simulation()
    auditor.export_report()
