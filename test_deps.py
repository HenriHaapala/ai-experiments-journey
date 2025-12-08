#!/usr/bin/env python
"""Test if requirements.txt dependencies can be resolved"""
import subprocess
import sys

print("Testing dependency resolution...")
print("=" * 60)

result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "--dry-run", "-r", "backend/requirements.txt"],
    capture_output=True,
    text=True
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print("\nReturn code:", result.returncode)

if result.returncode != 0:
    print("\n❌ Dependency resolution FAILED")
    sys.exit(1)
else:
    print("\n✅ Dependency resolution SUCCESS")
