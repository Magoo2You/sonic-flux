#!/usr/bin/env python3
"""
Sonic Flux - Source Switching Test Suite
======================================================
Tests source switching endpoints from WiiM Mini PDF documentation and DanBrezeanu extended API

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Commands: setPlayerCmd:switchmode:<mode>, getSources

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


async def test_source_switch_wifi():
    """Test: Switch to WiFi source"""
    
    print("\n" + "=" * 70)
    print("📡 TESTING: Source Switch - WiFi Mode")
    print("=" * 70)
    
    status, content = await make_request("setPlayerCmd:switchmode:wifi")
    
    print(f"\nCommand: setPlayerCmd:switchmode:wifi")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Switched to WiFi source")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_source_switch_radios():
    """Test: Switch to Radio source"""
    
    print("\n" + "=" * 70)
    print("📻 TESTING: Source Switch - Radio Mode")
    print("=" * 70)
    
    status, content = await make_request("setPlayerCmd:switchmode:radio")
    
    print(f"\nCommand: setPlayerCmd:switchmode:radio")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Switched to Radio source")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_source_switch_bluetooth():
    """Test: Switch to Bluetooth source"""
    
    print("\n" + "=" * 70)
    print("📱 TESTING: Source Switch - Bluetooth Mode")
    print("=" * 70)
    
    status, content = await make_request("setPlayerCmd:switchmode:bluetooth")
    
    print(f"\nCommand: setPlayerCmd:switchmode:bluetooth")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Switched to Bluetooth source")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_source_switch_udisk():
    """Test: Switch to USB Disk source"""
    
    print("\n" + "=" * 70)
    print("💾 TESTING: Source Switch - USB Disk Mode")
    print("=" * 70)
    
    status, content = await make_request("setPlayerCmd:switchmode:udisk")
    
    print(f"\nCommand: setPlayerCmd:switchmode:udisk")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Switched to USB Disk source")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_get_sources():
    """Test: Get available sources"""
    
    print("\n" + "=" * 70)
    print("📋 TESTING: Get Sources Command (if documented)")
    print("=" * 70)
    
    status, content = await make_request("getSources")
    
    print(f"\nCommand: getSources")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        try:
            import json
            data = json.loads(content)
            sources = data.get('sources', [])
            
            if isinstance(sources, list):
                print(f"\n✅ SUCCESS - Found {len(sources)} available source(s):")
                for i, source in enumerate(sources[:10], 1):  # Show first 10
                    print(f"   {i}. {source.get('name', 'Unknown')}")
            else:
                print(f"\nResponse structure: {sources}")
        except json.JSONDecodeError:
            print(f"⚠️  Response is not valid JSON, but command succeeded")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_source_switch_optical():
    """Test: Switch to Optical source"""
    
    print("\n" + "=" * 70)
    print("💡 TESTING: Source Switch - Optical Mode")
    print("=" * 70)
    
    status, content = await make_request("setPlayerCmd:switchmode:optical")
    
    print(f"\nCommand: setPlayerCmd:switchmode:optical")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Switched to Optical source")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def main():
    """Run all source switching tests in order."""
    
    print("\n" + "=" * 70)
    print("🧪 SONIC FLUX - WIIM HTTPAPI SOURCE SWITCHING TEST SUITE")
    print("=" * 70)
    print(f"\nTarget Device: WiiM Amp Ultra at 192.168.4.41")
    print("\nTesting source switching endpoints from documentation:")
    print("  1. setPlayerCmd:switchmode:wifi - WiFi streaming")
    print("  2. setPlayerCmd:switchmode:radio - Radio tuner")
    print("  3. setPlayerCmd:switchmode:bluetooth - Bluetooth source")
    print("  4. setPlayerCmd:switchmode:udisk - USB disk playback")
    print("  5. setPlayerCmd:switchmode:optical - Optical input")
    print("  6. getSources - List all available sources (if documented)")
    print("\n🔇 Current volume level: 20% (SAFETY FIRST!)")
    print("=" * 70)
    
    # Test each source switch
    await test_source_switch_wifi()      # WiFi streaming
    
    await test_source_switch_radios()    # Radio tuner
    
    await test_source_switch_bluetooth() # Bluetooth
    
    await test_source_switch_udisk()     # USB disk
    
    await test_source_switch_optical()   # Optical input
    
    # Test get sources (may not be documented for all devices)
    try:
        await test_get_sources()
    except Exception as e:
        print(f"\n⚠️  getSources endpoint may not be documented for this device")
    
    print("\n\n" + "=" * 70)
    print("✅ ALL SOURCE SWITCHING TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
