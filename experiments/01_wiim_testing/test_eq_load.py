#!/usr/bin/env python3
"""
Sonic Flux - EQLoad Command Test
======================================================
Tests loading EQ presets from WiiM Amp Ultra

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Command: EQLoad:name (e.g., "Flat", "Bass Booster")
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


async def test_eq_load(name: str):
    """Test: EQLoad - Load named EQ preset"""
    
    print("\n" + "=" * 70)
    print(f"🎚️  TESTING: EQLoad:{name} Command")
    print("=" * 70)
    
    status, content = await make_request(f"EQLoad:{name}")
    
    print(f"\nCommand: EQLoad:{name}")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Preset loaded successfully")
        return "SUCCESS"
    else:
        print(f"❌ FAILED - HTTP {status}")
        return f"FAILED (HTTP {status})"


async def main():
    """Test EQLoad with Flat preset first."""
    
    print("\n" + "=" * 70)
    print("🧪 SONIC FLUX - WIIM HTTPAPI EQLoad TEST")
    print("=" * 70)
    print(f"\nTarget Device: WiiM Amp Ultra at 192.168.4.41")
    print("\nTesting EQ preset loading command.")
    print("Starting with 'Flat' preset (neutral, good for testing).")
    print("=" * 70)
    
    result = await test_eq_load("Flat")
    
    print("\n" + "=" * 70)
    print(f"✅ EQLoad TEST COMPLETED: {result}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
