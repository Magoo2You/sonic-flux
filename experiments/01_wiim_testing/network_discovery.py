#!/usr/bin/env python3
"""
Sonic Flux - Wiim Network Discovery Script
============================================
Automatically discover and test WiiM devices on the network

Target IP (provided): 192.168.4.41
Date: August 15, 2026
"""

import asyncio
import aiohttp


async def test_https_endpoint():
    """Test HTTPS endpoint (common for Wiim devices)"""
    
    print("\n[Test] Testing HTTPS endpoint...")
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {'Accept': 'application/json', 'User-Agent': 'SonicFlux/1.0'}
            
            # Try HTTPS first (Wiim typically uses HTTPS)
            async with session.get("https://192.168.4.41/status", headers=headers, timeout=10.0) as resp:
                print(f"   HTTP Status: {resp.status}")
                
                if resp.status == 200:
                    status = await resp.json()
                    print(f"✅ HTTPS API working!")
                    
                    now_playing = status.get('nowPlaying', {})
                    if now_playing:
                        print(f"   Current source: {now_playing.get('sourceType', 'Unknown')}")
                        print(f"   Track title: {now_playing.get('title', 'N/A')}")
                        print(f"   Artist: {now_playing.get('artist', 'N/A')}")
                    return True
                    
    except aiohttp.ClientError as e:
        print(f"   HTTPS failed: {type(e).__name__}")
        
    return False


async def test_http_endpoint():
    """Test HTTP endpoint (fallback if HTTPS fails)"""
    
    print("\n[Test] Testing HTTP endpoint...")
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {'Accept': 'application/json', 'User-Agent': 'SonicFlux/1.0'}
            
            async with session.get("http://192.168.4.41/status", headers=headers, timeout=10.0) as resp:
                print(f"   HTTP Status: {resp.status}")
                
                if resp.status == 200:
                    status = await resp.json()
                    print(f"✅ HTTP API working!")
                    
                    now_playing = status.get('nowPlaying', {})
                    if now_playing:
                        print(f"   Current source: {now_playing.get('sourceType', 'Unknown')}")
                        
                    return True
                    
    except aiohttp.ClientError as e:
        print(f"   HTTP failed: {type(e).__name__}")
        
    return False


async def main():
    """Main discovery and testing function"""
    
    print("\n" + "="*60)
    print("🔍 SONIC FLUX - WIIM NETWORK DISCOVERY & TESTING")
    print("="*60)
    
    print(f"\nTarget IP: 192.168.4.41")
    print(f"[INCOMPLETE] - Testing network connectivity...")
    
    # Test HTTPS first (most common for Wiim)
    https_ok = await test_https_endpoint()
    
    if https_ok:
        print("\n✅ SUCCESS! Wiim is accessible via HTTPS!")
        
    # If HTTPS failed, try HTTP
    else:
        http_ok = await test_http_endpoint()
        
        if http_ok:
            print("\n✅ SUCCESS! Wiim is accessible via HTTP!")
        else:
            print("\n" + "="*60)
            print("📝 HARDWARE ACCESS STATUS:")
            print("="*60)
            print("""
Connection refused - possible causes:

1. ❌ Wiim might be on different subnet
   - Check both devices are on same WiFi network
   
2. ⚠️  Firewall blocking connection
   - Temporarily disable Windows firewall to test
   
3. 🔒 HTTPS certificate issue
   - Try installing root CA or use --insecure-ssl flag
   
4. 📱 WiiM app API configuration needed
   - Open WiiM app → Settings → Advanced
   - Enable "API Access" 
   
5. 💻 Different port configured
   - Check WiiM app for custom port settings

Next Steps:
1. Verify both PC and Wiim on same WiFi network (192.168.4.x)
2. Configure API access in WiiM mobile app
3. Try alternative discovery methods

GitHub Repository: https://github.com/Magoo2You/sonic-flux
            """)


if __name__ == "__main__":
    asyncio.run(main())
