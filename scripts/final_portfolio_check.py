"""Final Portfolio Verification Script for EduSense AI."""

import os
import sys
import subprocess
from app.db.session import engine, init_db
from app.services.prediction_service import prediction_service


def run_final_check():
    """Execute end-to-end verification of EduSense AI platform."""
    print("==================================================================")
    print("      🎓 EDUSENSE AI — FINAL PORTFOLIO PLATFORM VERIFICATION      ")
    print("==================================================================")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    errors = []

    # 1. Check Key Documentation Files
    print("\n1. Verifying Documentation Files:")
    doc_files = ["README.md", "docs/ARCHITECTURE.md", "docs/DEPLOYMENT_AWS.md", "Dockerfile", "docker-compose.yml"]
    for df in doc_files:
        full_p = os.path.join(base_dir, df)
        if os.path.exists(full_p):
            print(f"  [PASSED] {df} exists ({os.path.getsize(full_p)} bytes)")
        else:
            print(f"  [FAILED] {df} missing")
            errors.append(f"Missing doc file: {df}")

    # 2. Check Database Connectivity
    print("\n2. Verifying Database Schema & ORM Layer:")
    try:
        init_db()
        print("  [PASSED] Database tables initialized and verified successfully.")
    except Exception as e:
        print(f"  [FAILED] Database initialization error: {e}")
        errors.append(f"Database error: {e}")

    # 3. Check ML & Deep Learning Artifacts
    print("\n3. Verifying Machine Learning & PyTorch Artifacts:")
    pt_path = os.path.join(base_dir, "ml", "artifacts", "struggle_model_nn_v1.pt")
    rf_path = os.path.join(base_dir, "ml", "models", "struggle_model_rf_v1.pkl")

    if os.path.exists(pt_path):
        print(f"  [PASSED] PyTorch Deep MLP weights verified ({os.path.getsize(pt_path)} bytes)")
    else:
        print("  [FAILED] PyTorch model weights missing")
        errors.append("PyTorch model weights missing")

    if os.path.exists(rf_path):
        print(f"  [PASSED] Random Forest model verified ({os.path.getsize(rf_path)} bytes)")
    else:
        print("  [FAILED] Random Forest model missing")
        errors.append("Random Forest model missing")

    # 4. Run Pytest Suite
    print("\n4. Running Full Automated Pytest Suite:")
    res = subprocess.run([sys.executable, "-m", "pytest", "-v"], cwd=base_dir, capture_output=True, text=True)
    if res.returncode == 0:
        print("  [PASSED] All automated pytest suites passed successfully!")
    else:
        print("  [FAILED] Pytest suite failed:")
        print(res.stdout)
        print(res.stderr)
        errors.append("Pytest suite execution failed")

    print("\n==================================================================")
    if errors:
        print(f"❌ Final Verification Failed with {len(errors)} error(s).")
        sys.exit(1)
    else:
        print("🎉 ALL 12 SPRINTS FULLY BUILT, VERIFIED, AND PORTFOLIO READY!")
        print("==================================================================")


if __name__ == "__main__":
    run_final_check()
