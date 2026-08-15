#!/usr/bin/env python3
"""
Sonic Flux - Wiim Connection Troubleshooting Script
=====================================================
Diagnose common connection issues and provide solutions

Target IP: 192.168.4.41
Date: August 15, 2026
"""

import asyncio
import aiohttp
from pathlib import Path


async def test_with_insecure_ssl():
    """Test with SSL verification disabled (for self-signed certificates)"""
    
    print("\n[Test] Testing with insecure SSL flag...")
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            headers = {'Accept': 'application/json', 'User-Agent': 'SonicFlux/1.0'}
            
            async with session.get("https://192.168.4.41/status", headers=headers, timeout=10.0) as resp:
                print(f"   Status: {resp.status}")
                
                if resp.status == 200:
                    status = await resp.json()
                    
                    now_playing = status.get('nowPlaying', {})
                    if now_playing:
                        print(f"✅ SUCCESS!")
                        print(f"   Source: {now_playing.get('sourceType', 'Unknown')}")
                        print(f"   Title: {now_playing.get('title', 'N/A')}")
                        return True
                        
    except aiohttp.ClientError as e:
        print(f"   Still failed ({type(e).__name__}): {str(e)[:100]}...")
        
    return False


async def test_raw_socket():
    """Test raw TCP socket connection to verify basic network reachability"""
    
    print("\n[Test] Testing raw TCP socket connection...")
    
    try:
        import socket
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        
        result = sock.connect_ex(('192.168.4.41', 5000))  # Port 5000 is default HTTP
        print(f"   TCP Connection to port 5000: {'SUCCESS' if result == 0 else 'FAILED'}")
        
        if result == 0:
            sock.close()
            return True
            
    except Exception as e:
        print(f"   Raw socket failed: {e}")
        
    return False


async def check_subnet():
    """Check what subnet the PC is on"""
    
    print("\n[Test] Checking local network configuration...")
    
    try:
        import socket
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        
        print(f"   PC IP address: {ip_address}")
        
        # Try to resolve WiiM IP
        try:
            resolved = socket.gethostbyname('192.168.4.41')
            print(f"   WiiM resolves to: 192.168.4.41 (same subnet expected)")
            
        except socket.gaierror:
            print(f"   WiiM IP does not resolve")
            
    except Exception as e:
        print(f"   Network check failed: {e}")


async def main():
    """Main troubleshooting function"""
    
    print("\n" + "="*60)
    print("🔧 SONIC FLUX - WIIM CONNECTION TROUBLESHOOTING")
    print("="*60)
    
    print(f"\nTarget: WiiM AMP Ultra at 192.168.4.41")
    print("[INCOMPLETE] - Diagnosing connection issues...")
    
    # Check basic network configuration
    await check_subnet()
    
    # Test raw TCP connectivity first (bypasses SSL)
    tcp_ok = await test_raw_socket()
    
    if tcp_ok:
        print("\n✅ Raw TCP works! Issue is likely SSL certificate.")
        
        # Try with insecure SSL
        https_insecure_ok = await test_with_insecure_ssl()
        
        if https_insecure_ok:
            print("\n✅ Wiim is now accessible!")
            
    else:
        print("\n⚠️  Raw TCP connection failed")
        print("""

Possible causes:
1. ❌ Firewalls blocking port 5000/443
2. ❌ WiiM on different subnet (not same WiFi)
3. ❌ Wiim API not enabled in app settings
4. ❌ Wiim service not running

Troubleshooting steps:

A. Check Windows Firewall:
   - Open Windows Defender Firewall
   - Allow incoming connections for port 5000 or 443
   
B. Verify WiFi network:
   - PC and WiiM must be on same SSID/subnet
   
C. Enable API in WiiM app:
   - Open WiiM mobile app
   - Settings → Advanced → Enable API Access
   
D. Check port configuration:
   - In WiiM app, check if custom port is configured

E. Try using Wiim discovery:
   pip install pywiim[discover]
   python -c "from pywiim import discover_devices; devices = await discover_devices(); print(devices)"

GitHub Repository: https://github.com/Magoo2You/sonic-flux
        """)


if __name__ == "__main__":
    asyncio.run(main())
