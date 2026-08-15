#!/usr/bin/env python3
"""
Sonic Flux - Safe Volume Setup Script
========================================
Sets WiiM Amp Ultra to safe volume level (20 or below) for playback testing

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Command: setPlayerCmd:vol:value
Safety Level: 20% maximum (or lower if desired)

This script ensures safe listening levels before any playback tests.
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


async def set_safe_volume(max_percent: int = 20):
    """Set volume to safe level for testing."""
    
    print("\n" + "=" * 70)
    print("🔇 SONIC FLUX - SAFE VOLUME SETUP")
    print("=" * 70)
    print(f"\nSetting WiiM Amp Ultra volume to {max_percent}% maximum (SAFETY FIRST!)")
    print("This ensures safe listening levels during playback testing.\n")
    
    status, content = await make_request(f"setPlayerCmd:vol:{max_percent}")
    
    if status == 200:
        print("✅ VOLUME SET SUCCESSFUL!")
        print(f"   Command: setPlayerCmd:vol:{max_percent}")
        print(f"   HTTP Status: {status}")
        print(f"   Response: {content.strip()}")
        print(f"\n🔇 Your WiiM is now at a safe listening level ({max_percent}%)")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def main():
    """Run safe volume setup."""
    await set_safe_volume(max_percent=20)  # Set to 20% for safety


if __name__ == "__main__":
    asyncio.run(main())
