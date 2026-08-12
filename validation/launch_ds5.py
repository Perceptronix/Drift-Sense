#!/usr/bin/env python3
"""Launch DS5 generation as a detached process that survives session termination.

Usage: python validation/launch_ds5.py
The actual generation runs as a subprocess with stdout/stderr redirected to a log file.
"""
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "validation" / "run_ds5_production.py"
LOG = ROOT / "logs" / "ds5_generation" / "ds5_production_full.log"

# Build command
cmd = [
    sys.executable,
    str(SCRIPT),
    "--total", "100000",
    "--chunk-size", "10000",
    "--seed", "5005",
    "--workers", "4",
]

print(f"Launching detached DS5 generation...")
print(f"  Command: {' '.join(cmd)}")
print(f"  Log: {LOG}")
print(f"  PID will be printed below")

# Launch as detached process (survives parent termination)
creation_flags = 0
if sys.platform == "win32":
    creation_flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW

with open(LOG, "a", encoding="utf-8") as log_fp:
    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        stdout=log_fp,
        stderr=subprocess.STDOUT,
        creationflags=creation_flags,
        close_fds=True,
    )

print(f"  PID: {proc.pid}")
print(f"\nGeneration is now running independently.")
print(f"Monitor with: tail -f {LOG}")
print(f"Check progress: python -c \"import json; cp=json.load(open('datasets/ds5_final_training/checkpoint.json')); print(f'Done: {len(cp[chr(100)+chr(101)+chr(109)+chr(112)+chr(108)+chr(101)+chr(116)+chr(101)+chr(100)])}/100000')\"")
