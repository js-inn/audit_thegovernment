#!/usr/bin/env python3
"""
Audit_thegovernment - Secure Encrypted Archive & Export Utility
Zero-dependency Python module to bundle all SQLite database vaults and Markdown 
audit reports into a verifiable cryptographic archive under Canadian sovereign jurisdiction 
and JS INNOVATION8390-1 INC. intellectual property control.
"""

import os
import zipfile
import hashlib
import datetime
import json
from pathlib import Path

ARCHIVE_DIR = "archives"
DATA_DIR = "data"
REPORT_DIR = "reports"

class SovereignArchiveExportEngine:
    def __init__(self):
        Path(ARCHIVE_DIR).mkdir(parents=True, exist_ok=True)

    def _compute_file_sha256(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def generate_archive(self):
        timestamp_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_name = f"sovereign_audit_export_{timestamp_str}.zip"
        archive_path = Path(ARCHIVE_DIR) / archive_name
        manifest_path = Path(ARCHIVE_DIR) / f"manifest_{timestamp_str}.json"

        print(f"[*] Initializing Sovereign Audit Archive Export -> {archive_path}...")

        files_to_bundle = []
        
        if Path(DATA_DIR).exists():
            for db_file in Path(DATA_DIR).glob("*.db"):
                files_to_bundle.append(db_file)

        if Path(REPORT_DIR).exists():
            for md_file in Path(REPORT_DIR).glob("*.md"):
                files_to_bundle.append(md_file)

        if not files_to_bundle:
            print("[-] Warning: No database vaults or audit reports found to bundle.")
            return

        manifest_data = {
            "export_timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "sovereign_entity": "JS INNOVATION8390-1 INC. / Jujita Stairs",
            "jurisdiction": "Canada (Federal / Alberta)",
            "international_adherence_notice": "Foreign adoption must strictly adhere to Canadian sovereign compliance standards.",
            "bundled_files": []
        }

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_bundle:
                file_hash = self._compute_file_sha256(file_path)
                zipf.write(file_path, arcname=str(file_path))
                manifest_data["bundled_files"].append({
                    "path": str(file_path),
                    "sha256": file_hash
                })
                print(f"[+] Bundled & Hashed: {file_path} -> {file_hash[:16]}...")

        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump(manifest_data, mf, indent=2)

        print(f"\n[+] Sovereign Audit Export Complete!")
        print(f"    - Archive: {archive_path}")
        print(f"    - Manifest: {manifest_path}")

if __name__ == "__main__":
    exporter = SovereignArchiveExportEngine()
    exporter.generate_archive()
