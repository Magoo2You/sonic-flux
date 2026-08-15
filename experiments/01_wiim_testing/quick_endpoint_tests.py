#!/usr/bin/env python3
"""
Sonic Flux - Simplified Wiim HTTPAPI Endpoint Tests
====================================================
Quick validation of all endpoints from your Mini PDF documentation
"""

import aiohttp
import asyncio
import json


async def make_request(command: str, method: str = 'GET') -> tuple:
    """Make HTTP request to WiiM device."""
    ip = "192.168.4.41"
    url = f"https://{ip}/httpapi.asp?command={command}"
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=15.0)) as session:
            if method == 'POST':
                async with session.post(url, timeout=10.0) as resp:
                    return resp.status, await resp.text()
            else:
                async with session.get(url, timeout=10.0) as resp:
                    return resp.status, await resp.text()
    except Exception as e:
        return 0, str(e)


async def main():
    """Run simplified endpoint tests."""
    
    print("=" * 70)
    print("🧪 SONIC FLUX - WIIM HTTPAPI ENDPOINT VALIDATION")
    print("=" * 70)
    print(f"\nTarget: WiiM Amp Ultra at 192.168.4.41")
    print("\nTesting ALL endpoints documented in your WiiM Mini PDF\n")
    print("-" * 70)
    
    results = []
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: getStatusEx
    print("📋 [1/12] Testing Device Status (getStatusEx)...")
    status, content = await make_request("getStatusEx")
    if status == 200:
        data = json.loads(content)
        print(f"   ✓ PASS - HTTP {status} | Device: {data.get('ssid', 'Unknown')} | Firmware: {data.get('firmware', 'Unknown')}")
        tests_passed += 1
    else:
        print(f"   ✗ FAIL - HTTP {status}")
        tests_failed += 1
    results.append(f"[getStatusEx] HTTP {status} - Device: {json.loads(content).get('ssid') if status == 200 else 'Unknown'}")
