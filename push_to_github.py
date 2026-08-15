#!/usr/bin/env python3
"""
Push Sonic Flux project to GitHub using Personal Access Token
"""

import subprocess
import os

# Load configuration from .env
with open(".env", "r") as f:
    config = {}
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()

token = config.get("GITHUB_TOKEN", "")
repo_url_https = f"https://{config['GITHUB_USERNAME']}/sonic-flux"

print("Pushing Sonic Flux project to GitHub...")
print(f"Repository: {repo_url_https}")
print(f"Branch: master")
print()

# Configure Git to use token for authentication
os.environ["GIT_ASKPASS"] = "echo:"  # Suppress password prompt

# Create credentials helper script that uses the token
credentials_script = f'''
#!/bin/sh
if [ "$1" = "https://github.com/*" ]; then
    echo "{token}:x-oauth-basic"
fi
exit 0
'''

with open("git-creds.sh", "w") as f:
    f.write(credentials_script)

os.chmod("git-creds.sh", 0o755)

# Configure Git credential helper
subprocess.run(["git", "config", "--global", "credential.helper", ".git-creds"], check=True, shell=True)

print("✅ Credentials configured")
print()

# Add all files
subprocess.run(["git", "add", "."], check=True, shell=True)
print("✅ All files staged for commit")

# Commit changes
subprocess.run(["git", "commit", "-m", "Initial commit: Sonic Flux music discovery system"], check=True, shell=True)
print("✅ Committed all files")
print()

# Push to GitHub
print("Pushing to GitHub...")
result = subprocess.run(["git", "push", "-u", "origin", "master"], capture_output=True, text=True)

if result.returncode == 0:
    print("🎉 Successfully pushed to GitHub!")
    print()
    print(f"Project now available at:")
    print(f"https://github.com/{config['GITHUB_USERNAME']}/sonic-flux")
else:
    print("❌ Push failed:")
    print(result.stderr[:500])
