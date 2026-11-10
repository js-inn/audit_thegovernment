#!/usr/env/python3
"""
Sovereign Release Bundler: audit_thegovernment
Bundles all audit reports (.md) and SQLite provenance vaults (.db) into a timestamped ZIP archive 
and generates a SHA-256 cryptographic checksum manifesto.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import zipfile
import hashlib
import datetime
from pathlib import Path

def create_release_bundle():
    timestamp_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    zip_filename = f"audit_sovereign_release_{timestamp_str}.zip"
    manifest_filename = f"audit_sovereign_manifest_{timestamp_str}.sha256"

    # Define file patterns to bundle
    report_files = list(Path(".").glob("*report.md"))
    db_files = list(Path(".").glob("*.db"))
    
    all_artifacts = report_files + db_files

    if not all_artifacts:
        print("[-] Error: No audit reports or database vaults found to bundle.")
        return

    print(f"[*] Creating Sovereign Release Archive: {zip_filename}")
    print(f"[*] Found {len(report_files)} report(s) and {len(db_files)} vault(s).")

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for artifact in all_artifacts:
            zipf.write(artifact)
            print(f"    [+] Added to archive: {artifact.name}")

    # Compute SHA-256 checksum of the generated ZIP archive
    sha256_hash = hashlib.sha256()
    with open(zip_filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    archive_checksum = sha256_hash.hexdigest()

    # Write manifest file
    manifest_content = f"""# SOVEREIGN AUDIT RELEASE MANIFEST
**Generated:** {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Sovereign Entity:** JS INNOVATION8390-1 INC. / Jujita Stairs  
**Archive File:** {zip_filename}  
**SHA-256 Checksum:** `{archive_checksum}`  

---
## Included Artifacts:
"""
    for artifact in all_artifacts:
        manifest_content += f"- `{artifact.name}`\n"

    with open(manifest_filename, "w", encoding="utf-8") as mf:
        mf.write(manifest_content)

    print(f"[+] Manifest generated: {manifest_filename}")
    print(f"==================================================")
    print(f" 🟢 RELEASE BUNDLE SUCCESSFUL")
    print(f" Archive:  {zip_filename}")
    print(f" SHA-256:  {archive_checksum}")
    print(f"==================================================")

if __name__ == "__main__":
    create_release_bundle()
