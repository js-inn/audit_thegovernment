#!/usr/env/python3
"""
MPO Signee Vault: Tamper Simulation Suite
Injects an unauthorized modification into mpo_signee_vault.db to test SHA-256 chain detection on signing officers.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import sys
from pathlib import Path

DB_FILE = "mpo_signee_vault.db"

def simulate_tampering():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run mpo_signee_procurement_audit.py first.")
        sys.exit(1)

    print(f"[*] Opening MPO signee vault for unauthorized mutation: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Stealthily tamper with the sole-source advisory contract amount and signing officer cover-up
    print("[!] INJECTING UNAUTHORIZED MUTATION: Altering advisory contract amount from $14,500,000.00 to $1,000,000.00...")
    cursor.execute("""
        UPDATE mpo_procurement_signees 
        SET amount_cad = 1000000.0, verification_status = 'MUTATED_COVERUP_AUTHORIZED'
        WHERE contract_id = 'MPO-PROC-2026-089'
    """)
    conn.commit()
    conn.close()

    print("[+] Tampering complete. Run 'python3 verify_mpo_signee_chain.py' to observe the integrity verifier catch the cover-up.")

if __name__ == "__main__":
    simulate_tampering()
