#!/usr/bin/env python
"""
Run the WBS BPKH Streamlit application
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run Streamlit application"""
    root = Path(__file__).parent.parent
    app_path = root / "app.py"

    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])


if __name__ == "__main__":
    main()
