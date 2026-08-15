#!/usr/bin/env python3
"""
Final push attempt - embeds token directly in HTTPS URL
Uses store credential helper to save the auth
"""

import subprocess
import os
import sys

# Load token from .env file
with open(".env", "r") as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            if key.strip() == "GITHUB_TOKEN":
                TOKEN = value.strip()
                USER = os.environ.get('GITHUB_USERNAME', 'Magoo2You')
                REPO = 'sonic-flux'

print("=" * 60)
print("SONIC FLUX - PUSHING TO GITHUB")
print("=" * 60)
print()

# Step 1: Configure Git to use credential store helper
print("Step 1: Configuring credential storage...")
subprocess.run(["git", "config", "--global", "credential.helper", "store"], capture_output=True, check=True)
print("✅ Credential helper configured (credentials saved in plaintext)")
print()

# Step 2: Configure git to use the HTTPS URL with embedded token
print(f"Step 2: Configuring remote with authenticated URL...")
GIT_URL = f"https://{TOKEN}@github.com/{USER}/{REPO}.git"
print(f"Using URL: {GIT_URL}")
result = subprocess.run(
    ["git", "remote", "set-url", "origin", GIT_URL],
    capture_output=True, text=True, shell=False
)
if result.returncode == 0:
    print("✅ Remote URL configured")
else:
    print(f"Warning: {result.stderr}")
print()

# Step 3: Add all files
print("Step 3: Adding all files...")
result = subprocess.run(["git", "add", "."], capture_output=True, text=True)
if result.returncode == 0:
    print("✅ All files staged")
else:
    print(f"Error staging: {result.stderr[:200]}")
print()

# Step 4: Commit all files
print("Step 4: Committing all files...")
result = subprocess.run(
    ["git", "commit", "-m", "Initial commit: Sonic Flux - AI music discovery for WiiM"],
    capture_output=True, text=True
)
if result.returncode == 0:
    print(result.stdout if result.stdout else "")
    print("✅ Committed successfully")
else:
    print(f"Commit error: {result.stderr[:200]}")
print()

# Step 5: Push to GitHub
print("Step 5: Pushing to GitHub...")
print("-" * 60)

# Use git push with the HTTPS URL directly - should not prompt for password
result = subprocess.run(
    ["git", "push", "-u", "origin", "master"],
    capture_output=True, text=True
)

if result.returncode == 0:
    print(result.stdout if result.stdout else "")
    
    print()
    print("=" * 60)
    print("🎉 SUCCESS! Pushed to GitHub!")
    print("=" * 60)
    print()
    print(f"Project URL: https://github.com/{USER}/{REPO}")
    print()
    print("Next steps:")
    print("1. Open the URL above in your browser")
    print("2. Verify the project files are visible")
    print("3. Continue building Sonic Flux!")
    
else:
    print("Push failed. Full error output:")
    print(result.stderr)
    print()
    print("=" * 60)
    print("ALTERNATIVE: Try uploading via browser instead")
    print("=" * 60)
    print()
    print(f"1. Go to: https://github.com/{USER}/{REPO}")
    print("2. Click 'Import this repository' (or similar button)")
    print("3. Select C:\\HermesWiiM folder")
    print("4. Upload and verify")
