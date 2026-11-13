#!/usr/bin/env python3
"""
Audit Engine JSON Report Exporter (v2.7)
------------------------------------------
Exports core audit tables, velocity risk logs, sovereign IP anchors,
and ministerial enforcement bans into audit_compliance_report.json.
"""

import sqlite3, json, datetime, os

DB_FILENAME = "core_audit.db"
OUTPUT_REPORT = "audit_compliance_report.json"

def export_audit_data():
    if not os.path.exists(DB_FILENAME):
        print(f"[-] Error: Database '{DB_FILENAME}' not found. Run your test runner first.")
        return

    conn = sqlite3.connect(DB_FILENAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    report_data = {
        "metadata": {
            "generated_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "engine_version": "2.7-enforcement-pipeline",
            "jurisdiction": "Government of Canada / Federal Pipeline"
        },
        "portfolios": [],
        "contracts_2025_2026": [],
        "sovereign_ip_valuations": [],
        "fintrac_portfolios": [],
        "transaction_velocity_log": [],
        "sovereign_prior_art_registry": [],
        "ministerial_enforcement_log": []
    }

    try:
        for table in report_data.keys():
            if table == "metadata": continue
            cursor.execute(f"SELECT * FROM {table};")
            report_data[table] = [dict(row) for row in cursor.fetchall()]
    except sqlite3.OperationalError as e:
        print(f"[-] Notice: {e}")
    finally:
        conn.close()

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)

    print(f"[+] Success! Compliance report with ministerial enforcement logs exported to '{OUTPUT_REPORT}'.")

if __name__ == "__main__":
    export_audit_data()
