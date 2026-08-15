#!/usr/bin/env python3
"""
Sonic Flux - Simple HTTP Test with SSL Verification Disabled
=============================================================
Tests device status with urllib and disabled SSL verification

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Command: getStatusEx
"""

import urllib.request
import urllib.parse
import json


def get_device_status_raw():
    """Get full device status via getStatusEx endpoint."""
    
    url = "https://192.168.4.41/httpapi.asp?command=getStatusEx"
    
    print("=" * 70)
    print("📋 RAW RESPONSE TEST - getStatusEx")
    print("=" * 70)
    print(f"URL: {url}")
    print("-" * 70)
    
    try:
        # Create request with SSL verification disabled
        req = urllib.request.Request(url)
        
        # Use ssl._create_unverified_context to disable SSL verification
        import ssl
        context = ssl._create_unverified_context()
        
        with urllib.request.urlopen(req, timeout=15, context=context) as response:
            http_status = response.getcode()
            raw_content = response.read().decode('utf-8')
            
            print(f"\n✅ HTTP Status Code: {http_status}")
            print(f"Response Size: {len(raw_content)} bytes")
            print("\nRaw Response Content:")
            print("-" * 70)
            
            # Print full response (truncated to first ~3500 chars)
            print(raw_content[:3500])
            
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error - Code: {e.code}")
        print(f"Reason: {e.reason}")
        
    except urllib.error.URLError as e:
        print(f"\n❌ URL Error - {type(e.reason).__name__}: {e.reason}")
        
    except Exception as e:
        print(f"\n❌ Unexpected Error - {type(e).__name__}: {e}")


if __name__ == "__main__":
    get_device_status_raw()
