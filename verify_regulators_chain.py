#!/usr/env/python3
"""
Regulators Companion: SHA-256 Cryptographic Chain Verifier
Validates the immutability and provenance chaining of regulators_companion.db
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import sqlite3
import hashlib
import sys
from pathlib import Path

DB_FILE = "regulators_companion.db"

def verify_chain():
    if not Path(DB_FILE).exists():
        print(f"[-] Error: Audit database '{DB_FILE}' not found. Run regulators_companion_engine.py first.")
        sys.exit(1)

    print(f"[*] Opening audit vault: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, tender_id, department, vendor_name, contract_value, risk_score, previous_hash, current_hash, timestamp 
        FROM procurement_audits ORDER BY id ASC
    """)
    records = cursor.fetchall()
    conn.close()

    if not records:
        print("[-] No audit records found in the vault.")
        return

    print(f"[*] Loaded {len(records)} procurement record(s). Verifying SHA-256 chain...")
    
    expected_prev_hash = "GENESIS_REGULATORS_COMPANION_CANADA"
    chain_valid = True

    for row in records:
        rec_id, tender_id, dept, vendor, val, risk, prev_hash, current_hash, timestamp = row

        if prev_hash != expected_prev_hash:
            print(f"[!] CHAIN BREAK at Record ID {rec_id} ({tender_id}): Previous hash mismatch!")
            chain_valid = False

        hash_base = f"{tender_id}|{dept}|{vendor}|{val}|{risk}|{prev_hash}|{timestamp}"
        recomputed_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()

        if recomputed_hash != current_hash:
            print(f"[!] TAMPER DETECTED at ID {rec_id} ({tender_id}): Stored hash does not match recomputed hash!")
            print(f"    Stored:     {current_hash}")
            print(f"    Recomputed: {recomputed_hash}")
            chain_valid = False
        else:
            print(f"[✓] Record ID {rec_id} [{tender_id}] -> Hash Verified Match ({current_hash[:12]}...)")

        expected_prev_hash = current_hash

    print("\n" + "="*50)
    if chain_valid:
        print("🟢 SUCCESS: Regulators Companion chain is fully intact and verified.")
        print("="*50)
        sys.exit(0)
    else:
        print("🔴 FAILURE: Integrity check failed. Chain corruption or tampering detected.")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    verify_chain()
