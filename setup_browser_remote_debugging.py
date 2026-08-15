"""
Setup Chrome Remote Debugging for Browser Exec
================================================
Run this once to initialize the browser for API documentation exploration.

This script will:
1. Launch Chrome with remote debugging on port 9222
2. Create a clean profile directory
3. Wait for connection establishment
4. Verify browser is accessible
"""

import subprocess
import os
import time
import sys

# Configuration
CHROME_PATH = r"C:\Users\taman\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"
REMOTE_DEBUG_PORT = 9222
PROFILE_DIR = r"C:\HermesWiiM\chrome_profile"

def create_profile_directory():
    """Create clean profile directory for remote debugging."""
    print("📌 Creating browser profile directory...")
    os.makedirs(PROFILE_DIR, exist_ok=True)
    print(f"   ✅ Profile directory created: {PROFILE_DIR}")

def launch_browser_with_remote_debugging():
    """Launch Chrome with remote debugging enabled."""
    print("\n🚀 Launching Chrome with remote debugging on port 9222...")
    
    cmd = [
        CHROME_PATH,
        f"--remote-debugging-port={REMOTE_DEBUG_PORT}",
        "--no-first-run",
        f"--user-data-dir={PROFILE_DIR}"
    ]
    
    print(f"   Command: {' '.join(cmd)}")
    
    # Launch browser in background
    process = subprocess.Popen(
        cmd,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print(f"   ✅ Chrome launched (PID: {process.pid})")
    print(f"   📍 Listening on: http://localhost:{REMOTE_DEBUG_PORT}")
    
    return process

def wait_for_browser_ready(timeout=30):
    """Wait for browser to accept connections."""
    print(f"\n⏳ Waiting {timeout} seconds for browser initialization...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Try to connect via curl
            result = subprocess.run(
                f"curl -s http://localhost:{REMOTE_DEBUG_PORT}/json/top-level",
                shell=True,
                capture_output=True,
                timeout=2
            )
            
            if result.returncode == 0:
                print("   ✅ Browser is accepting connections!")
                return True
        except Exception as e:
            pass
        
        time.sleep(2)
    
    print("⚠️  Timeout waiting for browser to be ready")
    return False

def verify_browser_connection():
    """Verify browser connection is working."""
    print("\n🔍 Verifying browser connection...")
    
    try:
        result = subprocess.run(
            f"curl -s http://localhost:{REMOTE_DEBUG_PORT}/json/version",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("   ✅ Connection verified!")
            print(f"\n   {result.stdout[:200]}...")
            return True
        else:
            print(f"   ❌ Connection failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Verification error: {e}")
        return False

def main():
    """Main setup workflow."""
    print("=" * 70)
    print("🎵 SONIC FLUX - BROWSER REMOTE DEBUGGING SETUP")
    print("=" * 70)
    
    # Step 1: Create profile directory
    create_profile_directory()
    
    # Step 2: Launch browser
    process = launch_browser_with_remote_debugging()
    
    # Step 3: Wait for ready
    if not wait_for_browser_ready(timeout=30):
        print("\n⚠️  Browser may not be fully initialized.")
        print("   Try launching it manually and check port 9222 in Chrome://inspect")
    
    # Step 4: Verify connection
    if verify_browser_connection():
        print("\n" + "=" * 70)
        print("✅ BROWSER SETUP COMPLETE!")
        print("=" * 70)
        print("\nYou can now use browser_exec commands.")
        print("The browser is running in the background with remote debugging enabled.")
        
        return True
    else:
        print("\n" + "=" * 70)
        print("⚠️  SETUP INCOMPLETE - MANUAL INTERVENTION MAY BE NEEDED")
        print("=" * 70)
        print("\nPlease try these steps:")
        print("1. Close any existing Chrome instances")
        print("2. Run the setup script again")
        print("3. Check that port 9222 is listening in Chrome://inspect")
        
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
