#!/usr/env/python3
"""
Minister of Finance Vault: SHA-256 Cryptographic Chain Verifier
Validates immutability and provenance chaining of finance_minister_vault.db
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import hashlib
import sys
from pathlib import Path

DB_FILE = "finance_minister_vault.db"

def verify_chain():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run finance_minister_expenditure_audit.py first.")
        sys.exit(1)

    print(f"[*] Opening audit vault: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, expense_id, initiative_or_purpose, recipient_or_vendor, category, amount_cad, risk_score, previous_hash, current_hash, timestamp, audit_finding 
        FROM finance_minister_expenditures ORDER BY id ASC
    """)
    records = cursor.fetchall()
    conn.close()

    if not records:
        print("[-] No audit records found in the vault.")
        return

    print(f"[*] Loaded {len(records)} finance record(s). Verifying SHA-256 chain...")
    
    expected_prev_hash = "GENESIS_FINANCE_MINISTER_VAULT"
    chain_valid = True

    for row in records:
        rec_id, expense_id, purpose, vendor, category, amount, risk_score, prev_hash, current_hash, timestamp, finding = row

        if prev_hash != expected_prev_hash:
            print(f"[!] CHAIN BREAK at Record ID {rec_id} ({expense_id}): Previous hash mismatch!")
            chain_valid = False

        hash_base = f"{expense_id}|{purpose}|{vendor}|{category}|{amount}|{risk_score}|{prev_hash}|{timestamp}"
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
        print("🟢 SUCCESS: Minister of Finance audit chain is 100% INTACT and UNTAMPERED.")
        print("="*50)
        sys.exit(0)
    else:
        print("🔴 FAILURE: Integrity check failed. Chain corruption or tampering detected.")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    verify_chain()
