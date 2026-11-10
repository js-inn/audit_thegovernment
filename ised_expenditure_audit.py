#!/usr/env/python3
"""
ISED Minister & Departmental Expenditure Audit Engine: audit_thegovernment
Audits 6-month Proactive Disclosure outlays for Innovation, Science and Economic Development Canada,
flagging high-risk industrial grants, sole-source commercial contracts, and ministerial travel variances using SHA-256 chains.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import hashlib
import datetime
from pathlib import Path

DB_FILE = "ised_expenditure_vault.db"
REPORT_FILE = "ised_expenditure_report.md"

class ISEDExpenditureAuditor:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        Path(REPORT_FILE).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS ised_expenditures')
            cursor.execute('''
                CREATE TABLE ised_expenditures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expense_id TEXT UNIQUE,
                    branch_or_office TEXT,
                    recipient_or_vendor TEXT,
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

    def audit_expense(self, expense_id, branch, recipient, category, amount, risk_score, finding):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_hash FROM ised_expenditures ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            prev_hash = row[0] if row else "GENESIS_ISED_VAULT_CANADA"

        hash_base = f"{expense_id}|{branch}|{recipient}|{category}|{amount}|{risk_score}|{prev_hash}|{timestamp}"
        current_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ised_expenditures (expense_id, branch_or_office, recipient_or_vendor, category, amount_cad, risk_score, previous_hash, current_hash, timestamp, audit_finding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (expense_id, branch, recipient, category, amount, risk_score, prev_hash, current_hash, timestamp, finding))
            conn.commit()
            print(f"[ISED AUDIT] Recorded [{expense_id}] -> {category} | Amount: ${amount:,.2f} | Finding: {finding}")

    def run_simulation(self):
        print("[*] Executing 6-month Proactive Disclosure audit on ISED Ministerial Office and Strategic Innovation Programs...")
        records = [
            {
                "expense_id": "ISED-2026-Q1-021",
                "branch": "Minister of ISED Office",
                "vendor": "Global Tech Trade Mission Charter Corp",
                "category": "International Semiconductor & AI Ministerial Delegation Travel",
                "amount": 215000.0,
                "risk_score": 68,
                "finding": "FLAGGED_MINISTERIAL_CHARTER_FLIGHT_VARIANCE"
            },
            {
                "expense_id": "ISED-2026-Q1-094",
                "branch": "Strategic Innovation Fund (SIF)",
                "vendor": "NextGen EV Battery Technologies Inc.",
                "category": "Industrial Technology Contribution Agreement (> $25M)",
                "amount": 45000000.0,
                "risk_score": 22,
                "finding": "VERIFIED_COMPLIANT_MILESTONE_GRANT"
            },
            {
                "expense_id": "ISED-2026-Q2-112",
                "branch": "Minister of ISED Office",
                "vendor": "Rideau Club & Executive Dining Ottawa",
                "category": "Digital Economy Stakeholder Consultation Hosting",
                "amount": 24500.0,
                "risk_score": 30,
                "finding": "VERIFIED_STANDARD_HOSPITALITY_CLAIM"
            },
            {
                "expense_id": "ISED-2026-Q2-155",
                "branch": "Spectrum, Information Technologies and Telecom",
                "vendor": "Quantum Cryptography & Spectrum Advisory Group",
                "category": "Sole-Source Policy Research & Spectrum Consulting",
                "amount": 1250000.0,
                "risk_score": 88,
                "finding": "FLAGGED_SOLE_SOURCE_CONSULTING_CONTRACT_OVER_THRESHOLD"
            },
            {
                "expense_id": "ISED-2026-Q2-208",
                "branch": "Small Business and Tourism Branch",
                "vendor": "Pan-Canadian Digital Commerce Infrastructure",
                "category": " SME Digital Adoption Program Support",
                "amount": 3400000.0,
                "risk_score": 14,
                "finding": "VERIFIED_COMPETITIVE_TENDER_AWARD"
            }
        ]

        for r in records:
            self.audit_expense(
                expense_id=r["expense_id"],
                branch=r["branch"],
                recipient=r["vendor"],
                category=r["category"],
                amount=r["amount"],
                risk_score=r["risk_score"],
                finding=r["finding"]
            )

    def export_report(self):
        print(f"\n[*] Generating ISED Expenditure Audit Report -> {REPORT_FILE}...")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT expense_id, branch_or_office, recipient_or_vendor, category, amount_cad, risk_score, current_hash, audit_finding FROM ised_expenditures")
            records = cursor.fetchall()

        ts_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        md = f"""# ISED MINISTER & DEPARTMENTAL EXPENDITURE AUDIT REPORT
**Generated:** {ts_str}  
**Engine:** ISED Expenditure Auditor (Zero-Dependency Python Core)  
**Sovereign Entity:** JS INNOVATION8390-1 INC. / Jujita Stairs  
**Scope:** Minister of Innovation, Science and Industry Office & SIF Program Disclosures  

---

## 1. Audited ISED Financial & Grants Ledger

| Expense ID | Branch / Office | Recipient / Vendor | Category | Amount (CAD) | Risk Score | Audit Finding | SHA-256 Fingerprint |
|---|---|---|---|---|---|---|---|
"""
        total_spent = 0.0
        for r in records:
            eid, branch, vendor, cat, amount, risk, chash, finding = r
            total_spent += amount
            risk_badge = f"🔴 **{risk} (High Risk)**" if risk > 50 else f"🟢 **{risk} (Low Risk)**"
            md += f"| `{eid}` | {branch} | **{vendor}** | {cat} | `${amount:,.2f}` | {risk_badge} | `{finding}` | `{chash[:12]}...` |\n"

        md += f"\n### Summary Statistics\n"
        md += f"- **Total Audited ISED Outlays (6 Months):** `${total_spent:,.2f} CAD`\n"
        md += f"- **Cryptographic Integrity:** Secured via SHA-256 Provenance Chaining (`ised_expenditure_vault.db`)\n\n"
        md += "---\n*End of ISED Sovereign Expenditure Audit — JS INNOVATION8390-1 INC.*"

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[+] Report exported to {REPORT_FILE}")

if __name__ == "__main__":
    auditor = ISEDExpenditureAuditor()
    auditor.run_simulation()
    auditor.export_report()
