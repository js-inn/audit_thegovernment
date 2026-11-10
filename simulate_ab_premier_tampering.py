#!/usr/env/python3
"""
Alberta Premier Expenditure Vault: Tamper Simulation Suite
Injects an unauthorized modification into ab_premier_expenditure_vault.db to test SHA-256 chain detection.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import sys
from pathlib import Path

DB_FILE = "ab_premier_expenditure_vault.db"

def simulate_tampering():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run ab_premier_expenditure_audit.py first.")
        sys.exit(1)

    print(f"[*] Opening Alberta Premier expenditure vault for unauthorized mutation: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Stealthily tamper with the policy advocacy / consultancy record amount
    print("[!] INJECTING UNAUTHORIZED MUTATION: Altering advocacy consultancy expense amount from $350,000.00 to $25,000.00...")
    cursor.execute("""
        UPDATE ab_premier_expenditures 
        SET amount_cad = 25000.0, audit_finding = 'MUTATED_ADVOCACY_COVERUP'
        WHERE expense_id = 'ABPREM-2026-Q2-088'
    """)
    conn.commit()
    conn.close()

    print("[+] Tampering complete. Run 'python3 verify_ab_premier_chain.py' to observe the integrity verifier catch the cover-up.")

if __name__ == "__main__":
    simulate_tampering()
