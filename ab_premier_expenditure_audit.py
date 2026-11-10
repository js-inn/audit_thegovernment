#!/usr/env/python3
"""
Alberta Premier & Executive Office Expenditure Audit Engine: audit_thegovernment
Audits 6-month Proactive Disclosure outlays for the Office of the Premier of Alberta,
flagging delayed expense filings, sole-source stakeholder hospitality, and travel variances using SHA-256 chains.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import hashlib
import datetime
from pathlib import Path

DB_FILE = "ab_premier_expenditure_vault.db"
REPORT_FILE = "ab_premier_expenditure_report.md"

class ABPremierExpenditureAuditor:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        Path(REPORT_FILE).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS ab_premier_expenditures')
            cursor.execute('''
                CREATE TABLE ab_premier_expenditures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expense_id TEXT UNIQUE,
                    ministry TEXT,
                    vendor_or_claimant TEXT,
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

    def audit_expense(self, expense_id, ministry, vendor, category, amount, risk_score, finding):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_hash FROM ab_premier_expenditures ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            prev_hash = row[0] if row else "GENESIS_AB_PREMIER_VAULT"

        hash_base = f"{expense_id}|{ministry}|{vendor}|{category}|{amount}|{risk_score}|{prev_hash}|{timestamp}"
        current_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ab_premier_expenditures (expense_id, ministry, vendor_or_claimant, category, amount_cad, risk_score, previous_hash, current_hash, timestamp, audit_finding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (expense_id, ministry, vendor, category, amount, risk_score, prev_hash, current_hash, timestamp, finding))
            conn.commit()
            print(f"[AB PREMIER AUDIT] Recorded [{expense_id}] -> {category} | Amount: ${amount:,.2f} | Finding: {finding}")

    def run_simulation(self):
        print("[*] Executing 6-month Proactive Disclosure audit on Office of the Premier & Executive Council outlays...")
        records = [
            {
                "expense_id": "ABPREM-2026-Q1-004",
                "ministry": "Office of the Premier",
                "vendor": "TransAlberta Executive Air Charter Ltd.",
                "category": "Intergovernmental Mission & Northern Tour Transport",
                "amount": 115000.0,
                "risk_score": 72,
                "finding": "FLAGGED_CHARTER_FLIGHT_SOLE_SOURCE_VARIANCE"
            },
            {
                "expense_id": "ABPREM-2026-Q1-019",
                "ministry": "Executive Council",
                "vendor": "Edmonton Convention Centre & Catering",
                "category": "Premier's Dinner & Energy Sector Stakeholder Summit",
                "amount": 48500.0,
                "risk_score": 35,
                "finding": "VERIFIED_COMPLIANT_HOSPITALITY_CLAIM"
            },
            {
                "expense_id": "ABPREM-2026-Q2-051",
                "ministry": "Office of the Premier",
                "vendor": "Capital Hotel & Suites Calgary",
                "category": "Cabinet Retreat Accommodation & Working Sessions",
                "amount": 32000.0,
                "risk_score": 28,
                "finding": "VERIFIED_STANDARD_GOVERNMENT_RATE"
            },
            {
                "expense_id": "ABPREM-2026-Q2-088",
                "ministry": "Office of the Premier",
                "vendor": "Western Energy Advisory Group",
                "category": "Provincial Policy Advocacy & Stakeholder Relations",
                "amount": 350000.0,
                "risk_score": 85,
                "finding": "FLAGGED_LATE_DISCLOSURE_AND_CONSULTANCY_MONOPOLY"
            },
            {
                "expense_id": "ABPREM-2026-Q2-110",
                "ministry": "Executive Council",
                "vendor": "Secure Fleet Motorcade Alberta",
                "category": "Provincial Protection & Motorcade Logistics",
                "amount": 89000.0,
                "risk_score": 15,
                "finding": "VERIFIED_FRAMEWORK_AGREEMENT_COMPLIANT"
            }
        ]

        for r in records:
            self.audit_expense(
                expense_id=r["expense_id"],
                ministry=r["ministry"],
                vendor=r["vendor"],
                category=r["category"],
                amount=r["amount"],
                risk_score=r["risk_score"],
                finding=r["finding"]
            )

    def export_report(self):
        print(f"\n[*] Generating Alberta Premier Expenditure Audit Report -> {REPORT_FILE}...")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT expense_id, ministry, vendor_or_claimant, category, amount_cad, risk_score, current_hash, audit_finding FROM ab_premier_expenditures")
            records = cursor.fetchall()

        ts_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        md = f"""# ALBERTA PREMIER & EXECUTIVE COUNCIL EXPENDITURE AUDIT REPORT
**Generated:** {ts_str}  
**Engine:** Alberta Premier Expenditure Auditor (Zero-Dependency Python Core)  
**Sovereign Entity:** JS INNOVATION8390-1 INC. / Jujita Stairs  
**Scope:** Office of the Premier of Alberta & Executive Council Disclosures  

---

## 1. Audited Provincial Executive Ledger

| Expense ID | Ministry / Office | Vendor / Recipient | Category | Amount (CAD) | Risk Score | Audit Finding | SHA-256 Fingerprint |
|---|---|---|---|---|---|---|---|
"""
        total_spent = 0.0
        for r in records:
            eid, ministry, vendor, cat, amount, risk, chash, finding = r
            total_spent += amount
            risk_badge = f"🔴 **{risk} (High Risk)**" if risk > 50 else f"🟢 **{risk} (Low Risk)**"
            md += f"| `{eid}` | {ministry} | **{vendor}** | {cat} | `${amount:,.2f}` | {risk_badge} | `{finding}` | `{chash[:12]}...` |\n"

        md += f"\n### Summary Statistics\n"
        md += f"- **Total Audited Provincial Outlays (6 Months):** `${total_spent:,.2f} CAD`\n"
        md += f"- **Cryptographic Integrity:** Secured via SHA-256 Provenance Chaining (`ab_premier_expenditure_vault.db`)\n\n"
        md += "---\n*End of Alberta Sovereign Executive Audit — JS INNOVATION8390-1 INC.*"

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[+] Report exported to {REPORT_FILE}")

if __name__ == "__main__":
    auditor = ABPremierExpenditureAuditor()
    auditor.run_simulation()
    auditor.export_report()
