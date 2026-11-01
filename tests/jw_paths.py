"""Portable paths shared by regression tests.

Set JW_LEGACY_HOME to the directory prepared by legacy_layout.sh. When unset,
use the repository's local _legacy directory so tests also work on macOS and
Windows checkouts without creating /home/claude.
"""
import os
import sys
from pathlib import Path

TESTS = Path(__file__).resolve().parent
ROOT = TESTS.parent
HOME = Path(os.environ.get("JW_LEGACY_HOME", ROOT / "_legacy"))
DRAWTOOL = HOME / "drawtool"
VFX = HOME / "vfx"
OFFLINE_URL = (DRAWTOOL / "offline.html").as_uri()

# Keep imports simple for scripts launched from nested test directories.
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))
