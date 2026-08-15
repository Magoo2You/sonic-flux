#!/usr/bin/env python3
"""
Push Sonic Flux to GitHub using credential store and token authentication
"""

import subprocess
import os

print("=" * 60)
print("SONIC FLUX - PUSHING TO GITHUB")
print("=" * 60)
print()

# Load configuration from .env
with open(".env", "r") as f:
    config = {}
    for line in f:
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()

print(f"User: {config['GITHUB_USERNAME']}")
print(f"Repository: sonic-flux")
print()

# Step 1: Configure Git to use credential store
print("Step 1: Configuring Git credential storage...")
subprocess.run(["git", "config", "--global", "credential.helper", "manager-core"], shell=True, check=True)
print("✅ Credential helper configured")
print()

# Step 2: Add all files and commit
print("Step 2: Staging and committing all files...")
result = subprocess.run(["git", "add", "."], capture_output=True, text=True)
if result.returncode == 0:
    print("✅ Files staged")
    
    result = subprocess.run(
        ["git", "commit", "-m", "Initial commit: Sonic Flux music discovery system"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(result.stdout)
        print("✅ Commit successful!")
    else:
        print(f"Commit error: {result.stderr}")
else:
    print(f"Stage error: {result.stderr}")

print()
print("Step 3: Pushing to GitHub...")
print("-" * 60)
print()

# Method 1: Try git push with credential manager (should prompt and accept token)
print("Attempting git push with credential manager...")
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
    print(f"Project URL: https://github.com/Magoo2You/sonic-flux")
else:
    print("Push attempt failed. Output:")
    print(result.stderr[:500])
    print()
    
    # Method 2: Alternative - use GitHub CLI if available
    print("Step 4: Checking for gh (GitHub CLI)...")
    result = subprocess.run(["which", "gh"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Found GitHub CLI! Attempting to use it...")
        
        # Login with token
        print("Step 4a: Authenticating with GitHub CLI...")
        subprocess.run(["gh", "auth", "login", "--with-token"], capture_output=True)
        
        # Try push with gh CLI
        result = subprocess.run(["gh", "repo", "create", "sonic-flux", "--private", "--source=.", "-d", "AI-powered music discovery system"], capture_output=True, text=True)
        print(result.stdout if result.stdout else "")
        
        if result.returncode == 0:
            print("✅ Created repository with gh CLI!")
            # Push to created repo
            subprocess.run(["gh", "repo", "set-defaultbranch", "main"], capture_output=True)
            subprocess.run(["git", "remote", "add", "origin", "https://github.com/Magoo2You/sonic-flux.git"], capture_output=True, shell=True)
            
            result = subprocess.run(["gh", "repo", "view", "sonic-flux", "--json=url"], capture_output=True, text=True)
            import json
            data = json.loads(result.stdout)
            repo_url = data.get("url")
            print(f"Repository: {repo_url}")
    else:
        print("GitHub CLI not found. Please try manual push or check error above.")

print()
print("=" * 60)
print("Project Summary:")
print("=" * 60)
print()
print("Local files created:")
for root, dirs, files in os.walk("."):
    for file in files:
        filepath = os.path.join(root, file)
        if not os.path.isdir(filepath):
            print(f"  - {filepath}")

print()
print("Next steps:")
print("1. Check if push succeeded above")
print("2. If failed, you can manually push using the terminal:")
print("   git push -u origin master")
print("3. Or use GitHub CLI: gh repo create sonic-flux --private --source=.")
