"""Minimal conftest for rules engine tests.

These tests are pure computation — no database, no LLM, no async.
"""

import sys
from pathlib import Path

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
