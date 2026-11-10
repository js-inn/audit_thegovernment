#!/usr/bin/env python3
"""
Tamper Demonstration Script
Silently modifies a record in basel_audit_simulation.db to test SHA-256 integrity detection.
"""

import sqlite3

DB_FILE = "basel_audit_simulation.db"

def tamper_database():
    print(f"[*] Opening audit vault for malicious injection: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Inspect original value for BASEL-LEVERAGE-03
    cursor.execute("SELECT metric_id, audited_value, compliance_status FROM basel_audit_records WHERE metric_id = 'BASEL-LEVERAGE-03'")
    orig = cursor.fetchone()
    print(f"[-] BEFORE TAMPERING -> Metric: {orig[0]} | Audited Value: {orig[1]} | Status: {orig[2]}")
    
    # Silently tamper with the audited value and change status without recalculating hash
    print("[!] INJECTING UNAUTHORIZED MODIFICATION: Changing Leverage Ratio from 4.3 to 7.5...")
    cursor.execute('''
        UPDATE basel_audit_records 
        SET audited_value = 7.5, compliance_status = 'FORGED_COMPLIANT_OVERRIDE'
        WHERE metric_id = 'BASEL-LEVERAGE-03'
    ''')
    conn.commit()
    
    # Verify modification took effect
    cursor.execute("SELECT metric_id, audited_value, compliance_status FROM basel_audit_records WHERE metric_id = 'BASEL-LEVERAGE-03'")
    updated = cursor.fetchone()
    print(f"[!] AFTER TAMPERING  -> Metric: {updated[0]} | Audited Value: {updated[1]} | Status: {updated[2]}")
    conn.close()
    print("[*] Tampering complete. Now run 'python3 verify_basel_chain.py' to observe the cryptographic verifier catch this breach.")

if __name__ == "__main__":
    tamper_database()
