#!/usr/env/python3
"""
Minister of Finance Vault: Tamper Simulation Suite
Injects an unauthorized modification into finance_minister_vault.db to test SHA-256 chain detection.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import sys
from pathlib import Path

DB_FILE = "finance_minister_vault.db"

def simulate_tampering():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run finance_minister_expenditure_audit.py first.")
        sys.exit(1)

    print(f"[*] Opening finance vault for unauthorized mutation: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Stealthily tamper with the sole-source macro-consulting contract amount
    print("[!] INJECTING UNAUTHORIZED MUTATION: Altering advisory contract amount from $2,100,000.00 to $100,000.00...")
    cursor.execute("""
        UPDATE finance_minister_expenditures 
        SET amount_cad = 100000.0, audit_finding = 'MUTATED_COVERUP_AUTHORIZED'
        WHERE expense_id = 'FIN-2026-Q1-088'
    """)
    conn.commit()
    conn.close()

    print("[+] Tampering complete. Run 'python3 verify_finance_chain.py' to observe the integrity verifier catch the breach.")

if __name__ == "__main__":
    simulate_tampering()
