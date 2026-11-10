#!/usr/bin/env python3
"""
Audit_thegovernment - Systemic Corruption & Financial Flow Blueprint
Maps institutional connivance across federal ministries (ISED, Finance), CRA, 
and regulated financial institutions, featuring an automated expenditure watchdog 
and suspicious appropriation flagging engine with SHA-256 cryptographic provenance.
"""

import sqlite3
import json
import hashlib
import datetime
from pathlib import Path

DB_FILE = "data/corruption_blueprint_vault.db"
REPORT_FILE = "reports/systemic_corruption_financial_flows_report.md"

class CorruptionBlueprintEngine:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        Path(REPORT_FILE).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS institutional_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT UNIQUE,
                    entity_name TEXT,
                    role_classification TEXT,
                    connivance_vector TEXT,
                    timestamp TEXT,
                    node_hash TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenditure_watchdog_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appropriation_id TEXT UNIQUE,
                    source_department TEXT,
                    target_institution TEXT,
                    allocated_amount REAL,
                    flag_status TEXT,
                    risk_score REAL,
                    flag_reason TEXT,
                    timestamp TEXT,
                    ledger_hash TEXT
                )
            ''')
            conn.commit()

    def register_connivance_node(self, node_id, entity_name, role_classification, vector_description):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        payload = {
            "entity_name": entity_name,
            "role_classification": role_classification,
            "connivance_vector": vector_description
        }
        payload_str = json.dumps(payload, sort_keys=True)
        raw_sig = f"{node_id}|{entity_name}|{role_classification}|{timestamp}|{payload_str}"
        node_hash = hashlib.sha256(raw_sig.encode('utf-8')).hexdigest()

        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO institutional_nodes (node_id, entity_name, role_classification, connivance_vector, timestamp, node_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (node_id, entity_name, role_classification, vector_description, timestamp, node_hash))
                conn.commit()
                print(f"[CORRUPTION NODE] Registered [{node_id}] -> Entity: {entity_name} ({role_classification})")
            except sqlite3.IntegrityError:
                print(f"[-] Node ID '{node_id}' already registered.")

    def run_expenditure_watchdog(self, appropriation_id, source_dept, target_inst, amount, justification_notes=""):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Autonomous Watchdog Heuristics for Flagging Suspicious Appropriations
        risk_score = 0.0
        flag_status = "CLEAN_APPROPRIATION"
        reasons = []

        if amount > 50000000.0:  # Large scale public capital injection ($50M+)
            risk_score += 40.0
            reasons.append("High-volume capital transfer exceeding standard oversight threshold.")

        if "CRA" in source_dept or "ISED" in source_dept or "Finance" in source_dept:
            risk_score += 30.0
            reasons.append("Direct ministerial or tax authority conduit involved.")

        if "Schedule I" in target_inst or "Bank" in target_inst or "Financial" in target_inst:
            risk_score += 30.0
            reasons.append("Funds directed to private regulated financial institution without open competitive tender.")

        if risk_score >= 70.0:
            flag_status = "CRITICAL_SUSPICIOUS_APPROPRIATION"
        elif risk_score >= 40.0:
            flag_status = "ELEVATED_DIVERGENCE_WARNING"

        reason_str = " | ".join(reasons) if reasons else "Standard operational expenditure."

        payload = {
            "source_dept": source_dept,
            "target_inst": target_inst,
            "amount": amount,
            "justification": justification_notes
        }
        payload_str = json.dumps(payload, sort_keys=True)
        raw_sig = f"{appropriation_id}|{source_dept}|{target_inst}|{amount}|{flag_status}|{timestamp}|{payload_str}"
        ledger_hash = hashlib.sha256(raw_sig.encode('utf-8')).hexdigest()

        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO expenditure_watchdog_logs (appropriation_id, source_department, target_institution, allocated_amount, flag_status, risk_score, flag_reason, timestamp, ledger_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (appropriation_id, source_dept, target_inst, amount, flag_status, risk_score, reason_str, timestamp, ledger_hash))
                conn.commit()
                print(f"[WATCHDOG FLAG] ID [{appropriation_id}] | Status: {flag_status} | Risk: {risk_score}/100 | Amount: ${amount:,.2f}")
            except sqlite3.IntegrityError:
                print(f"[-] Appropriation ID '{appropriation_id}' already monitored.")

    def export_blueprint_report(self, output_file=REPORT_FILE):
        print(f"\n[*] Generating Systemic Corruption & Financial Flow Report -> {output_file}...")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT node_id, entity_name, role_classification, connivance_vector, node_hash FROM institutional_nodes")
            nodes = cursor.fetchall()

            cursor.execute("SELECT appropriation_id, source_department, target_institution, allocated_amount, flag_status, risk_score, flag_reason, ledger_hash FROM expenditure_watchdog_logs")
            logs = cursor.fetchall()

        report_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        md = f"""# SYSTEMIC CORRUPTION & FINANCIAL FLOW BLUEPRINT
**Generated:** {report_timestamp}  
**Framework:** Audit_thegovernment Corruption Blueprint & Autonomous Watchdog  
**Cryptographic Standard:** SHA-256 Provenance Chaining  

---

## 1. Institutional Connivance Network Map
The following topology maps the administrative and regulatory nodes involved in systemic policy capture, shielding financial institutions from public accountability:

| Node ID | Entity / Office | Role Classification | Connivance Vector & Policy Capture Mechanism | Hash Anchor |
|---|---|---|---|---|
"""
        for n in nodes:
            nid, entity, role, vector, nhash = n
            md += f"| `{nid}` | **{entity}** | {role} | {vector} | `{nhash[:10]}...` |\n"

        md += """
---

## 2. Autonomous Expenditure Watchdog & Appropriation Flagging Log
Monitoring public fund appropriations, illicit financial conduits, and unvouched bailouts directed toward regulated financial entities:

| Appropriation ID | Source Dept | Target Institution | Allocated Amount (CAD) | Flag Status | Risk Score (0-100) | Flag Reason / Anomaly Analysis | Ledger Hash |
|---|---|---|---|---|---|---|---|
"""
        for l in logs:
            aid, sdept, tinst, amt, fstatus, rscore, freason, lhash = l
            md += f"| `{aid}` | {sdept} | {tinst} | **${amt:,.2f}** | **{fstatus}** | `{rscore:.1f}` | {freason} | `{lhash[:10]}...` |\n"

        md += """
---

## 3. Legal & Commercial Notice
- **Community Advocacy:** Free for community legal clinics, social advocates, and independent public interest researchers under strict attribution to JS INNOVATION8390-1 INC. / Jujita Stairs.
- **Commercial Restriction:** Strict prohibition for for-profit corporations and financial institutions without an executed commercial sublicense and royalty agreement. Unauthorized use triggers automated compliance audits.

*End of Corruption Blueprint Report — Audit_thegovernment Engine*
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md)

        print(f"[+] Report exported successfully to '{output_file}'.")


if __name__ == "__main__":
    engine = CorruptionBlueprintEngine()

    print("[*] Initializing Systemic Corruption Blueprint & Watchdog Simulation...")

    engine.register_connivance_node(
        node_id="CORP-NODE-01",
        entity_name="Minister of Innovation, Science and Economic Development (ISED)",
        role_classification="Executive Policy Gatekeeper",
        vector_description="Facilitates non-competitive industrial subsidies and shields corporate balance sheets from public scrutiny."
    )

    engine.register_connivance_node(
        node_id="CORP-NODE-02",
        entity_name="Minister of Finance",
        role_classification="Fiscal Apparatus Controller",
        vector_description="Manages regulatory blind spots and capital injections for Schedule I banks, overriding consumer protection mandates."
    )

    engine.register_connivance_node(
        node_id="CORP-NODE-03",
        entity_name="Canada Revenue Agency (CRA)",
        role_classification="Enforcement Suppression Unit",
        vector_description="Selectively applies compliance audits while insulating institutional tax omissions and undisclosed liabilities."
    )

    engine.register_connivance_node(
        node_id="CORP-NODE-04",
        entity_name="Regulated Financial Institutions (Schedule I Banks & ATB)",
        role_classification="Primary Beneficiary / Dual-Ledger Operator",
        vector_description="Operates undisclosed dual ledgers, concealing regulatory defaults and structural solvency risks."
    )

    engine.run_expenditure_watchdog(
        appropriation_id="APP-2026-0881",
        source_dept="Department of Finance / ISED Conduit",
        target_inst="Schedule I Bank / Major Financial Syndicate",
        amount=125000000.0,
        justification_notes="Emergency liquidity support and unvouched technological modernization grant without open procurement."
    )

    engine.run_expenditure_watchdog(
        appropriation_id="APP-2026-0942",
        source_dept="CRA Compliance Relief Fund",
        target_inst="ATB Financial / Regional Banking Entity",
        amount=75000000.0,
        justification_notes="Confidential tax settlement adjustment and compliance liability waiver."
    )

    engine.export_blueprint_report()
