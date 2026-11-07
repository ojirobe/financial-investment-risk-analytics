"""Streamlit Community Cloud entry point."""

from pathlib import Path
from runpy import run_path


run_path(str(Path(__file__).parent / "dashboards" / "app.py"), run_name="__main__")

