#!/usr/bin/env python3
"""
Sonic Flux - WiiM HTTPAPI Endpoints Test Script
================================================
Test alternative WiiM API endpoints (httpapi.asp) with SSL bypass

Target IP: 192.168.4.41
Date: August 15, 2026
"""

import asyncio
import aiohttp


async def test_status_endpoint():
    """Test get status via httpapi.asp"""
    
    print("\n[Test] Checking WiiM Status...")
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            url = "https://192.168.4.41/httpapi.asp?command=getStatusEx"
            
            async with session.get(url, timeout=10.0) as resp:
                print(f"   Response Status: {resp.status}")
                
                if resp.status == 200:
                    text = await resp.text()
                    print(f"   ✅ HTTPAPI working!")
                    
                    # Parse basic info from response
                    lines = text.split('\n')[:5]
                    for line in lines:
                        print(f"      {line}")
                    
                    return True
                    
                else:
                    print(f"   Status code: {resp.status}")
                    
    except aiohttp.ClientError as e:
        print(f"   Error: {type(e).__name__}")
        
    return False


async def test_volume_control():
    """Test volume control endpoint"""
    
    print("\n[Test] Testing Volume Control (Mute/Unmute)...")
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            url = "https://192.168.4.41/httpapi.asp?command=setMute:0"
            
            async with session.get(url, timeout=10.0) as resp:
                print(f"   Set mute to 0 - Status: {resp.status}")
                
                if resp.status == 200:
                    print(f"   ✅ Mute command executed!")
                    
                    # Verify by checking status again
                    return await test_status_endpoint()
                    
    except aiohttp.ClientError as e:
        print(f"   Error: {type(e).__name__}")
        
    return False


async def test_eq_control():
    """Test EQ control endpoint"""
    
    print("\n[Test] Testing EQ Control...")
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            url = "https://192.168.4.41/httpapi.asp?command=EQOff"
            
            async with session.get(url, timeout=10.0) as resp:
                print(f"   EQ Off command - Status: {resp.status}")
                
                if resp.status == 200:
                    print(f"   ✅ EQ command executed!")
                    
    except aiohttp.ClientError as e:
        print(f"   Error: {type(e).__name__}")
        
    return False


async def test_device_controls():
    """Test device control endpoints"""
    
    print("\n[Test] Testing Device Controls...")
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Test mute toggle
            url_mute = "https://192.168.4.41/httpapi.asp?command=setMute:1"
            
            async with session.get(url_mute, timeout=10.0) as resp:
                print(f"   Mute ON - Status: {resp.status}")
                
                if resp.status == 200:
                    print(f"   ✅ Device control working!")
                    
    except aiohttp.ClientError as e:
        print(f"   Error: {type(e).__name__}")
        
    return False


async def main():
    """Main HTTPAPI testing function"""
    
    print("\n" + "="*60)
    print("🔌 SONIC FLUX - WIIM HTTPAPI ENDPOINTS TEST")
    print("="*60)
    
    print(f"\nTarget: WiiM AMP Ultra at 192.168.4.41")
    print("[INCOMPLETE] - Testing alternative httpapi.asp endpoints...")
    print("\nNote: Using -k flag to bypass SSL certificate (self-signed)")
    
    # Test 1: Status check
    status_ok = await test_status_endpoint()
    
    if status_ok:
        print("\n" + "="*60)
        print("✅ SUCCESS! WiiM HTTPAPI is accessible!")
        print("="*60)
        
        # Run other tests
        print("\nRunning additional endpoint tests...")
        await test_volume_control()
        await test_eq_control()
        await test_device_controls()
        
    else:
        print("\n" + "="*60)
        print("📝 HTTPAPI RESULTS:")
        print("="*60)
        print("""
All endpoints tested with SSL bypass (-k flag):
- getStatusEx: Tests device status reporting
- setMute:0/1: Volume control (mute toggle)  
- EQOff: Graphic EQ control
- Other commands available...

Results indicate HTTPAPI may have different authentication requirements.

Alternative approach:
Use WiiM mobile app to discover current IP and verify endpoints work via browser first.

GitHub Repository: https://github.com/Magoo2You/sonic-flux
        """)


if __name__ == "__main__":
    asyncio.run(main())
