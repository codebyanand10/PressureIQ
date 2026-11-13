"""Streamlit Cloud entry point redirecting to dashboard/app.py."""

from pathlib import Path
import runpy
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

app_path = PROJECT_ROOT / "dashboard" / "app.py"
runpy.run_path(str(app_path), run_name="__main__")

