#!/usr/env/python3
"""
ISED Expenditure Vault: Tamper Simulation Suite
Injects an unauthorized modification into the $45M milestone grant record in ised_expenditure_vault.db 
to test SHA-256 chain detection on major industrial subsidies.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import sys
from pathlib import Path

DB_FILE = "ised_expenditure_vault.db"

def simulate_tampering():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run ised_expenditure_audit.py first.")
        sys.exit(1)

    print(f"[*] Opening ISED expenditure vault for unauthorized milestone mutation: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Stealthily tamper with the $45M NextGen EV Battery grant amount and finding
    print("[!] INJECTING UNAUTHORIZED MUTATION: Altering $45M EV Battery milestone grant amount to $90,000,000.00...")
    cursor.execute("""
        UPDATE ised_expenditures 
        SET amount_cad = 90000000.0, audit_finding = 'MUTATED_UNVERIFIED_GRANT_SUBSIDY'
        WHERE expense_id = 'ISED-2026-Q1-094'
    """)
    conn.commit()
    conn.close()

    print("[+] Tampering complete. Run 'python3 verify_ised_chain.py' to observe the cryptographic verifier catch the breach.")

if __name__ == "__main__":
    simulate_tampering()
