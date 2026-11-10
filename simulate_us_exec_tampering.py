#!/usr/env/python3
"""
US Executive Expenditure Vault: Tamper Simulation Suite
Injects an unauthorized modification into us_executive_expenditure_vault.db to test SHA-256 chain detection.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import sys
from pathlib import Path

DB_FILE = "us_executive_expenditure_vault.db"

def simulate_tampering():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run us_executive_expenditure_audit.py first.")
        sys.exit(1)

    print(f"[*] Opening US executive expenditure vault for unauthorized mutation: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Stealthily tamper with the executive airlift / transport record amount
    print("[!] INJECTING UNAUTHORIZED MUTATION: Altering Air Force One support expense amount from $12,500,000.00 to $1,500,000.00...")
    cursor.execute("""
        UPDATE us_executive_expenditures 
        SET amount_usd = 1500000.0, audit_finding = 'MUTATED_EXECUTIVE_AIRLIFT_COVERUP'
        WHERE expense_id = 'USEC-EXP-2026-Q1-012'
    """)
    conn.commit()
    conn.close()

    print("[+] Tampering complete. Run 'python3 verify_us_exec_chain.py' to observe the integrity verifier catch the cover-up.")

if __name__ == "__main__":
    simulate_tampering()
