#!/usr/bin/env python3
"""get-cp3-status.py — 读取 harness state 并返回 CP3 状态"""
import json
import sys
from pathlib import Path

state_file = Path("harness/feedback/state/state.json")
if not state_file.exists():
    print("unknown")
    sys.exit(0)

state = json.load(open(state_file))
cp3 = state.get("checkpoints", {}).get("CP3", {})

# 支持两种格式：字符串 "pending" 或对象 {"status": "completed"}
if isinstance(cp3, str):
    print(cp3)
elif isinstance(cp3, dict):
    print(cp3.get("status", "unknown"))
else:
    print("unknown")
