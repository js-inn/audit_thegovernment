#!/usr/env/python3
"""
Basel Audit Vault: Tamper Simulation Suite
Injects an unauthorized modification into basel_audit_simulation.db to test SHA-256 chain detection.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import sys
from pathlib import Path

DB_FILE = "basel_audit_simulation.db"

def tamper_database():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run td_basel_audit_simulator.py first.")
        sys.exit(1)

    print(f"[*] Opening audit vault for malicious injection: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Inspect record before tampering
    cursor.execute("SELECT metric_id, audited_value, status FROM basel_metrics WHERE metric_id = 'BASEL-LEVERAGE-03'")
    row = cursor.fetchone()
    if not row:
        print("[-] Target metric 'BASEL-LEVERAGE-03' not found in vault.")
        sys.exit(1)

    print(f"[-] BEFORE TAMPERING -> Metric: {row[0]} | Audited Value: {row[1]} | Status: {row[2]}")

    # Inject unauthorized change without updating hash
    print("[!] INJECTING UNAUTHORIZED MODIFICATION: Changing Leverage Ratio from 4.3 to 7.5...")
    cursor.execute("""
        UPDATE basel_metrics 
        SET audited_value = 7.5, status = 'FORGED_COMPLIANT_OVERRIDE'
        WHERE metric_id = 'BASEL-LEVERAGE-03'
    """)
    conn.commit()

    cursor.execute("SELECT metric_id, audited_value, status FROM basel_metrics WHERE metric_id = 'BASEL-LEVERAGE-03'")
    row_after = cursor.fetchone()
    print(f"[!] AFTER TAMPERING  -> Metric: {row_after[0]} | Audited Value: {row_after[1]} | Status: {row_after[2]}")
    conn.close()

    print("[*] Tampering complete. Now run 'python3 verify_basel_chain.py' to observe the cryptographic verifier catch this breach.")

if __name__ == "__main__":
    tamper_database()
