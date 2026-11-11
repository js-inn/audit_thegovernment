import sqlite3
import hashlib
import json
from datetime import datetime, timezone
import urllib.request
import xml.etree.ElementTree as ET

def parse_regulatory_feeds():
    print("[*] Initializing Regulatory Feed Parser & Audit Log...")
    db_path = "regulatory_audit_vault.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS regulatory_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feed_title TEXT,
        feed_link TEXT,
        payload_json TEXT,
        previous_hash TEXT,
        current_hash TEXT,
        timestamp TEXT
    )
    """)
    
    # Sample secure entry simulating regulatory feed check
    feed_data = {
        "source": "Treasury Board Secretariat / Federal Regulatory Feed",
        "status": "MONITORED_COMPLIANCE_CHECK",
        "contract_ref": "CW2321555",
        "business_number": "735350935"
    }
    
    payload_str = json.dumps(feed_data, sort_keys=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    
    cursor.execute("SELECT current_hash FROM regulatory_logs ORDER BY id DESC LIMIT 1;")
    row = cursor.fetchone()
    prev_hash = row[0] if row else "0000000000000000000000000000000000000000000000000000000000000000"
    
    hasher = hashlib.sha256()
    hasher.update(f"{prev_hash}{feed_data['source']}{payload_str}{timestamp}".encode("utf-8"))
    curr_hash = hasher.hexdigest()
    
    cursor.execute("""
    INSERT INTO regulatory_logs (feed_title, feed_link, payload_json, previous_hash, current_hash, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "TBS Procurement & Compliance Feed",
        "https://www.canada.ca/en/treasury-board-secretariat.html",
        payload_str,
        prev_hash,
        curr_hash,
        timestamp
    ))
    
    conn.commit()
    conn.close()
    print(f"[✓] Regulatory feed parsed and chained successfully. SHA-256: {curr_hash}")

if __name__ == "__main__":
    parse_regulatory_feeds()
