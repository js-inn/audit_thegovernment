import sqlite3
import hashlib
import json
from datetime import datetime, timezone

def initialize_whistleblower_vault():
    db_path = "whistleblower_vault.db"
    print(f"[*] Initializing Whistleblower Provenance Vault: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS whistleblower_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id TEXT UNIQUE,
        creator_uuid TEXT,
        cryptographic_anchor TEXT,
        category TEXT,
        payload_json TEXT,
        previous_hash TEXT,
        current_hash TEXT,
        timestamp TEXT
    )
    """)
    
    record_data = {
        "record_id": "WB-PROV-2026-001",
        "creator_uuid": "e4f1b2a7-6d3c-4902-8a5e-9f7b6c5d4e1a",
        "cryptographic_anchor": "3d9f8a21-c5e7-4b6a-9128-f0d3e2a1b9c7",
        "subject": "Systemic Malpractice & Uncollected Federal Contract CW2321555",
        "status": "SECURE_PROVENANCE_ANCHORED"
    }
    
    payload_str = json.dumps(record_data, sort_keys=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    
    cursor.execute("SELECT current_hash FROM whistleblower_records ORDER BY id DESC LIMIT 1;")
    row = cursor.fetchone()
    prev_hash = row[0] if row else "0000000000000000000000000000000000000000000000000000000000000000"
    
    hasher = hashlib.sha256()
    hasher.update(f"{prev_hash}{record_data['record_id']}{payload_str}{timestamp}".encode("utf-8"))
    curr_hash = hasher.hexdigest()
    
    try:
        cursor.execute("""
        INSERT INTO whistleblower_records (record_id, creator_uuid, cryptographic_anchor, category, payload_json, previous_hash, current_hash, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record_data["record_id"],
            record_data["creator_uuid"],
            record_data["cryptographic_anchor"],
            "Whistleblower Provenance Audit Log",
            payload_str,
            prev_hash,
            curr_hash,
            timestamp
        ))
        conn.commit()
        print(f"[✓] Successfully recorded and chained provenance entry {record_data['record_id']}")
        print(f"[✓] SHA-256 Hash: {curr_hash}")
    except sqlite3.IntegrityError:
        print("[!] Record already exists in vault.")
        
    conn.close()

if __name__ == "__main__":
    initialize_whistleblower_vault()
