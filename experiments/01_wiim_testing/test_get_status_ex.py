#!/usr/bin/env python3
"""
Sonic Flux - Single Endpoint Test: getStatusEx
=====================================================
Tests basic device status retrieval from your WiiM Amp Ultra

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Command: getStatusEx
Expected: JSON response with device info (~3KB)
"""

import aiohttp
import asyncio
import json


async def get_device_status(ip_address: str) -> dict:
    """Get full device status via getStatusEx endpoint."""
    
    url = f"https://{ip_address}/httpapi.asp?command=getStatusEx"
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)  # SSL bypass for self-signed cert
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=15.0)) as session:
            async with session.get(url, timeout=10.0) as resp:
                if resp.status == 200:
                    status_data = await resp.json()
                    
                    # Print key device info
                    print("=" * 60)
                    print("📋 DEVICE STATUS SUCCESSFUL")
                    print("=" * 60)
                    print(f"Device Name: {status_data.get('ssid', 'Unknown')}")
                    print(f"Firmware Version: {status_data.get('firmware', 'Unknown')}")
                    print(f"Hardware Model: {status_data.get('hardware', 'Unknown')}")
                    print(f"Volume Control: {status_data.get('volume_control', 'Unknown')}")
                    print(f"WiFi Signal (RSSI): {status_data.get('RSSI', 'Unknown')} dBm")
                    print(f"Language: {status_data.get('language', 'Unknown')}")
                    
                    # Print connection info
                    if 'netstat' in status_data:
                        netstat = status_data['netstat']
                        if netstat == 2 or netstat == '2':
                            print(f"\n✓ Network Status: ONLINE (netstat=2)")
                    
                    print("=" * 60)
                    
                    return {
                        "status": "SUCCESS",
                        "http_status": resp.status,
                        "response_size": len(await resp.text()),
                        "device_info": status_data
                    }
                else:
                    print(f"✗ FAILED - HTTP {resp.status}")
                    return {"status": "FAILED", "http_status": resp.status}
                    
    except Exception as e:
        print(f"✗ ERROR - {type(e).__name__}: {e}")
        return {"status": "ERROR", "error": str(e)}


async def main():
    """Run getStatusEx test."""
    print("\n🧪 TESTING: Device Status Endpoint")
    print("=" * 70)
    print("Command: getStatusEx")
    print("URL: https://192.168.4.41/httpapi.asp?command=getStatusEx")
    print("-" * 70)
    
    result = await get_device_status("192.168.4.41")
    
    print("\n💾 RESULT:", result["status"])
    if result["status"] == "SUCCESS":
        print(f"   Response Size: {result['response_size']} bytes")


if __name__ == "__main__":
    asyncio.run(main())
