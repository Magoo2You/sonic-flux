#!/usr/bin/env python3
"""
GitHub Repository Creator - Creates Sonic Flux repository and pushes local files
"""

import subprocess
import json

# Load token from .env file
with open(".env", "r") as f:
    for line in f:
        if line.startswith("GITHUB_TOKEN="):
            token = line.strip().split("=")[1]

github_username = "todd"  # Edit this with your actual GitHub username
repo_name = "sonic-flux"

print(f"Creating GitHub repository for user {github_username}...")
print(f"Repository name: {repo_name}")

# Create repository via API
url = f"https://api.github.com/user/repos"

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "HermesWiiM-Project-Setup"
}

# Execute curl command to create repo
cmd = f'curl -X POST "{url}" -H "Authorization: Bearer {token}" -H "Accept: application/vnd.github.v3+json" -d "{{\\"name\\\": \\"{repo_name}\\", \\"private\\\": true}}" --silent'

response = subprocess.run(cmd, shell=True, capture_output=True, text=True)

print(f"Response code: {response.returncode}")
print(f"Response: {response.stdout[:200]}")

if response.returncode == 0:
    print("✅ Repository created successfully!")
    
    # Get the clone URL from response
    data = json.loads(response.stdout)
    clone_url_https = f"https://{github_username}@github.com/{github_username}/{repo_name}.git"
    print(f"\nClone URL: {clone_url_https}")
    print(f"HTTPS: https://github.com/{github_username}/{repo_name}")
    
else:
    print("❌ Failed to create repository")
    print(f"Error: {response.stderr[:500]}")
    exit(1)
