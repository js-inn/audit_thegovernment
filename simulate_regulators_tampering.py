#!/usr/env/python3
"""
Regulators Companion: Tamper Simulation Suite
Injects an unauthorized modification into regulators_companion.db to test SHA-256 chain detection.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import sys
from pathlib import Path

DB_FILE = "regulators_companion.db"

def simulate_tampering():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run regulators_companion_engine.py first.")
        sys.exit(1)

    print(f"[*] Opening audit vault for unauthorized injection: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Target Record ID 2 (TEND-2026-0912) and stealthily alter its contract value or risk score
    # without recomputing the SHA-256 chain.
    print("[*] Injecting unauthorized modification at Record ID 2 (TEND-2026-0912)...")
    cursor.execute("""
        UPDATE procurement_audits 
        SET contract_value = 99999999.99, risk_score = 99, audit_finding = 'UNAUTHORIZED_MUTATION_BY_EXTERNAL_ACTOR'
        WHERE id = 2
    """)
    conn.commit()
    conn.close()

    print("[+] Tampering simulation complete. Run 'python3 verify_regulators_chain.py' to test detection.")

if __name__ == "__main__":
    simulate_tampering()
