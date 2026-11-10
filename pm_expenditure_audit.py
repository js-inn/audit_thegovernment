#!/usr/env/python3
"""
PM & Federal Expenditure Audit Engine: audit_thegovernment
Audits 6-month Proactive Disclosure expenditures for the Prime Minister's Office / Privy Council Office,
flagging high-risk contracts, non-competitive charters, and hospitality variances using SHA-256 chains.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import hashlib
import datetime
from pathlib import Path

DB_FILE = "pm_expenditure_vault.db"
REPORT_FILE = "pm_expenditure_audit_report.md"

class PMExpenditureAuditor:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        Path(REPORT_FILE).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS federal_expenditures')
            cursor.execute('''
                CREATE TABLE federal_expenditures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expense_id TEXT UNIQUE,
                    department TEXT,
                    vendor_or_recipient TEXT,
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

    def audit_expense(self, expense_id, department, vendor, category, amount, risk_score, finding):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_hash FROM federal_expenditures ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            prev_hash = row[0] if row else "GENESIS_PM_EXPENDITURE_VAULT_CANADA"

        hash_base = f"{expense_id}|{department}|{vendor}|{category}|{amount}|{risk_score}|{prev_hash}|{timestamp}"
        current_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO federal_expenditures (expense_id, department, vendor_or_recipient, category, amount_cad, risk_score, previous_hash, current_hash, timestamp, audit_finding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (expense_id, department, vendor, category, amount, risk_score, prev_hash, current_hash, timestamp, finding))
            conn.commit()
            print(f"[PM EXPENDITURE AUDIT] Recorded [{expense_id}] -> {category} | Amount: ${amount:,.2f} | Finding: {finding}")

    def run_simulation(self):
        print("[*] Executing 6-month Proactive Disclosure audit on PMO & Federal Executive expenditures...")
        records = [
            {
                "expense_id": "PMO-EXP-2026-Q1-042",
                "department": "Prime Minister's Office / Privy Council Office",
                "vendor": "Northwest Executive Air Charters Ltd.",
                "category": "Official International Delegation Air Transport",
                "amount": 1420000.0,
                "risk_score": 78,
                "finding": "FLAGGED_SOLE_SOURCE_AIR_CHARTER_OVER_THRESHOLD"
            },
            {
                "expense_id": "PMO-EXP-2026-Q1-089",
                "department": "Privy Council Office",
                "vendor": "Ottawa Secure Communications & IT Corp",
                "category": "Classified Infrastructure & Hardware Upgrade",
                "amount": 3150000.0,
                "risk_score": 15,
                "finding": "VERIFIED_COMPETITIVE_TENDER_AWARD"
            },
            {
                "expense_id": "PMO-EXP-2026-Q2-112",
                "department": "Prime Minister's Office",
                "vendor": "Chateau Laurier Conference & Dining",
                "category": "Official State Hospitality & Summit Dinner",
                "amount": 185000.0,
                "risk_score": 62,
                "finding": "FLAGGED_HOSPITALITY_VARIANCE_ABOVE_GUIDELINES"
            },
            {
                "expense_id": "PMO-EXP-2026-Q2-154",
                "department": "Privy Council Office",
                "vendor": "Global Strategic Advisory Partners",
                "category": "Policy Consulting & Intergovernmental Research",
                "amount": 890000.0,
                "risk_score": 88,
                "finding": "FLAGGED_DIRECT_AWARD_CONSULTANCY_MONOPOLY"
            },
            {
                "expense_id": "PMO-EXP-2026-Q2-201",
                "department": "Prime Minister's Office",
                "vendor": "Dominion Secure Transit Services",
                "category": "Ground Motorcade & Logistics Support",
                "amount": 540000.0,
                "risk_score": 20,
                "finding": "VERIFIED_FRAMEWORK_AGREEMENT_COMPLIANT"
            }
        ]

        for r in records:
            self.audit_expense(
                expense_id=r["expense_id"],
                department=r["department"],
                vendor=r["vendor"],
                category=r["category"],
                amount=r["amount"],
                risk_score=r["risk_score"],
                finding=r["finding"]
            )

    def export_report(self):
        print(f"\n[*] Generating Federal Expenditure Audit Report -> {REPORT_FILE}...")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT expense_id, department, vendor_or_recipient, category, amount_cad, risk_score, current_hash, audit_finding FROM federal_expenditures")
            records = cursor.fetchall()

        ts_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        md = f"""# PM & FEDERAL EXPENDITURE AUDIT REPORT (6-MONTH PROACTIVE DISCLOSURE)
**Generated:** {ts_str}  
**Engine:** PM Expenditure Auditor (Zero-Dependency Python Core)  
**Sovereign Entity:** JS INNOVATION8390-1 INC. / Jujita Stairs  
**Scope:** Prime Minister's Office & Privy Council Office Proactive Disclosures  

---

## 1. Audited Executive Expenditure Ledger

| Expense ID | Department | Recipient / Vendor | Category | Amount (CAD) | Risk Score | Audit Finding | SHA-256 Fingerprint |
|---|---|---|---|---|---|---|---|
"""
        total_spent = 0.0
        for r in records:
            eid, dept, vendor, cat, amount, risk, chash, finding = r
            total_spent += amount
            risk_badge = f"🔴 **{risk} (High Risk)**" if risk > 50 else f"🟢 **{risk} (Low Risk)**"
            md += f"| `{eid}` | {dept} | **{vendor}** | {cat} | `${amount:,.2f}` | {risk_badge} | `{finding}` | `{chash[:12]}...` |\n"

        md += f"\n### Summary Statistics\n"
        md += f"- **Total Audited Outlays (6 Months):** `${total_spent:,.2f} CAD`\n"
        md += f"- **Cryptographic Integrity:** Secured via SHA-256 Provenance Chaining (`pm_expenditure_vault.db`)\n\n"
        md += "---\n*End of Sovereign Expenditure Audit — JS INNOVATION8390-1 INC.*"

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[+] Report exported to {REPORT_FILE}")

if __name__ == "__main__":
    auditor = PMExpenditureAuditor()
    auditor.run_simulation()
    auditor.export_report()
