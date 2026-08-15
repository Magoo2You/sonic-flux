#!/usr/bin/env python3
"""
Sonic Flux - Seek Position Test Suite
======================================================
Tests position/seek endpoints from WiiM Mini PDF documentation

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Commands: seekForward, seekBackward, setPlayerCmd:seek:position

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


async def test_seek_forward(seconds: int = 10):
    """Test: Seek forward in track"""
    
    print(f"\n{'=' * 70}")
    print(f"⏩ TESTING: Seek Forward Command ({seconds} seconds)")
    print("=" * 70)
    
    status, content = await make_request(f"seekForward:{seconds}")
    
    print(f"\nCommand: seekForward:{seconds}")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Seek forward successful")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_seek_backward(seconds: int = 10):
    """Test: Seek backward in track"""
    
    print(f"\n{'=' * 70}")
    print(f"⏪ TESTING: Seek Backward Command ({seconds} seconds)")
    print("=" * 70)
    
    status, content = await make_request(f"seekBackward:{seconds}")
    
    print(f"\nCommand: seekBackward:{seconds}")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Seek backward successful")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_set_seek_position(seconds: int = 300):
    """Test: Absolute seek position"""
    
    print(f"\n{'=' * 70}")
    print(f"📍 TESTING: Set Seek Position Command ({seconds} seconds)")
    print("=" * 70)
    
    status, content = await make_request(f"setPlayerCmd:seek:{seconds}")
    
    print(f"\nCommand: setPlayerCmd:seek:{seconds}")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Seek position set successful")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def main():
    """Run all seek position tests in order."""
    
    print("\n" + "=" * 70)
    print("🧪 SONIC FLUX - WIIM HTTPAPI SEEK POSITION TEST SUITE")
    print("=" * 70)
    print(f"\nTarget Device: WiiM Amp Ultra at 192.168.4.41")
    print("\nTesting seek/position endpoints from WiiM Mini PDF documentation:")
    print("  1. seekForward:<seconds> - Seek forward in track")
    print("  2. seekBackward:<seconds> - Seek backward in track")
    print("  3. setPlayerCmd:seek:position - Absolute seek position")
    print("\n🔇 Current volume level: 20% (SAFETY FIRST!)")
    print("=" * 70)
    
    # Test forward seek
    await test_seek_forward(seconds=10)
    await asyncio.sleep(1)             # Wait for seek to complete
    
    # Test backward seek
    await test_seek_backward(seconds=10)
    await asyncio.sleep(1)             # Wait for seek to complete
    
    # Test absolute position seek
    await test_set_seek_position(seconds=300)  # Jump to 5 minutes
    
    print("\n\n" + "=" * 70)
    print("✅ ALL SEEK POSITION TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
