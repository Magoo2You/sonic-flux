#!/usr/bin/env python3
"""
GitHub Repository Creator - Creates Sonic Flux repository and pushes local files
"""

import os
import subprocess
import sys

def create_github_repo(token, username):
    """Create new GitHub repository via API"""
    
    # Replace these with your actual values
    github_token = token  # "ghp_***"
    github_username = username  # Your GitHub username (e.g., "todd")
    
    repo_name = "sonic-flux"
    
    # Create repository endpoint
    url = f"https://api.github.com/user/repos"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "HermesWiiM-Project-Setup"
    }
    
    # Create repository
    response = subprocess.run(
        ["curl", "-X", "POST", url],
        headers=headers,
        json={
            "name": repo_name,
            "private": True  # Keep it private for security
        },
        capture_output=True,
        text=True
    )
    
    print(f"Repository creation status: {response.returncode}")
    
    if response.returncode == 0:
        import json
        data = json.loads(response.stdout)
        repo_url = f"https://{github_username}@github.com/{github_username}/{repo_name}.git"
        
        return repo_url
    
    print(f"Error creating repository: {response.stderr}")
    return None

def setup_git_remote(repo_url):
    """Add GitHub remote to local repository"""
    
    subprocess.run([
        "git", "remote", "add", "origin", repo_url,
        "-o", "url", "ssh://git@github.com"  # Convert HTTPS to SSH (will need SSH key setup)
    ], shell=True)
    
    return True

def push_to_github():
    """Push local files to GitHub"""
    
    subprocess.run(["git", "add", "."], shell=True, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit: Sonic Flux music discovery system"], shell=True, check=True)
    subprocess.run(["git", "push", "-u", "origin", "master"], shell=True)

if __name__ == "__main__":
    # Load token from .env file
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GITHUB_TOKEN="):
                token = line.split("=")[1].strip()
    
    # Replace with your actual username - edit this!
    username = "todd"  # CHANGE THIS TO YOUR ACTUAL GITHUB USERNAME
    
    print(f"Creating GitHub repository for user: {username}")
    
    repo_url = create_github_repo(token, username)
    
    if repo_url:
        print(f"\n✅ Repository created!")
        print(f"Repository URL: {repo_url}")
        
        # Setup remote
        setup_git_remote(repo_url)
        print("\n✅ Remote added successfully!")
        
        # Push to GitHub
        push_to_github()
        print("\n🎉 Successfully pushed all files to GitHub!")
        
        print("\n=== Project now available at:")
        print(f"https://github.com/{username}/sonic-flux")
    else:
        print("❌ Failed to create repository. Please check token and try again.")
