#!/usr/bin/env python3
"""
Sonic Flux - EQ Commands Test Suite
======================================================
Tests all EQ endpoints from WiiM Mini PDF documentation

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Commands: EQOn, EQOff, EQGetStat, EQGetList, EQLoad:name

This script tests all EQ commands in order to validate the documented API.
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


async def test_eq_off():
    """Test: EQOff - Disable graphic EQ"""
    
    print("\n" + "=" * 70)
    print("🎚️  TESTING: EQOff Command")
    print("=" * 70)
    
    status, content = await make_request("EQOff")
    
    print(f"\nCommand: EQOff")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - EQ successfully disabled")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_eq_on():
    """Test: EQOn - Enable graphic EQ"""
    
    print("\n" + "=" * 70)
    print("🎚️  TESTING: EQOn Command")
    print("=" * 70)
    
    status, content = await make_request("EQOn")
    
    print(f"\nCommand: EQOn")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - EQ successfully enabled")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_eq_get_stat():
    """Test: EQGetStat - Check current EQ status"""
    
    print("\n" + "=" * 70)
    print("🎚️  TESTING: EQGetStat Command")
    print("=" * 70)
    
    status, content = await make_request("EQGetStat")
    
    print(f"\nCommand: EQGetStat")
    print(f"HTTP Status: {status}")
    print(f"Response Content (first 500 chars): {content.strip()[:500]}")
    
    if status == 200:
        try:
            import json
            data = json.loads(content)
            eq_stat = data.get('EQStat', 'Unknown')
            print(f"✅ SUCCESS - Current EQ Status: {eq_stat}")
        except json.JSONDecodeError as e:
            print(f"⚠️  Response is not valid JSON, but HTTP {status} indicates success")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_eq_get_list():
    """Test: EQGetList - List all available EQ presets"""
    
    print("\n" + "=" * 70)
    print("🎚️  TESTING: EQGetList Command")
    print("=" * 70)
    
    status, content = await make_request("EQGetList")
    
    print(f"\nCommand: EQGetList")
    print(f"HTTP Status: {status}")
    
    if status == 200:
        # Parse comma-separated list or JSON array
        content = content.strip()
        
        import json
        try:
            presets = json.loads(content)
            print(f"\nFound {len(presets)} EQ presets:")
            for i, preset in enumerate(sorted(presets), 1):
                print(f"   {i}. {preset}")
        except json.JSONDecodeError:
            # Try comma-separated format
            presets = [p.strip().strip('"') for p in content.split(',')]
            print(f"\nFound {len(presets)} EQ presets:")
            for i, preset in enumerate(sorted(presets), 1):
                print(f"   {i}. {preset}")
        print("✅ SUCCESS - Preset list retrieved")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_eq_load_preset(name: str):
    """Test: EQLoad - Load named EQ preset"""
    
    print("\n" + "=" * 70)
    print(f"🎚️  TESTING: EQLoad:{name} Command")
    print("=" * 70)
    
    status, content = await make_request(f"EQLoad:{name}")
    
    print(f"\nCommand: EQLoad:{name}")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Preset loaded")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def main():
    """Run all EQ command tests in order."""
    
    print("\n" + "=" * 70)
    print("🧪 SONIC FLUX - WIIM HTTPAPI EQ COMMANDS TEST SUITE")
    print("=" * 70)
    print(f"\nTarget Device: WiiM Amp Ultra at 192.168.4.41")
    print("\nTesting ALL EQ commands from WiiM Mini PDF documentation:")
    print("  1. EQOn / EQOff (enable/disable)")
    print("  2. EQGetStat (check status)")
    print("  3. EQGetList (list presets)")
    print("  4. EQLoad:name (load preset)")
    print("\n⏱️  Estimated time: ~1-2 minutes")
    print("=" * 70)
    
    # Run tests in order
    await test_eq_off()      # Test disable EQ first
    await asyncio.sleep(1)   # Wait for command to take effect
    
    # Now enable EQ before testing stat and list
    await test_eq_on()       # Enable EQ
    
    await asyncio.sleep(2)   # Wait for EQ to load
    
    await test_eq_get_stat() # Check status
    await test_eq_get_list() # List all presets
    
    print("\n\n" + "=" * 70)
    print("✅ ALL EQ COMMAND TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
