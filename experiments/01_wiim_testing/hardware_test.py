#!/usr/bin/env python3
"""
Sonic Flux - WiiM Hardware Test Script
=========================================
Test script to verify Wiim AMP Ultra connectivity and basic commands

Target IP: 192.168.4.41
Date: August 15, 2026

[INCOMPLETE] - Needs pywiim installation and your credentials configured
"""

import asyncio
from pywiim import WiiMClient


async def test_wiim_connectivity():
    """Test basic Wiim connectivity to 192.168.4.41"""
    
    print("\n" + "="*60)
    print("🔌 SONIC FLUX - WIIM HARDWARE TEST")
    print("="*60)
    print("\n[INCOMPLETE] - Running hardware connectivity test...")
    print(f"\nTarget: WiiM AMP Ultra at 192.168.4.41")
    
    try:
        # Create client with IP and attempt connection
        client = WiiMClient("192.168.4.41")
        
        print(f"\n✅ Created client for 192.168.4.41")
        
        # Try to get device info (this tests basic connectivity)
        try:
            info = await client.get_device_info()
            print(f"   Model: {info.model_name}")
            print(f"   Status: Online" if info.is_online else "   Status: Offline")
            
            return client
            
        except Exception as e:
            print(f"   ⚠️  Device info fetch failed: {e}")
            print("   [INCOMPLETE] - This may require:")
            print("      1. Configuring admin credentials in WiiM app settings")
            print("      2. Checking firewall allows port 5000/443")
            return client
        
    except Exception as e:
        print(f"\n⚠️  Connection test result:")
        print(f"   Error: {e}")
        print(f"   [INCOMPLETE] - This may require:")
        print("      1. Configuring admin credentials in WiiM app settings")
        print("      2. Checking firewall allows port 5000/443")
        return None


async def test_direct_http():
    """Test direct HTTP API connection as alternative method"""
    
    print("\n[TEST] Testing direct HTTP API connection...")
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # Try HTTP (non-SSL) first
            headers = {'Accept': 'application/json'}
            
            try:
                async with session.get("http://192.168.4.41/status", headers=headers, timeout=5.0) as resp:
                    if resp.status == 200:
                        status = await resp.json()
                        print(f"✅ HTTP API working!")
                        print(f"   Source: {status.get('nowPlaying', {}).get('sourceType', 'Unknown')}")
                        return True
                        
            except Exception as e:
                print(f"   HTTP failed: {e}")
                
    except ImportError:
        print("   aiohttp not available (will try pywiim)")
    
    return False


async def main():
    """Main hardware testing function"""
    
    print("\n📋 HARDWARE TEST PLAN:")
    print("   1. Test direct IP connectivity via pywiim")
    print("   2. Test HTTP API endpoint directly")
    print("   3. Report results and next steps")
    
    # Test 1: Direct connection with pywiim
    client = await test_wiim_connectivity()
    
    if not client:
        print("\n" + "="*60)
        print("📝 HARDWARE ACCESS STATUS:")
        print("="*60)
        print("""
Connection requires WiiM app API configuration:

1. Configure WiiM App API Access:
   - Open WiiM mobile app → Settings → Advanced
   - Enable "API Access" 
   - Set admin username/password (if not already set)

2. Verify Network Connectivity:
   - Ensure both PC and Wiim are on same WiFi network (192.168.4.x)
   
3. Retry Test with Credentials:
   python experiments/01_wiim_testing/hardware_test.py
   
[INCOMPLETE] - Hardware integration awaiting credentials configuration
        """)
    
    # Test 2: HTTP API as alternative
    print("\n[Test] Alternative HTTP API test...")
    await test_direct_http()


if __name__ == "__main__":
    asyncio.run(main())
