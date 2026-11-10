#!/usr/env/python3
"""
Treasury Board Secretariat (TBS) Vault: Tamper Simulation Suite
Injects an unauthorized modification into tbs_sole_source_vault.db to test SHA-256 chain detection.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import sys
from pathlib import Path

DB_FILE = "tbs_sole_source_vault.db"

def simulate_tampering():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run tbs_sole_source_audit.py first.")
        sys.exit(1)

    print(f"[*] Opening TBS vault for unauthorized mutation: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Stealthily tamper with MSA Contract ID CW2321555 amount and finding
    print("[!] INJECTING UNAUTHORIZED MUTATION: Altering MSA Contract CW2321555 value from $3,750,000.00 to $10,000.00...")
    cursor.execute("""
        UPDATE tbs_procurement_contracts 
        SET total_value_cad = 10000.0, audit_finding = 'MUTATED_UNAUTHORIZED_COVERUP'
        WHERE contract_id = 'CW2321555'
    """)
    conn.commit()
    conn.close()

    print("[+] Tampering complete. Run 'python3 verify_tbs_chain.py' to observe the integrity verifier catch the breach.")

if __name__ == "__main__":
    simulate_tampering()
