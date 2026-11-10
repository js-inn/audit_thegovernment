#!/usr/env/python3
"""
Master Audit Suite Runner: audit_thegovernment
Executes full simulation, verification, tampering, and breach detection 
pipelines across Basel Financial, Regulators Companion, and PM Expenditure modules.
Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs
"""

import subprocess
import sys
import time
from pathlib import Path

def reset_vaults():
    print("[*] Resetting audit vaults for pristine test execution...")
    for db in ["basel_audit_simulation.db", "regulators_companion.db", "pm_expenditure_vault.db"]:
        p = Path(db)
        if p.exists():
            p.unlink()
            print(f"    Removed old vault: {db}")

STEPS = [
    # 1-4: Basel Financial Module
    ("1. Running Basel Financial Audit Simulation", ["python3", "td_basel_audit_simulator.py"], True),
    ("2. Verifying Pristine Basel SHA-256 Chain", ["python3", "verify_basel_chain.py"], True),
    ("3. Simulating Tampering on Basel Vault", ["python3", "simulate_tampering.py"], True),
    ("4. Verifying Basel Chain Breaches (Expecting Failure)", ["python3", "verify_basel_chain.py"], False),
    
    # 5-8: Regulators Companion Module
    ("5. Running Regulators Companion Procurement Audit", ["python3", "regulators_companion_engine.py"], True),
    ("6. Verifying Pristine Regulators SHA-256 Chain", ["python3", "verify_regulators_chain.py"], True),
    ("7. Simulating Tampering on Regulators Vault", ["python3", "simulate_regulators_tampering.py"], True),
    ("8. Verifying Regulators Chain Breaches (Expecting Failure)", ["python3", "verify_regulators_chain.py"], False),

    # 9-12: PM & Federal Expenditure Module
    ("9. Running PM & Federal Expenditure Audit", ["python3", "pm_expenditure_audit.py"], True),
    ("10. Verifying Pristine PM Expenditure SHA-256 Chain", ["python3", "verify_pm_chain.py"], True),
    ("11. Simulating Tampering on PM Expenditure Vault", ["python3", "simulate_pm_tampering.py"], True),
    ("12. Verifying PM Expenditure Chain Breaches (Expecting Failure)", ["python3", "verify_pm_chain.py"], False),
]

def run_suite():
    print("="*70)
    print(" 🏛️  AUDIT_THEGOVERNMENT: MASTER COMPLIANCE & INTEGRITY TEST RUNNER")
    print(" Sovereign Entity: JS INNOVATION8390-1 INC. / Jujita Stairs")
    print("="*70 + "\n")

    reset_vaults()
    print("\n" + "-"*70 + "\n")

    success_count = 0
    total_steps = len(STEPS)

    for title, cmd, expect_success in STEPS:
        print(f"\n[EXEC] {title}")
        print(f"       Command: {' '.join(cmd)}")
        print("-" * 50)
        
        result = subprocess.run(cmd)
        
        if expect_success:
            if result.returncode == 0:
                print(f"\n[PASS] {title} completed successfully.\n")
                success_count += 1
            else:
                print(f"\n[FAIL] {title} failed unexpectedly with exit code {result.returncode}.\n")
                sys.exit(1)
        else:
            if result.returncode != 0:
                print(f"\n[PASS] {title} correctly caught the tamper breach (exit code {result.returncode}).\n")
                success_count += 1
            else:
                print(f"\n[FAIL] {title} expected integrity failure but passed unexpectedly!\n")
                sys.exit(1)
        
        time.sleep(0.3)

    print("="*70)
    print(f" 🟢 MASTER SUITE COMPLETE: {success_count}/{total_steps} Verification Steps Passed.")
    print(" All cryptographic provenance chains and audit vaults verified.")
    print("="*70)

if __name__ == "__main__":
    run_suite()
