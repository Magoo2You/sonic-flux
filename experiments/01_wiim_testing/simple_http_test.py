#!/usr/bin/env python3
"""
Sonic Flux - Simple HTTP Test: getStatusEx
=====================================================
Tests device status with basic urllib to see raw response

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Command: getStatusEx
"""

import urllib.request
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
        # Create request with no SSL verification (self-signed cert)
        req = urllib.request.Request(url, headers={'User-Agent': 'SonicFlux/1.0'})
        
        # Use context manager to handle connection properly
        with urllib.request.urlopen(req, timeout=15, cafile=None) as response:
            http_status = response.getcode()
            raw_content = response.read().decode('utf-8')
            
            print(f"\n✅ HTTP Status Code: {http_status}")
            print(f"Response Size: {len(raw_content)} bytes")
            print("\nRaw Response Content:")
            print("-" * 70)
            
            # Print full response
            print(raw_content[:3000])  # First 3000 chars
            
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error - Code: {e.code}")
        print(f"Reason: {e.reason}")
        
    except urllib.error.URLError as e:
        print(f"\n❌ URL Error - {type(e.reason).__name__}: {e.reason}")
        
    except Exception as e:
        print(f"\n❌ Unexpected Error - {type(e).__name__}: {e}")


if __name__ == "__main__":
    get_device_status_raw()
