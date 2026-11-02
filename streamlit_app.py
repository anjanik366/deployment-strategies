"""
streamlit_app.py - Standard Streamlit Cloud Entrypoint
Redirects to or imports app.py.
"""
import runpy
from pathlib import Path

app_path = Path(__file__).resolve().parent / "app.py"
runpy.run_path(str(app_path), run_name="__main__")

