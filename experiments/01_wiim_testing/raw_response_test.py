#!/usr/bin/env python3
"""
Sonic Flux - Raw Response Test: getStatusEx
=====================================================
Tests basic device status retrieval and shows RAW response content

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Command: getStatusEx
Expected: JSON response with device info
"""

import aiohttp
import asyncio
import json


async def get_device_status_raw(ip_address: str) -> tuple:
    """Get full device status via getStatusEx endpoint - returns raw response."""
    
    url = f"https://{ip_address}/httpapi.asp?command=getStatusEx"
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=15.0)) as session:
            async with session.get(url, timeout=10.0) as resp:
                
                print("=" * 70)
                print("📋 RAW RESPONSE TEST - getStatusEx")
                print("=" * 70)
                print(f"URL: {url}")
                print(f"HTTP Status Code: {resp.status}")
                print("-" * 70)
                
                # Get raw content first
                raw_content = await resp.text()
                print(f"\nRaw Response Content (first 200 chars):")
                print(raw_content[:200])
                
                if len(raw_content) > 200:
                    print("...")
                    print(raw_content[-100:])
                
                return resp.status, raw_content
                
    except Exception as e:
        print(f"\n✗ ERROR - {type(e).__name__}: {e}")
        return 0, str(e)


async def main():
    """Run getStatusEx test."""
    status, content = await get_device_status_raw("192.168.4.41")
    
    print("\n" + "=" * 70)
    if status == 200:
        print("✅ STATUS CODE: 200 (OK)")
        # Try to parse as JSON
        try:
            data = json.loads(content)
            print(f"\n📄 RESPONSE CONTENT ({len(content)} bytes):")
            print(json.dumps(data, indent=2)[:1500])  # Print first 1500 chars of JSON
        except json.JSONDecodeError as e:
            print(f"\n⚠️  Not valid JSON - raw response type check needed:")
            print(f"   Content type issue detected")
    else:
        print(f"❌ STATUS CODE: {status}")
