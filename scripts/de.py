#!/usr/bin/env python3
"""Run the shared CLI without installing it (works from any consumer project cwd)."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from design_engineering.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
