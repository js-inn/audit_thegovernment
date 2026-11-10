#!/usr/env/python3
"""
MPO Signee Vault: SHA-256 Cryptographic Chain Verifier
Validates immutability and provenance chaining of mpo_signee_vault.db
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import hashlib
import sys
from pathlib import Path

DB_FILE = "mpo_signee_vault.db"

def verify_chain():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run mpo_signee_procurement_audit.py first.")
        sys.exit(1)

    print(f"[*] Opening audit vault: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, contract_id, project_name, supplier, solicitation_method, signing_officer, officer_title, amount_cad, previous_hash, current_hash, timestamp, verification_status 
        FROM mpo_procurement_signees ORDER BY id ASC
    """)
    records = cursor.fetchall()
    conn.close()

    if not records:
        print("[-] No audit records found in the vault.")
        return

    print(f"[*] Loaded {len(records)} MPO signee record(s). Verifying SHA-256 chain...")
    
    expected_prev_hash = "GENESIS_MPO_SIGNEE_VAULT"
    chain_valid = True

    for row in records:
        rec_id, contract_id, project, supplier, method, officer, title, amount, prev_hash, current_hash, timestamp, status = row

        if prev_hash != expected_prev_hash:
            print(f"[!] CHAIN BREAK at Record ID {rec_id} ({contract_id}): Previous hash mismatch!")
            chain_valid = False

        hash_base = f"{contract_id}|{project}|{supplier}|{method}|{officer}|{title}|{amount}|{prev_hash}|{timestamp}"
        recomputed_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()

        if recomputed_hash != current_hash:
            print(f"[!] TAMPER DETECTED at ID {rec_id} ({contract_id}): Stored hash does not match recomputed hash!")
            print(f"    Stored:     {current_hash}")
            print(f"    Recomputed: {recomputed_hash}")
            chain_valid = False
        else:
            print(f"[✓] Record ID {rec_id} [{contract_id}] -> Hash Verified Match ({current_hash[:12]}...)")

        expected_prev_hash = current_hash

    print("\n" + "="*50)
    if chain_valid:
        print("🟢 SUCCESS: MPO signee procurement audit chain is 100% INTACT and UNTAMPERED.")
        print("="*50)
        sys.exit(0)
    else:
        print("🔴 FAILURE: Integrity check failed. Chain corruption or tampering detected.")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    verify_chain()
