#!/usr/bin/env python3
"""
Basel Audit Ledger - Cryptographic Integrity & Hash Chain Verifier
Zero-dependency Python script to validate SHA-256 provenance chaining in SQLite vaults.
"""

import sqlite3
import hashlib

DB_FILE = "basel_audit_simulation.db"

def verify_chain():
    print(f"[*] Opening audit vault: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Retrieve records in chronological order
    cursor.execute('''
        SELECT id, metric_id, category, description, audited_value, basel_threshold, previous_hash, current_hash, timestamp 
        FROM basel_audit_records ORDER BY id ASC
    ''')
    records = cursor.fetchall()
    conn.close()

    if not records:
        print("[-] No records found in the audit database.")
        return

    print(f"[*] Loaded {len(records)} audit record(s). Verifying SHA-256 chain...")
    
    expected_prev_hash = "GENESIS_BASEL_HASH_CANADA"
    chain_valid = True

    for row in records:
        rec_id, metric_id, category, description, audited_value, threshold, prev_hash, curr_hash, timestamp = row
        
        # 1. Verify previous hash linkage
        if prev_hash != expected_prev_hash:
            print(f"[!] BROKEN CHAIN at ID {rec_id} ({metric_id}): Expected previous hash '{expected_prev_hash[:12]}...', got '{prev_hash[:12]}...'")
            chain_valid = False

        # 2. Recompute current hash using exact base fields
        # Note: description is included implicitly or explicitly depending on engine structure. 
        # Let's match the exact hashing formula used in td_basel_audit_simulator.py:
        hash_base = f"{metric_id}|{category}|{description}|{audited_value}|{threshold}|{prev_hash}|{timestamp}"
        recomputed_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()

        if recomputed_hash != curr_hash:
            print(f"[!] TAMPER DETECTED at ID {rec_id} ({metric_id}): Stored hash does not match recomputed hash!")
            print(f"    Stored:     {curr_hash}")
            print(f"    Recomputed: {recomputed_hash}")
            chain_valid = False
        else:
            print(f"[✓] Record ID {rec_id} [{metric_id}] -> Hash Verified Match ({curr_hash[:12]}...)")

        expected_prev_hash = curr_hash

    print("\n" + "="*50)
    if chain_valid:
        print("🟢 SUCCESS: The Basel audit cryptographic hash chain is 100% INTACT and UNTAMPERED.")
    else:
        print("🔴 FAILURE: Integrity check failed. Chain corruption or tampering detected.")
    print("="*50)

if __name__ == "__main__":
    verify_chain()
