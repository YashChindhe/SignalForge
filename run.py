#!/usr/bin/env python3
"""SignalForge — Automated Signal Analysis Workbench."""

import sys
import os

# Ensure src is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui.main_window import main

if __name__ == "__main__":
    main()
