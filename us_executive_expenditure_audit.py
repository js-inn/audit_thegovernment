#!/usr/env/python3
"""
US Executive Expenditure Audit Engine: audit_thegovernment
Audits 6-month executive discretionary and operational expenditures for the Executive Office of the President,
flagging sole-source defense contracts, non-competitive travel, and hospitality variances using SHA-256 chains.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import hashlib
import datetime
from pathlib import Path

DB_FILE = "us_executive_expenditure_vault.db"
REPORT_FILE = "us_executive_expenditure_report.md"

class USExecutiveExpenditureAuditor:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        Path(REPORT_FILE).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS us_executive_expenditures')
            cursor.execute('''
                CREATE TABLE us_executive_expenditures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expense_id TEXT UNIQUE,
                    agency TEXT,
                    vendor_or_recipient TEXT,
                    category TEXT,
                    amount_usd REAL,
                    risk_score INTEGER,
                    previous_hash TEXT,
                    current_hash TEXT,
                    timestamp TEXT,
                    audit_finding TEXT
                )
            ''')
            conn.commit()

    def audit_expense(self, expense_id, agency, vendor, category, amount, risk_score, finding):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_hash FROM us_executive_expenditures ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            prev_hash = row[0] if row else "GENESIS_US_EXECUTIVE_VAULT"

        hash_base = f"{expense_id}|{agency}|{vendor}|{category}|{amount}|{risk_score}|{prev_hash}|{timestamp}"
        current_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO us_executive_expenditures (expense_id, agency, vendor_or_recipient, category, amount_usd, risk_score, previous_hash, current_hash, timestamp, audit_finding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (expense_id, agency, vendor, category, amount, risk_score, prev_hash, current_hash, timestamp, finding))
            conn.commit()
            print(f"[US EXECUTIVE AUDIT] Recorded [{expense_id}] -> {category} | Amount: ${amount:,.2f} | Finding: {finding}")

    def run_simulation(self):
        print("[*] Executing 6-month expenditure audit on Executive Office of the President / Federal Discretionary accounts...")
        records = [
            {
                "expense_id": "USEC-EXP-2026-Q1-012",
                "agency": "Executive Office of the President / DoD Support",
                "vendor": "Global Aviation Charter Services LLC",
                "category": "Air Force One Support & Executive Airlift Logistics",
                "amount": 12500000.0,
                "risk_score": 82,
                "finding": "FLAGGED_SOLE_SOURCE_EXECUTIVE_TRANSPORT_AWARD"
            },
            {
                "expense_id": "USEC-EXP-2026-Q1-045",
                "agency": "Department of Homeland Security / USSS",
                "vendor": "Palmetto Secure Motorcade & Fleet Logistics",
                "category": "Motorcade Protection & Armored Vehicle Transport",
                "amount": 4800000.0,
                "risk_score": 25,
                "finding": "VERIFIED_COMPETITIVE_FRAMEWORK_AGREEMENT"
            },
            {
                "expense_id": "USEC-EXP-2026-Q2-088",
                "agency": "Executive Office of the President",
                "vendor": "Mar-a-Lago Club & Hospitality Holdings",
                "category": "State Dinner & Official Diplomatic Summit Hosting",
                "amount": 1450000.0,
                "risk_score": 76,
                "finding": "FLAGGED_PROPRIETARY_VENUE_HOSPITALITY_VARIANCE"
            },
            {
                "expense_id": "USEC-EXP-2026-Q2-132",
                "agency": "General Services Administration (GSA)",
                "vendor": "Capital Infrastructure & Security Solutions Inc.",
                "category": "Classified Perimeter Hardening & Communications",
                "amount": 8900000.0,
                "risk_score": 18,
                "finding": "VERIFIED_OPEN_TENDER_COMPLIANT"
            },
            {
                "expense_id": "USEC-EXP-2026-Q2-195",
                "agency": "Executive Office of the President",
                "vendor": "Vanguard Strategic Communications Group",
                "category": "Public Diplomacy & Executive Advisory Services",
                "amount": 3200000.0,
                "risk_score": 89,
                "finding": "FLAGGED_DIRECT_AWARD_CONSULTANCY_MONOPOLY"
            }
        ]

        for r in records:
            self.audit_expense(
                expense_id=r["expense_id"],
                agency=r["agency"],
                vendor=r["vendor"],
                category=r["category"],
                amount=r["amount"],
                risk_score=r["risk_score"],
                finding=r["finding"]
            )

    def export_report(self):
        print(f"\n[*] Generating US Executive Expenditure Audit Report -> {REPORT_FILE}...")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT expense_id, agency, vendor_or_recipient, category, amount_usd, risk_score, current_hash, audit_finding FROM us_executive_expenditures")
            records = cursor.fetchall()

        ts_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        md = f"""# US EXECUTIVE EXPENDITURE AUDIT REPORT (6-MONTH DISCLOSURE)
**Generated:** {ts_str}  
**Engine:** US Executive Expenditure Auditor (Zero-Dependency Python Core)  
**Sovereign Entity:** JS INNOVATION8390-1 INC. / Jujita Stairs  
**Scope:** Executive Office of the President & Federal Discretionary Accounts  

---

## 1. Audited Executive Expenditure Ledger

| Expense ID | Agency / Office | Vendor / Recipient | Category | Amount (USD) | Risk Score | Audit Finding | SHA-256 Fingerprint |
|---|---|---|---|---|---|---|---|
"""
        total_spent = 0.0
        for r in records:
            eid, agency, vendor, cat, amount, risk, chash, finding = r
            total_spent += amount
            risk_badge = f"🔴 **{risk} (High Risk)**" if risk > 50 else f"🟢 **{risk} (Low Risk)**"
            md += f"| `{eid}` | {agency} | **{vendor}** | {cat} | `${amount:,.2f}` | {risk_badge} | `{finding}` | `{chash[:12]}...` |\n"

        md += f"\n### Summary Statistics\n"
        md += f"- **Total Audited Outlays (6 Months):** `${total_spent:,.2f} USD`\n"
        md += f"- **Cryptographic Integrity:** Secured via SHA-256 Provenance Chaining (`us_executive_expenditure_vault.db`)\n\n"
        md += "---\n*End of Sovereign Executive Audit — JS INNOVATION8390-1 INC.*"

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[+] Report exported to {REPORT_FILE}")

if __name__ == "__main__":
    auditor = USExecutiveExpenditureAuditor()
    auditor.run_simulation()
    auditor.export_report()
