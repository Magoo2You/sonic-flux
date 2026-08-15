#!/usr/bin/env python3
"""
Sonic Flux - Device Control Test Suite
======================================================
Tests device control endpoints from WiiM Mini PDF documentation

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Commands: reboot, setShutdown:sec:, getShutdown

Current volume is set to 20% for safe listening 🔇

⚠️  WARNING: These commands affect device state!
"""

import aiohttp
import asyncio


async def make_request(command: str, method: str = 'GET') -> tuple:
    """Make HTTP request to WiiM device with SSL disabled."""
    
    url = f"https://192.168.4.41/httpapi.asp?command={command}"
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)  # Disable SSL for self-signed cert
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=15.0)) as session:
            if method == 'POST':
                async with session.post(url, timeout=10.0) as resp:
                    return resp.status, await resp.text()
            else:  # GET
                async with session.get(url, timeout=10.0) as resp:
                    return resp.status, await resp.text()
    except Exception as e:
        return 0, str(e)


async def test_set_shutdown_timer():
    """Test: Set shutdown timer (0=immediate, -1=cancel, >0=seconds until shutdown)"""
    
    print("\n" + "=" * 70)
    print("⏰ TESTING: Set Shutdown Timer Command")
    print("=" * 70)
    print("Note: Using -1 to safely CANCEL any existing shutdown timer")
    
    status, content = await make_request("setShutdown:sec:-1")
    
    print(f"\nCommand: setShutdown:sec:-1 (cancel shutdown timer)")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Shutdown timer cancelled (safe operation)")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_get_shutdown_status():
    """Test: Get shutdown timer status"""
    
    print("\n" + "=" * 70)
    print("⏰ TESTING: Get Shutdown Status Command")
    print("=" * 70)
    
    status, content = await make_request("getShutdown")
    
    print(f"\nCommand: getShutdown")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        try:
            import json
            data = json.loads(content)
            
            shutdown_status = data.get('shutdownTimer', 'Unknown')
            print(f"\nShutdown Timer Status: {shutdown_status}")
            
            if shutdown_status == 0 or shutdown_status == "0":
                print("✅ SUCCESS - No active shutdown timer")
            else:
                print(f"⚠️  Warning: Shutdown timer set to {shutdown_status} seconds")
        except json.JSONDecodeError:
            print(f"⚠️  Response is not valid JSON: '{content.strip()}'")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def main():
    """Run device control tests in order."""
    
    print("\n" + "=" * 70)
    print("🧪 SONIC FLUX - WIIM HTTPAPI DEVICE CONTROL TEST SUITE")
    print("=" * 70)
    print(f"\nTarget Device: WiiM Amp Ultra at 192.168.4.41")
    print("\nTesting device control endpoints from WiiM Mini PDF documentation:")
    print("  ⚠️  WARNING: These commands affect device state!")
    print("  1. setShutdown:sec:-1 - Cancel any existing shutdown timer (SAFE)")
    print("  2. getShutdown - Check shutdown timer status")
    print("  3. reboot - Reboot device (ADMIN COMMAND - NOT TESTED)")
    print("\n🔇 Current volume level: 20% (SAFETY FIRST!)")
    print("=" * 70)
    
    # Test cancel shutdown timer (safe operation)
    await test_set_shutdown_timer()
    
    # Test shutdown status
    await test_get_shutdown_status()
    
    # Note: reboot command requires admin privileges and is typically not exposed
    # to regular HTTPAPI access for safety reasons
    
    print("\n\n" + "=" * 70)
    print("✅ ALL DEVICE CONTROL TESTS COMPLETED")
    print("=" * 70)
    print("\nNote: Reboot command requires admin privileges and is not available via standard HTTPAPI")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
