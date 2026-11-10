#!/usr/env/python3
"""
ISED Expenditure Vault: SHA-256 Cryptographic Chain Verifier
Validates immutability and provenance chaining of ised_expenditure_vault.db
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import hashlib
import sys
from pathlib import Path

DB_FILE = "ised_expenditure_vault.db"

def verify_chain():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run ised_expenditure_audit.py first.")
        sys.exit(1)

    print(f"[*] Opening audit vault: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, expense_id, branch_or_office, recipient_or_vendor, category, amount_cad, risk_score, previous_hash, current_hash, timestamp 
        FROM ised_expenditures ORDER BY id ASC
    """)
    records = cursor.fetchall()
    conn.close()

    if not records:
        print("[-] No audit records found in the vault.")
        return

    print(f"[*] Loaded {len(records)} ISED expenditure record(s). Verifying SHA-256 chain...")
    
    expected_prev_hash = "GENESIS_ISED_VAULT_CANADA"
    chain_valid = True

    for row in records:
        rec_id, expense_id, branch, recipient, cat, amount, risk, prev_hash, current_hash, timestamp = row

        if prev_hash != expected_prev_hash:
            print(f"[!] CHAIN BREAK at Record ID {rec_id} ({expense_id}): Previous hash mismatch!")
            chain_valid = False

        hash_base = f"{expense_id}|{branch}|{recipient}|{cat}|{amount}|{risk}|{prev_hash}|{timestamp}"
        recomputed_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()

        if recomputed_hash != current_hash:
            print(f"[!] TAMPER DETECTED at ID {rec_id} ({expense_id}): Stored hash does not match recomputed hash!")
            print(f"    Stored:     {current_hash}")
            print(f"    Recomputed: {recomputed_hash}")
            chain_valid = False
        else:
            print(f"[✓] Record ID {rec_id} [{expense_id}] -> Hash Verified Match ({current_hash[:12]}...)")

        expected_prev_hash = current_hash

    print("\n" + "="*50)
    if chain_valid:
        print("🟢 SUCCESS: ISED expenditure audit chain is 100% INTACT and UNTAMPERED.")
        print("="*50)
        sys.exit(0)
    else:
        print("🔴 FAILURE: Integrity check failed. Chain corruption or tampering detected.")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    verify_chain()
