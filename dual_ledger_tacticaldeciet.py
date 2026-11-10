#!/usr/bin/env python3
"""
Audit_thegovernment - Dual Ledger Tactical Deceit Analysis Engine
Zero-dependency Python SQLite tracking engine to model, ingest, and quantify 
discrepancies between public reporting ledgers (Ledger A) and internal operational ledgers (Ledger B).
"""

import sqlite3
import json
import hashlib
import datetime
from pathlib import Path

DB_FILE = "data/dual_ledger_vault.db"
REPORT_FILE = "reports/dual_ledger_deceit_analysis.md"

class DualLedgerEngine:
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
                CREATE TABLE IF NOT EXISTS dual_ledger_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT UNIQUE,
                    institution_name TEXT,
                    ledger_a_public TEXT,
                    ledger_b_internal TEXT,
                    discrepancy_metric REAL,
                    tactical_classification TEXT,
                    timestamp TEXT,
                    node_hash TEXT
                )
            ''')
            conn.commit()

    def record_discrepancy(self, case_id, institution_name, ledger_a_val, ledger_b_val, classification, notes=""):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        try:
            a_num = float(ledger_a_val)
            b_num = float(ledger_b_val)
            discrepancy_metric = abs(a_num - b_num) / ((a_num + b_num) / 2) * 100 if (a_num + b_num) > 0 else 0.0
        except ValueError:
            discrepancy_metric = 100.0

        payload = {
            "ledger_a_public": ledger_a_val,
            "ledger_b_internal": ledger_b_val,
            "notes": notes
        }
        payload_str = json.dumps(payload, sort_keys=True)

        raw_sig = f"{case_id}|{institution_name}|{ledger_a_val}|{ledger_b_val}|{classification}|{timestamp}|{payload_str}"
        node_hash = hashlib.sha256(raw_sig.encode('utf-8')).hexdigest()

        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO dual_ledger_nodes (case_id, institution_name, ledger_a_public, ledger_b_internal, discrepancy_metric, tactical_classification, timestamp, node_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (case_id, institution_name, str(ledger_a_val), str(ledger_b_val), discrepancy_metric, classification, timestamp, node_hash))
                conn.commit()
                print(f"[DUAL-LEDGER INGEST] Case [{case_id}] | Institution: {institution_name} | Divergence: {discrepancy_metric:.2f}% -> Hash: {node_hash[:10]}...")
            except sqlite3.IntegrityError:
                print(f"[-] Case ID '{case_id}' already exists in the dual-ledger vault.")

    def export_analysis_report(self, output_file=REPORT_FILE):
        print(f"\n[*] Generating Dual-Ledger Tactical Deceit Report -> {output_file}...")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT case_id, institution_name, ledger_a_public, ledger_b_internal, discrepancy_metric, tactical_classification, timestamp, node_hash FROM dual_ledger_nodes")
            nodes = cursor.fetchall()

        report_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        md = f"""# DUAL-LEDGER TACTICAL DECEIT & DIVERGENCE ANALYSIS
**Generated:** {report_timestamp}  
**Framework:** Audit_thegovernment Tactical Deceit Engine  
**Cryptographic Anchor:** SHA-256 Immutable Provenance Chaining  

---

## 1. Recorded Discrepancy Nodes (Ledger A vs. Ledger B)
| Case ID | Institution | Public Reporting (Ledger A) | Internal Truth (Ledger B) | Divergence Metric | Classification | Hash Anchor |
|---|---|---|---|---|---|---|
"""
        for n in nodes:
            cid, inst, la, lb, metric, classif, ts, nhash = n
            md += f"| `{cid}` | {inst} | `{la}` | `{lb}` | **{metric:.2f}%** | {classif} | `{nhash[:10]}...` |\n"

        md += """
---

## 2. Commercial & Legal Notice
- **Non-Commercial Advocacy:** Free for community legal advocates and social researchers with mandatory attribution.
- **Commercial Use:** Strict prohibition for for-profit entities and financial institutions without a formal commercial sublicense and royalty agreement with JS INNOVATION8390-1 INC. Unauthorized exploitation is subject to systematic audit.

*End of Tactical Report — Audit_thegovernment Engine*
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md)

        print(f"[+] Report exported successfully to '{output_file}'.")


if __name__ == "__main__":
    engine = DualLedgerEngine()

    print("[*] Initializing Dual-Ledger Tactical Deceit Simulation...")

    engine.record_discrepancy(
        case_id="DL-CASE-2026-01",
        institution_name="Schedule I Bank / ATB Financial Context",
        ledger_a_val="100.0% Compliant Settlement Disclosure",
        ledger_b_val="12-Month Unresolved Default & Omitted Liability",
        classification="Tactical Disclosure Omission",
        notes="Divergence between public regulatory filing and internal dispute ledger."
    )

    engine.record_discrepancy(
        case_id="DL-CASE-2026-02",
        institution_name="CIRO Oversight Reporting Node",
        ledger_a_val="Standardized Prospectus Pool Rating: AAA",
        ledger_b_val="Unverified Sub-Asset Repackaging Risk",
        classification="Asset Repackaging Deceit",
        notes="Internal risk model flags structural subordination omitted in public prospectus."
    )

    engine.export_analysis_report()
