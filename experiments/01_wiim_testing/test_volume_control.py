#!/usr/bin/env python3
"""
Sonic Flux - Volume Control Test Suite
======================================================
Tests all volume control endpoints from WiiM Mini PDF documentation

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Commands: setPlayerCmd:vol:value, setPlayerCmd:volUp, setPlayerCmd:volDown
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


async def test_volume_absolute(value: int):
    """Test: Absolute volume setting (0-100)"""
    
    print(f"\n{'=' * 70}")
    print(f"🔊 TESTING: setPlayerCmd:vol:{value} Command")
    print("=" * 70)
    
    status, content = await make_request(f"setPlayerCmd:vol:{value}")
    
    print(f"\nCommand: setPlayerCmd:vol:{value}")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Volume set successfully")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_volume_up():
    """Test: Incremental volume up"""
    
    print("\n" + "=" * 70)
    print("🔊 TESTING: setPlayerCmd:volUp Command")
    print("=" * 70)
    
    status, content = await make_request("setPlayerCmd:volUp")
    
    print(f"\nCommand: setPlayerCmd:volUp")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Volume increased")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_volume_down():
    """Test: Incremental volume down"""
    
    print("\n" + "=" * 70)
    print("🔊 TESTING: setPlayerCmd:volDown Command")
    print("=" * 70)
    
    status, content = await make_request("setPlayerCmd:volDown")
    
    print(f"\nCommand: setPlayerCmd:volDown")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        print("✅ SUCCESS - Volume decreased")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_get_volume():
    """Test: Get current volume level"""
    
    print("\n" + "=" * 70)
    print("🔊 TESTING: getVolume Command (if documented)")
    print("=" * 70)
    
    try:
        status, content = await make_request("getVolume")
        
        print(f"\nCommand: getVolume")
        print(f"HTTP Status: {status}")
        print(f"Response Content: '{content.strip()}'")
        
        if status == 200:
            try:
                import json
                data = json.loads(content)
                volume_level = data.get('Volume', 'Unknown')
                print(f"✅ SUCCESS - Current Volume Level: {volume_level}%")
            except json.JSONDecodeError:
                print("⚠️  Response is not valid JSON")
        else:
            print(f"❌ FAILED - HTTP {status}")
            
    except Exception as e:
        print(f"\nCommand: getVolume (endpoint may not be documented)")
        print(f"Note: Endpoint may not exist in this device version")


async def main():
    """Run all volume control tests in order."""
    
    print("\n" + "=" * 70)
    print("🧪 SONIC FLUX - WIIM HTTPAPI VOLUME CONTROL TEST SUITE")
    print("=" * 70)
    print(f"\nTarget Device: WiiM Amp Ultra at 192.168.4.41")
    print("\nTesting ALL volume control endpoints from WiiM Mini PDF documentation:")
    print("  1. setPlayerCmd:vol:value (absolute volume 0-100)")
    print("  2. setPlayerCmd:volUp (incremental up)")
    print("  3. setPlayerCmd:volDown (incremental down)")
    print("=" * 70)
    
    # Test absolute volume at multiple levels
    await test_volume_absolute(0)      # Minimum volume
    await asyncio.sleep(1)             # Wait for command
    
    await test_volume_absolute(50)     # Medium volume
    await asyncio.sleep(1)             # Wait for command
    
    await test_volume_absolute(75)     # Higher volume
    await asyncio.sleep(1)             # Wait for command
    
    await test_volume_absolute(100)    # Maximum volume
    await asyncio.sleep(2)             # Wait for full change
    
    # Test incremental controls
    await test_volume_up()              # Volume up
    await asyncio.sleep(0.5)            # Small delay
    
    await test_volume_down()           # Volume down
    await asyncio.sleep(0.5)            # Small delay
    
    # Test get current volume
    await test_get_volume()


if __name__ == "__main__":
    asyncio.run(main())
