import os, zipfile, json

def export_archives():
    print("[*] Exporting Sovereign Vault Archives...")
    os.makedirs("archives", exist_ok=True)
    archive_path = "archives/sovereign_vault_snapshot.zip"
    with zipfile.ZipFile(archive_path, 'w') as zipf:
        if os.path.exists("reports"):
            for root, dirs, files in os.walk("reports"):
                for file in files:
                    zipf.write(os.path.join(root, file))
    print(f"[✓] Archive successfully created at {archive_path}")

if __name__ == "__main__":
    export_archives()
