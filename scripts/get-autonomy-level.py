#!/usr/bin/env python3
"""get-autonomy-level.py — 读取 harness state 并返回 autonomy level"""
import json
import sys
from pathlib import Path

state_file = Path("harness/feedback/state/state.json")
if not state_file.exists():
    print("4")
    sys.exit(0)

state = json.load(open(state_file))
print(state.get("autonomy", {}).get("level", 4))
