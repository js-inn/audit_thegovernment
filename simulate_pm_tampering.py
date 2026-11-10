#!/usr/env/python3
"""
PM Expenditure Vault: Tamper Simulation Suite
Injects an unauthorized modification into pm_expenditure_vault.db to test SHA-256 chain detection.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import sys
from pathlib import Path

DB_FILE = "pm_expenditure_vault.db"

def simulate_tampering():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run pm_expenditure_audit.py first.")
        sys.exit(1)

    print(f"[*] Opening expenditure vault for unauthorized mutation: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Stealthily tamper with the 'classified infrastructure' record amount or finding
    print("[!] INJECTING UNAUTHORIZED MUTATION: Altering classified expenditure amount from $3,150,000.00 to $50,000.00...")
    cursor.execute("""
        UPDATE federal_expenditures 
        SET amount_cad = 50000.0, audit_finding = 'MUTATED_CLASSIFIED_COVERUP'
        WHERE expense_id = 'PMO-EXP-2026-Q1-089'
    """)
    conn.commit()
    conn.close()

    print("[+] Tampering complete. Run 'python3 verify_pm_chain.py' to observe the integrity verifier catch the cover-up.")

if __name__ == "__main__":
    simulate_tampering()
