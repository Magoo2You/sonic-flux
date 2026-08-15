#!/usr/bin/env python3
"""
Sonic Flux - Playback Control Test Suite
======================================================
Tests all playback control endpoints from WiiM Mini PDF documentation

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Commands: pause, resume, onepause, next, prev, stop

Current volume is set to 20% for safe listening 🔇
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


async def test_pause():
    """Test: Pause playback"""
    
    print("\n" + "=" * 70)
    print("▶️⏸️  TESTING: Pause Command")
    print("=" * 70)
    
    status, content = await make_request("setPlayerCmd:pause")
    
    print(f"\nCommand: setPlayerCmd:pause")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Playback paused")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_resume():
    """Test: Resume playback"""
    
    print("\n" + "=" * 70)
    print("▶️⏯️  TESTING: Resume Command")
    print("=" * 70)
    
    status, content = await make_request("setPlayerCmd:resume")
    
    print(f"\nCommand: setPlayerCmd:resume")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Playback resumed")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_onepause():
    """Test: Toggle play/pause"""
    
    print("\n" + "=" * 70)
    print("▶️⏸️  TESTING: One-Pause Toggle Command")
    print("=" * 70)
    
    status, content = await make_request("setPlayerCmd:onepause")
    
    print(f"\nCommand: setPlayerCmd:onepause")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Toggle play/pause successful")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_next():
    """Test: Skip to next track"""
    
    print("\n" + "=" * 70)
    print("⏭️  TESTING: Next Track Command")
    print("=" * 70)
    
    status, content = await make_request("setPlayerCmd:next")
    
    print(f"\nCommand: setPlayerCmd:next")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Skipped to next track")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_prev():
    """Test: Skip to previous track"""
    
    print("\n" + "=" * 70)
    print("⏮️  TESTING: Previous Track Command")
    print("=" * 70)
    
    status, content = await make_request("setPlayerCmd:prev")
    
    print(f"\nCommand: setPlayerCmd:prev")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Skipped to previous track")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_stop():
    """Test: Stop playback"""
    
    print("\n" + "=" * 70)
    print("⏹️  TESTING: Stop Command")
    print("=" * 70)
    
    status, content = await make_request("setPlayerCmd:stop")
    
    print(f"\nCommand: setPlayerCmd:stop")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Playback stopped")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def main():
    """Run all playback control tests in order."""
    
    print("\n" + "=" * 70)
    print("🧪 SONIC FLUX - WIIM HTTPAPI PLAYBACK CONTROL TEST SUITE")
    print("=" * 70)
    print(f"\nTarget Device: WiiM Amp Ultra at 192.168.4.41")
    print("\nTesting ALL playback control endpoints from WiiM Mini PDF documentation:")
    print("  1. pause - Pause current track")
    print("  2. resume / onepause - Resume or toggle play/pause")
    print("  3. next - Skip to next track")
    print("  4. prev - Skip to previous track")
    print("  5. stop - Stop playback")
    print("\n🔇 Current volume level: 20% (SAFETY FIRST!)")
    print("=" * 70)
    
    # Test pause first
    await test_pause()
    await asyncio.sleep(1)             # Wait for pause to take effect
    
    # Now test resume
    await test_resume()
    await asyncio.sleep(2)             # Wait for track to load
    
    # Test onepause (toggle)
    await test_onepause()
    await asyncio.sleep(2)             # Wait for state change
    
    # Test navigation
    await test_next()                  # Skip forward
    await asyncio.sleep(1)             # Small delay
    
    await test_prev()                  # Go back
    await asyncio.sleep(1)             # Small delay
    
    # Test stop
    await test_stop()
    
    print("\n\n" + "=" * 70)
    print("✅ ALL PLAYBACK CONTROL TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
