#!/usr/bin/env python3
"""
Push Sonic Flux to GitHub using HTTPS with embedded token
Bypasses credential manager and uses direct authentication
"""

import subprocess
import os
import re

# Load token from .env file
with open(".env", "r") as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            if key.strip() == "GITHUB_TOKEN":
                TOKEN = value.strip()

# Build HTTPS URL with embedded token
USER_NAME = "Magoo2You"
REPO_NAME = "sonic-flux"

print("=" * 60)
print("SONIC FLUX - PUSHING TO GITHUB (Direct Auth)")
print("=" * 60)
print()
print(f"User: {USER_NAME}")
print(f"Repository: {REPO_NAME}")
print(f"Token (truncated): {TOKEN[:8]}***{TOKEN[-5:]}")
print()

# Create HTTPS URL with token embedded in auth header
GIT_URL = f"https://{TOKEN}@github.com/{USER_NAME}/{REPO_NAME}.git"

print("Step 1: Configuring Git remote...")
print("-" * 60)
subprocess.run(["git", "remote", "set-url", "origin", GIT_URL], shell=True, check=True)
print("✅ Remote URL configured")
print()

# Add and commit all files
print("Step 2: Adding and committing all files...")
print("-" * 60)
result = subprocess.run(["git", "add", "."], capture_output=True, text=True)
if result.returncode == 0:
    print("✅ All files staged")
else:
    print(f"Warning: {result.stderr}")

result = subprocess.run(
    ["git", "commit", "-m", "Initial commit: Sonic Flux music discovery system"],
    capture_output=True, text=True
)
if result.returncode == 0:
    print("✅ Committed successfully!")
    print(result.stdout)
else:
    print(f"Commit error: {result.stderr}")

print()
print("Step 3: Pushing to GitHub with embedded token...")
print("-" * 60)
print(f"Using URL: {GIT_URL}")
print()

# Use git push with the HTTPS URL (should accept token directly)
result = subprocess.run(
    ["git", "push", "-u", "origin", "master"],
    capture_output=True, text=True,
    env={**os.environ}
)

print(result.stdout if result.stdout else "")

if result.returncode == 0:
    print()
    print("=" * 60)
    print("🎉 SUCCESS! Pushed to GitHub!")
    print("=" * 60)
    print()
    print(f"Project URL: https://github.com/{USER_NAME}/{REPO_NAME}")
    print()
    print("Next steps:")
    print("1. Visit the URL above to view your project")
    print("2. Continue building Sonic Flux!")
else:
    print()
    print("=" * 60)
    print("❌ Push failed - retrying...")
    print("=" * 60)
    print(result.stderr[:1000])
