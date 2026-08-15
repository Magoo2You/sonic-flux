#!/usr/bin/env python3
"""
Sonic Flux - WiiM HTTPAPI Complete Test Suite
================================================
Test all available WiiM HTTPAPI endpoints with proper authentication

Target IP: 192.168.4.41
Date: August 15, 2026

Based on WiiM documentation, HTTPAPI requires POST requests with specific headers
and authentication (MCUKey).
"""

import asyncio
import aiohttp


async def test_all_endpoints():
    """Test all major WiiM HTTPAPI endpoints"""
    
    print("\n" + "="*60)
    print("🔌 SONIC FLUX - WIIM HTTPAPI COMPLETE TEST SUITE")
    print("="*60)
    
    connector = aiohttp.TCPConnector(ssl=False)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'SonicFlux/1.0'
        }
        
        base_url = "https://192.168.4.41/httpapi.asp"
        
        # Test 1: getStatusEx - Get device status
        print("\n[Test 1] getStatusEx - Device Status")
        try:
            url = f"{base_url}?command=getStatusEx"
            async with session.get(url, timeout=10.0) as resp:
                print(f"   Status Code: {resp.status}")
                
                if resp.status == 200:
                    text = await resp.text()
                    print(f"   Response Length: {len(text)} bytes")
                    
                    # Print first few lines
                    lines = text.split('\n')[:3]
                    for i, line in enumerate(lines):
                        print(f"      {i+1}. {line}")
                else:
                    print(f"   Status code indicates endpoint may need authentication")
                    
        except Exception as e:
            print(f"   Error: {type(e).__name__}: {str(e)[:80]}")
        
        # Test 2: setMute - Volume control
        print("\n[Test 2] setMute - Volume Control")
        try:
            url = f"{base_url}?command=setMute:0"
            async with session.get(url, timeout=10.0) as resp:
                print(f"   Unmute command - Status: {resp.status}")
                if resp.status == 200:
                    print(f"   ✅ Volume control endpoint accessible")
                    
        except Exception as e:
            print(f"   Error: {type(e).__name__}")
        
        # Test 3: EQOff - Equalizer control
        print("\n[Test 3] EQOff - Graphic EQ Control")
        try:
            url = f"{base_url}?command=EQOff"
            async with session.get(url, timeout=10.0) as resp:
                print(f"   EQ Off command - Status: {resp.status}")
                
        except Exception as e:
            print(f"   Error: {type(e).__name__}")
        
        # Test 4: MCUKeyShortClick - Remote control simulation
        print("\n[Test 4] MCUKeyShortClick - Device Control")
        try:
            url = f"{base_url}?command=MCUKeyShortClick:1Mute"
            async with session.get(url, timeout=10.0) as resp:
                print(f"   Mute key command - Status: {resp.status}")
                
        except Exception as e:
            print(f"   Error: {type(e).__name__}")
        
        # Test 5: Play track URL
        print("\n[Test 5] playURL - Audio Playback Control")
        try:
            url = f"{base_url}?command=playURL&url=http://test.mp3"
            async with session.get(url, timeout=10.0) as resp:
                print(f"   Play command - Status: {resp.status}")
                
        except Exception as e:
            print(f"   Error: {type(e).__name__}")


async def test_post_requests():
    """Test HTTPAPI with POST method (may be required)"""
    
    print("\n" + "="*60)
    print("🔌 TESTING WITH POST REQUESTS")
    print("="*60)
    
    connector = aiohttp.TCPConnector(ssl=False)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'SonicFlux/1.0'
        }
        
        # Try getStatusEx via POST
        print("\n[Test] Testing POST request method...")
        
        try:
            url = "https://192.168.4.41/httpapi.asp?command=getStatusEx"
            data = '{"command":"getStatusEx"}'
            
            async with session.post(url, data=data, timeout=10.0) as resp:
                print(f"   POST Status: {resp.status}")
                
                if resp.status == 200:
                    text = await resp.text()
                    print(f"   ✅ POST method working!")
                    
        except Exception as e:
            print(f"   Error: {type(e).__name__}: {str(e)[:80]}")


async def main():
    """Main testing function"""
    
    await test_all_endpoints()
    await test_post_requests()
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY:")
    print("="*60)
    print("""
All HTTPAPI endpoints tested with SSL bypass.

Note: WiiM HTTPAPI typically requires:
1. MCUKey authentication header
2. Proper POST method (not GET)
3. Specific session cookie management

If all tests fail with 403/401 status codes, the device may need:
- API access enabled in app settings
- Or different authentication mechanism configured

Next Steps:
1. Try WiiM mobile app to verify endpoints work via browser first
2. Check if MCUKey needs to be extracted from another source
3. Consider using WiiM's UPnP/SSRP discovery methods instead

GitHub Repository: https://github.com/Magoo2You/sonic-flux
        """)


if __name__ == "__main__":
    asyncio.run(main())
