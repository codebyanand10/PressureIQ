"""PressureIQ - Dependency and Environment Verification Script.

Verifies the availability and versions of all required libraries in the environment,
reports detailed diagnostics, and checks overall environment readiness.
"""

from __future__ import annotations

import importlib
import os
import platform
import sys
from typing import Dict, List, Tuple


REQUIRED_DEPENDENCIES: List[Tuple[str, str]] = [
    # (import_name, display_name)
    ("pandas", "Pandas"),
    ("numpy", "NumPy"),
    ("pyarrow", "PyArrow"),
    ("sklearn", "Scikit-learn"),
    ("scipy", "SciPy"),
    ("statsmodels", "Statsmodels"),
    ("matplotlib", "Matplotlib"),
    ("seaborn", "Seaborn"),
    ("plotly", "Plotly"),
    ("streamlit", "Streamlit"),
    ("jupyter", "Jupyter"),
    ("ipykernel", "IPyKernel"),
    ("joblib", "Joblib"),
    ("openpyxl", "OpenPyXL"),
    ("yaml", "PyYAML"),
    ("dotenv", "Python-dotenv"),
    ("pytest", "Pytest"),
    ("pytest_cov", "Pytest-cov"),
]


def check_dependencies() -> Dict[str, Dict[str, str]]:
    """Test importing every required dependency and capture version or failure."""
    results: Dict[str, Dict[str, str]] = {}

    for import_name, display_name in REQUIRED_DEPENDENCIES:
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, "__version__", "Available")
            results[display_name] = {"status": "INSTALLED", "version": str(version), "error": ""}
        except Exception as exc:
            error_msg = f"{type(exc).__name__}: {str(exc)}"
            results[display_name] = {"status": "FAILED", "version": "N/A", "error": error_msg}

    return results


def main() -> int:
    """Run environment and dependency audit."""
    print("=" * 80)
    print("  PRESSUREIQ — ENVIRONMENT & DEPENDENCY AUDIT REPORT")
    print("=" * 80)
    print(f"Python Version:   {platform.python_version()} ({platform.architecture()[0]})")
    print(f"Python Executable:{sys.executable}")
    print(f"Operating System: {platform.system()} {platform.release()} ({platform.version()})")
    print(f"Virtual Env:      {'Yes' if sys.prefix != sys.base_prefix else 'No'} ({sys.prefix})")
    print("-" * 80)
    print(f"{'Package':<20} | {'Status':<12} | {'Version':<18} | {'Details / Error'}")
    print("-" * 80)

    results = check_dependencies()
    passed = 0
    failed = 0

    for display_name, info in results.items():
        status = info["status"]
        ver = info["version"]
        err = info["error"]
        status_marker = "[✓] PASS" if status == "INSTALLED" else "[✗] FAIL"

        if status == "INSTALLED":
            passed += 1
            print(f"{display_name:<20} | {status_marker:<12} | {ver:<18} | OK")
        else:
            failed += 1
            # Truncate error message if too long
            short_err = err[:40] + "..." if len(err) > 40 else err
            print(f"{display_name:<20} | {status_marker:<12} | {ver:<18} | {short_err}")

    print("-" * 80)
    print(f"Summary: {passed} passed, {failed} failed out of {len(REQUIRED_DEPENDENCIES)} packages.")

    if failed == 0:
        print("Overall Environment Status: READY (100% Dependencies Verified)")
        return 0
    else:
        print("Overall Environment Status: PARTIALLY CONFIGURED (Review Failed Packages Above)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
