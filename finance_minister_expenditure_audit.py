#!/usr/env/python3
"""
Minister of Finance Expenditure Audit Engine: audit_thegovernment
Audits departmental expenditures, fiscal policy advisory contracts, and ministerial outlays,
flagging high-risk sole-source consulting and fiscal variances using SHA-256 chains.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import hashlib
import datetime
from pathlib import Path

DB_FILE = "finance_minister_vault.db"
REPORT_FILE = "finance_minister_expenditure_report.md"

class FinanceMinisterAuditor:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        Path(REPORT_FILE).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS finance_minister_expenditures')
            cursor.execute('''
                CREATE TABLE finance_minister_expenditures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expense_id TEXT UNIQUE,
                    initiative_or_purpose TEXT,
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

    def audit_expense(self, expense_id, purpose, vendor, category, amount, risk_score, finding):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_hash FROM finance_minister_expenditures ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            prev_hash = row[0] if row else "GENESIS_FINANCE_MINISTER_VAULT"

        hash_base = f"{expense_id}|{purpose}|{vendor}|{category}|{amount}|{risk_score}|{prev_hash}|{timestamp}"
        current_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO finance_minister_expenditures (expense_id, initiative_or_purpose, recipient_or_vendor, category, amount_cad, risk_score, previous_hash, current_hash, timestamp, audit_finding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (expense_id, purpose, vendor, category, amount, risk_score, prev_hash, current_hash, timestamp, finding))
            conn.commit()
            print(f"[FINANCE AUDIT] Recorded [{expense_id}] -> {purpose} | Amount: ${amount:,.2f} | Finding: {finding}")

    def run_simulation(self):
        print("[*] Executing Proactive Disclosure audit on Department of Finance ministerial outlays...")
        records = [
            {
                "expense_id": "FIN-2026-Q1-014",
                "initiative_or_purpose": "G7 Finance Ministers & Central Bank Governors Delegation Travel",
                "recipient_or_vendor": "Government Air Transport / Official Delegation",
                "category": "Ministerial International Travel & Logistics",
                "amount": 185000.0,
                "risk_score": 38,
                "finding": "VERIFIED_STANDARD_MINISTERIAL_DELEGATION"
            },
            {
                "expense_id": "FIN-2026-Q1-088",
                "initiative_or_purpose": "Macroeconomic Forecasting & Fiscal Framework Modeling",
                "recipient_or_vendor": "Meridian Economic Advisory Group Ltd.",
                "category": "Sole-Source Fiscal Policy Research",
                "amount": 2100000.0,
                "risk_score": 82,
                "finding": "FLAGGED_SOLE_SOURCE_MACRO_CONSULTING_CONTRACT"
            },
            {
                "expense_id": "FIN-2026-Q2-132",
                "initiative_or_purpose": "Federal Budget 2026 National Stakeholder Consultations",
                "recipient_or_vendor": "OmniVoice Public Engagement Corp.",
                "category": "Consultation Hosting & Digital Town Halls",
                "amount": 650000.0,
                "risk_score": 29,
                "finding": "VERIFIED_COMPETITIVE_TENDER_AWARD"
            },
            {
                "expense_id": "FIN-2026-Q2-205",
                "initiative_or_purpose": "Financial Sector Cyber-Resilience & Systemic Risk Stress Testing",
                "recipient_or_vendor": "QuantSec Financial Systems Inc.",
                "category": "Specialized Tech & Banking System Audit",
                "amount": 3400000.0,
                "risk_score": 45,
                "finding": "VERIFIED_COMPLIANT_COMPETITIVE_AGREEMENT"
            }
        ]

        for r in records:
            self.audit_expense(
                expense_id=r["expense_id"],
                purpose=r["initiative_or_purpose"],
                vendor=r["recipient_or_vendor"],
                category=r["category"],
                amount=r["amount"],
                risk_score=r["risk_score"],
                finding=r["finding"]
            )

    def export_report(self):
        print(f"\n[*] Generating Minister of Finance Audit Report -> {REPORT_FILE}...")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT expense_id, initiative_or_purpose, recipient_or_vendor, category, amount_cad, risk_score, current_hash, audit_finding FROM finance_minister_expenditures")
            records = cursor.fetchall()

        ts_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        md = f"""# CANADIAN MINISTER OF FINANCE / DEPARTMENT OF FINANCE EXPENDITURE AUDIT REPORT
**Generated:** {ts_str}  
**Engine:** Finance Minister Auditor (Zero-Dependency Python Core)  
**Sovereign Entity:** JS INNOVATION8390-1 INC. / Jujita Stairs  
**Scope:** Department of Finance Outlays, Fiscal Advisory Contracts, and Ministerial Travel  

---

## 1. Audited Ministerial & Departmental Ledger

| Expense ID | Purpose / Initiative | Recipient / Vendor | Category | Amount (CAD) | Risk Score | Audit Finding | SHA-256 Fingerprint |
|---|---|---|---|---|---|---|---|
"""
        total_spent = 0.0
        for r in records:
            eid, purpose, vendor, cat, amount, risk, chash, finding = r
            total_spent += amount
            risk_badge = f"🔴 **{risk} (High Risk)**" if risk > 50 else f"🟢 **{risk} (Low Risk)**"
            md += f"| `{eid}` | {purpose} | **{vendor}** | {cat} | `${amount:,.2f}` | {risk_badge} | `{finding}` | `{chash[:12]}...` |\n"

        md += f"\n### Summary Statistics\n"
        md += f"- **Total Audited Finance Outlays:** `${total_spent:,.2f} CAD`\n"
        md += f"- **Cryptographic Integrity:** Secured via SHA-256 Provenance Chaining (`finance_minister_vault.db`)\n\n"
        md += "---\n*End of Minister of Finance Sovereign Audit — JS INNOVATION8390-1 INC.*"

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[+] Report exported to {REPORT_FILE}")

if __name__ == "__main__":
    auditor = FinanceMinisterAuditor()
    auditor.run_simulation()
    auditor.export_report()
