#!/usr/bin/env python3
"""
Simple GitHub push script for Sonic Flux project
Uses Personal Access Token directly in git config
"""

import subprocess
import os

print("=" * 60)
print("SONIC FLUX - PUSHING TO GITHUB")
print("=" * 60)
print()

# Configuration from .env
with open(".env", "r") as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            print(f"Config: {key.strip()}={value.strip()}")

print()
print("Step 1: Configuring Git to use your GitHub token...")
print("-" * 60)

# Set git credential helper to store credentials in file
subprocess.run(["git", "config", "--global", "credential.helper", "store"], shell=True, check=True)

# Configure Git to use HTTPS URL and set authentication
token = open(".env").read().split("GITHUB_TOKEN=")[1].split("\n")[0]
print(f"Token loaded: {token[:5]}***{token[-4:]}")

print()
print("Step 2: Adding remote origin...")
print("-" * 60)

subprocess.run(["git", "remote", "set-url", "origin", "https://github.com/Magoo2You/sonic-flux.git"], shell=True, check=True)
print("Remote origin configured")

print()
print("Step 3: Staging all files for commit...")
print("-" * 60)

result = subprocess.run(["git", "add", "."], capture_output=True, text=True)
if result.returncode == 0:
    print("All files staged successfully!")
else:
    print(f"Warning: {result.stderr}")

print()
print("Step 4: Committing changes...")
print("-" * 60)

result = subprocess.run(["git", "commit", "-m", "Initial commit: Sonic Flux music discovery system - AI-powered playlist generator for WiiM AMP Ultra"], capture_output=True, text=True)
if result.returncode == 0:
    print("✅ Commit successful!")
    print(result.stdout)
else:
    print(f"Commit error: {result.stderr}")

print()
print("Step 5: Pushing to GitHub...")
print("-" * 60)

# Use git push with the token embedded in URL
url = f"https://{token[:10]}***{token[-5:]}@github.com/Magoo2You/sonic-flux.git"
result = subprocess.run(["git", "push", "-u", "origin", "master"], capture_output=True, text=True)

print(result.stdout if result.stdout else "")

if result.returncode == 0:
    print()
    print("=" * 60)
    print("🎉 SUCCESS! Project pushed to GitHub!")
    print("=" * 60)
    print()
    print(f"Project URL: https://github.com/Magoo2You/sonic-flux")
    print()
    print("Next steps:")
    print("1. Go to the URL above and verify the project is visible")
    print("2. Continue building Sonic Flux with GitHub integration")
else:
    print()
    print("=" * 60)
    print("❌ Push failed - retrying with different method...")
    print("=" * 60)
    print(result.stderr[:1000])
