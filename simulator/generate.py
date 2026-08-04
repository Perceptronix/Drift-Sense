#!/usr/bin/env python3
"""SEMICON 2026 Synthetic SEM Image Generator — CLI entry point.

Usage
-----
    python generate.py build-library --out structure_library/semicon.gds
    python generate.py run     --config configs/demo.yml --out demo_output
    python generate.py batch   --config configs/demo.yml --n 16 --out demo_output
    python generate.py self-check
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SRC = _HERE / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
if str(_HERE) not in os.environ.get("PYTHONPATH", ""):
    os.environ["PYTHONPATH"] = str(_SRC) + os.pathsep + os.environ.get("PYTHONPATH", "")

from semicon.orchestration.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
