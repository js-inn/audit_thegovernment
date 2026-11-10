#!/usr/env/python3
"""
Basel Audit Vault: SHA-256 Cryptographic Chain Verifier
Validates the immutability and provenance chaining of basel_audit_simulation.db
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import hashlib
import sys
from pathlib import Path

DB_FILE = "basel_audit_simulation.db"

def verify_chain():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run td_basel_audit_simulator.py first.")
        sys.exit(1)

    print(f"[*] Opening audit vault: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, metric_id, description, audited_value, threshold, status, previous_hash, current_hash, timestamp 
        FROM basel_metrics ORDER BY id ASC
    """)
    records = cursor.fetchall()
    conn.close()

    if not records:
        print("[-] No audit records found in the vault.")
        return

    print(f"[*] Loaded {len(records)} audit record(s). Verifying SHA-256 chain...")
    
    expected_prev_hash = "GENESIS_BASEL_AUDIT_VAULT_CANADA"
    chain_valid = True

    for row in records:
        rec_id, metric_id, desc, val, thresh, status, prev_hash, current_hash, timestamp = row

        if prev_hash != expected_prev_hash:
            print(f"[!] CHAIN BREAK at Record ID {rec_id} ({metric_id}): Previous hash mismatch!")
            chain_valid = False

        hash_base = f"{metric_id}|{desc}|{val}|{thresh}|{status}|{prev_hash}|{timestamp}"
        recomputed_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()

        if recomputed_hash != current_hash:
            print(f"[!] TAMPER DETECTED at ID {rec_id} ({metric_id}): Stored hash does not match recomputed hash!")
            print(f"    Stored:     {current_hash}")
            print(f"    Recomputed: {recomputed_hash}")
            chain_valid = False
        else:
            print(f"[✓] Record ID {rec_id} [{metric_id}] -> Hash Verified Match ({current_hash[:12]}...)")

        expected_prev_hash = current_hash

    print("\n" + "="*50)
    if chain_valid:
        print("🟢 SUCCESS: The Basel audit cryptographic hash chain is 100% INTACT and UNTAMPERED.")
        print("="*50)
        sys.exit(0)
    else:
        print("🔴 FAILURE: Integrity check failed. Chain corruption or tampering detected.")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    verify_chain()
