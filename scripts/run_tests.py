#!/usr/bin/env python
"""
Run all tests for WBS BPKH
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run pytest"""
    root = Path(__file__).parent.parent
    tests_path = root / "tests"

    subprocess.run([
        sys.executable, "-m", "pytest",
        str(tests_path),
        "-v",
        "--tb=short"
    ])


if __name__ == "__main__":
    main()
