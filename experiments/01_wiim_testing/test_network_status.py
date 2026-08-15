#!/usr/bin/env python3
"""
Sonic Flux - Network Status Test Suite
======================================================
Tests network status endpoints from WiiM Mini PDF documentation

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Commands: wlanGetConnectState, wifiConnectState, bluetoothConnectState

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


async def test_wlan_get_connect_state():
    """Test: wlanGetConnectState - WiFi connection status"""
    
    print("\n" + "=" * 70)
    print("📶 TESTING: wlanGetConnectState Command")
    print("=" * 70)
    
    status, content = await make_request("wlanGetConnectState")
    
    print(f"\nCommand: wlanGetConnectState")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    # Parse connection state (non-JSON response)
    if status == 200:
        state = content.strip()
        print(f"\nConnection State: {state}")
        
        if state.upper() in ["OK", "FAIL", "PROCESS", "PAIRFAIL"]:
            print("✅ SUCCESS - Network status retrieved successfully")
        else:
            print(f"⚠️  Unknown response format: {state}")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_wifi_connect_state():
    """Test: wifiConnectState - Alternative WiFi check"""
    
    print("\n" + "=" * 70)
    print("📶 TESTING: wifiConnectState Command (if documented)")
    print("=" * 70)
    
    status, content = await make_request("wifiConnectState")
    
    print(f"\nCommand: wifiConnectState")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        try:
            import json
            data = json.loads(content)
            print(f"✅ SUCCESS - Response parsed: {data.get('ssid', 'N/A')}")
        except json.JSONDecodeError:
            print(f"⚠️  Response is not valid JSON: '{content.strip()}'")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def test_bluetooth_connect_state():
    """Test: bluetoothConnectState - Bluetooth connection status"""
    
    print("\n" + "=" * 70)
    print("📱 TESTING: bluetoothConnectState Command (if documented)")
    print("=" * 70)
    
    status, content = await make_request("bluetoothConnectState")
    
    print(f"\nCommand: bluetoothConnectState")
    print(f"HTTP Status: {status}")
    print(f"Response Content: '{content.strip()}'")
    
    if status == 200:
        try:
            import json
            data = json.loads(content)
            
            bt_status = data.get('btConnectState', 'Unknown')
            mac = data.get('BTMAC', 'N/A')
            
            print(f"✅ SUCCESS - Bluetooth connection status retrieved")
            print(f"   Connection State: {bt_status}")
            print(f"   BT MAC Address: {mac}")
        except json.JSONDecodeError:
            print(f"⚠️  Response is not valid JSON: '{content.strip()}'")
    else:
        print(f"❌ FAILED - HTTP {status}")


async def main():
    """Run all network status tests in order."""
    
    print("\n" + "=" * 70)
    print("🧪 SONIC FLUX - WIIM HTTPAPI NETWORK STATUS TEST SUITE")
    print("=" * 70)
    print(f"\nTarget Device: WiiM Amp Ultra at 192.168.4.41")
    print("\nTesting network status endpoints from WiiM Mini PDF documentation:")
    print("  1. wlanGetConnectState - WiFi connection status")
    print("  2. wifiConnectState - Alternative WiFi check (if available)")
    print("  3. bluetoothConnectState - Bluetooth connection status (if available)")
    print("\n🔇 Current volume level: 20% (SAFETY FIRST!)")
    print("=" * 70)
    
    # Test WiFi connection state
    await test_wlan_get_connect_state()
    
    # Test alternative WiFi check (may not exist on all devices)
    try:
        await test_wifi_connect_state()
    except Exception as e:
        print(f"\n⚠️  wifiConnectState endpoint may not be documented for this device")
    
    # Test Bluetooth connection state (may not exist on all devices)
    try:
        await test_bluetooth_connect_state()
    except Exception as e:
        print(f"\n⚠️  bluetoothConnectState endpoint may not be documented for this device")
    
    print("\n\n" + "=" * 70)
    print("✅ ALL NETWORK STATUS TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
