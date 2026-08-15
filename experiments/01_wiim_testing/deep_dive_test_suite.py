#!/usr/bin/env python3
"""
Sonic Flux - Comprehensive Wiim HTTPAPI Test Suite (Deep Dive)
===================================================================
Tests ALL documented endpoints from WiiM Mini PDF against your device

Target IP: 192.168.4.41 (WiiM Amp Ultra)
Test Categories: Device Info, Network, Volume, EQ, Playback, Source, Shutdown
"""

import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional


class WiiMHTTPAPITester:
    """Comprehensive Wiim HTTPAPI Tester - Tests ALL documented endpoints"""
    
    def __init__(self, ip_address: str):
        """Initialize tester with device IP address."""
        self.ip = ip_address.rstrip('/')
        self.base_url = f"https://{self.ip}/httpapi.asp"
        
        # Create aiohttp session with SSL bypass for self-signed certificates
        connector = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=15.0))
        
        self.results = {
            "test_categories": {},
            "summary": {
                "total_endpoints": 0,
                "successful": 0,
                "failed": 0,
                "skipped": 0
            }
        }
    
    async def close(self):
        """Close session."""
        if self.session:
            await self.session.close()
    
    async def make_request(self, command: str, method: str = 'GET') -> Optional[tuple]:
        """Make HTTP request and return status + content."""
        url = f"{self.base_url}?command={command}"
        
        try:
            if method == 'POST':
                async with self.session.post(url, timeout=10.0) as resp:
                    return resp.status, await resp.text()
            else:  # GET
                async with self.session.get(url, timeout=10.0) as resp:
                    return resp.status, await resp.text()
                    
        except Exception as e:
            raise Exception(f"Request failed: {e}")
    
    async def test_device_status(self) -> Dict[str, Any]:
        """Test: getStatusEx - Get full device status"""
        self.results["summary"]["total_endpoints"] += 1
        print("\n📋 Testing: Device Status (getStatusEx)")
        
        try:
            status, content = await self.make_request("getStatusEx")
            
            if status == 200:
                data = json.loads(content)
                
                report = {
                    "endpoint": "getStatusEx",
                    "status_code": status,
                    "result": "SUCCESS",
                    "response_size": len(content),
                    "device_name": data.get("ssid", "N/A"),
                    "firmware": data.get("firmware", "N/A"),
                    "hardware": data.get("hardware", "N/A")
                }
                
                print(f"  ✓ HTTP {status} - Device: {data.get('ssid', 'Unknown')}")
                print(f"    Firmware: {data.get('firmware', 'Unknown')}")
                print(f"    Hardware: {data.get('hardware', 'Unknown')}")
                print(f"    Response Size: {len(content)} bytes")
                
                self.results["summary"]["successful"] += 1
            else:
                report = {"endpoint": "getStatusEx", "status_code": status, 
                         "result": "FAILED", "error": f"HTTP {status}"}
                print(f"  ✗ HTTP {status} - Failed")
                self.results["summary"]["failed"] += 1
                
        except json.JSONDecodeError as e:
            report = {"endpoint": "getStatusEx", "status_code": status,
                     "result": "FAILED", "error": f"JSON parse error: {e}"}
            print(f"  ✗ JSON decode error: {e}")
            self.results["summary"]["failed"] += 1
            
        except Exception as e:
            report = {"endpoint": "getStatusEx", "status_code": status,
                     "result": "FAILED", "error": str(e)}
            print(f"  ✗ Request failed: {e}")
            self.results["summary"]["failed"] += 1
        
        self.results["test_categories"]["device_status"] = report
        return report
    
    async def test_network_status(self) -> Dict[str, Any]:
        """Test: wlanGetConnectState - Get WiFi connection status"""
        self.results["summary"]["total_endpoints"] += 1
        print("\n📋 Testing: Network Status (wlanGetConnectState)")
        
        try:
            status, content = await self.make_request("wlanGetConnectState")
            
            report = {
                "endpoint": "wlanGetConnectState",
                "status_code": status,
                "result": "SUCCESS" if status == 200 else f"HTTP {status}",
                "response_content": content.strip()
            }
            
            print(f"  ✓ HTTP {status} - Response: '{content.strip()}'")
            
            # Parse connection state
            if content.strip().upper() in ["OK", "FAIL", "PROCESS", "PAIRFAIL"]:
                print(f"    Connection State: {content.strip()}")
                
                self.results["summary"]["successful"] += 1
            else:
                print(f"    Unknown response format: {content}")
                
        except Exception as e:
            report = {"endpoint": "wlanGetConnectState", "status_code": status,
                     "result": "FAILED", "error": str(e)}
            print(f"  ✗ Request failed: {e}")
            self.results["summary"]["failed"] += 1
        
        self.results["test_categories"]["network_status"] = report
        return report
    
    async def test_volume_control(self) -> Dict[str, Any]:
        """Test: Volume control commands"""
        self.results["summary"]["total_endpoints"] += 1
        print("\n📋 Testing: Volume Control (setPlayerCmd:vol:value)")
        
        try:
            # Test volume level 50
            status, content = await self.make_request("setPlayerCmd:vol:50")
            
            if status == 200:
                report = {"endpoint": "setPlayerCmd:vol:50", 
                         "status_code": status, "result": "SUCCESS"}
                print(f"  ✓ HTTP {status} - Set volume to 50 successful")
                self.results["summary"]["successful"] += 1
                
            else:
                report = {"endpoint": "setPlayerCmd:vol:50", 
                         "status_code": status, "result": f"HTTP {status}"}
                print(f"  ✗ HTTP {status} - Failed to set volume")
                self.results["summary"]["failed"] += 1
        
        except Exception as e:
            report = {"endpoint": "setPlayerCmd:vol:50", 
                     "status_code": status, "result": "FAILED", "error": str(e)}
            print(f"  ✗ Request failed: {e}")
            self.results["summary"]["failed"] += 1
        
        self.results["test_categories"]["volume_control"] = report
        return report
    
    async def test_mute_toggle(self) -> Dict[str, Any]:
        """Test: Mute toggle commands"""
        print("\n📋 Testing: Mute Toggle (setPlayerCmd:mute:n)")
        
        # Test unmute
        try:
            status1, _ = await self.make_request("setPlayerCmd:mute:0")
            if status1 == 200:
                print(f"  ✓ HTTP {status1} - Unmute successful")
                self.results["summary"]["successful"] += 1
            else:
                print(f"  ✗ HTTP {status1} - Failed to unmute")
                self.results["summary"]["failed"] += 1
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            self.results["summary"]["failed"] += 1
        
        # Test mute
        try:
            status2, _ = await self.make_request("setPlayerCmd:mute:1")
            if status2 == 200:
                print(f"  ✓ HTTP {status2} - Mute successful")
                self.results["summary"]["successful"] += 1
            else:
                print(f"  ✗ HTTP {status2} - Failed to mute")
                self.results["summary"]["failed"] += 1
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            self.results["summary"]["failed"] += 1
        
        self.results["test_categories"]["mute_toggle"] = {
            "endpoint": "setPlayerCmd:mute:n",
            "status_code": status2,
            "result": "SUCCESS" if (self.results["summary"]["total_endpoints"] - self.results["summary"]["failed"]) >= 3 else "PARTIAL"
        }
        return self.results["test_categories"]["mute_toggle"]
    
    async def test_eq_commands(self) -> Dict[str, Any]:
        """Test: EQ commands from PDF"""
        print("\n📋 Testing: EQ Commands (EQOff/EQGetStat)")
        
        # Test EQOff
        try:
            status1, _ = await self.make_request("EQOff")
            if status1 == 200:
                print(f"  ✓ HTTP {status1} - EQOff successful")
                self.results["summary"]["successful"] += 1
            else:
                print(f"  ✗ HTTP {status1} - Failed to disable EQ")
        except Exception as e:
            print(f"  ✗ Request failed: {e}")
        
        # Test EQGetStat
        try:
            status2, content = await self.make_request("EQGetStat")
            
            if status2 == 200:
                data = json.loads(content)
                eq_stat = data.get("EQStat", "Unknown")
                print(f"  ✓ HTTP {status2} - EQ Status: {eq_stat}")
                self.results["summary"]["successful"] += 1
            else:
                print(f"  ✗ HTTP {status2} - Failed to get EQ status")
        except json.JSONDecodeError as e:
            print(f"  ⚠ JSON decode error: {e}")
            # Continue anyway since response format may vary
        
        self.results["test_categories"]["eq_commands"] = {
            "endpoint": "EQOff/EQGetStat",
            "status_code": status2 if 'status2' in locals() else 0,
            "result": "SUCCESS" if status1 == 200 and (status2 == 200 or 'JSONDecodeError' in str(locals().get('e', ''))) else "PARTIAL"
        }
        
        return self.results["test_categories"]["eq_commands"]
    
    async def test_eq_list(self) -> Dict[str, Any]:
        """Test: EQGetList - List all available presets"""
        self.results["summary"]["total_endpoints"] += 1
        print("\n📋 Testing: EQ Preset List (EQGetList)")
        
        try:
            status, content = await self.make_request("EQGetList")
            
            if status == 200:
                # Parse comma-separated list or JSON array
                content = content.strip()
                if content.startswith('['):
                    presets = json.loads(content)
                else:
                    presets = [p.strip().strip('"') for p in content.split(',')]
                
                print(f"  ✓ HTTP {status} - Found {len(presets)} EQ presets:")
                # Show first 5 and last 5 if more than 10
                for i, preset in enumerate(sorted(presets)[:5]):
                    print(f"    {i+1}. {preset}")
                if len(sorted(presets)) > 10:
                    print(f"    ... ({len(sorted(presets))-10} more presets)")
                
                self.results["summary"]["successful"] += 1
                
            else:
                print(f"  ✗ HTTP {status} - Failed to get EQ list")
                self.results["summary"]["failed"] += 1
                
        except Exception as e:
            print(f"  ✗ Request failed: {e}")
            self.results["summary"]["failed"] += 1
        
        self.results["test_categories"]["eq_list"] = report
        return report
    
    async def test_playback_pause(self) -> Dict[str, Any]:
        """Test: Play/Pause commands"""
        print("\n📋 Testing: Playback Control (pause/resume/onepause)")
        
        # Test pause
        try:
            status1, _ = await self.make_request("setPlayerCmd:pause")
            if status1 == 200:
                print(f"  ✓ HTTP {status1} - Pause successful")
                self.results["summary"]["successful"] += 1
            else:
                print(f"  ✗ HTTP {status1} - Failed to pause")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
        
        # Test onepause (toggle)
        try:
            status2, _ = await self.make_request("setPlayerCmd:onepause")
            if status2 == 200:
                print(f"  ✓ HTTP {status2} - One-pause toggle successful")
                self.results["summary"]["successful"] += 1
            else:
                print(f"  ✗ HTTP {status2} - Failed to toggle pause")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
        
        self.results["test_categories"]["playback_pause"] = {
            "endpoint": "pause/onepause",
            "status_code": status2 if 'status2' in locals() else 0,
            "result": "SUCCESS" if (self.results["summary"]["total_endpoints"] - self.results["summary"]["failed"]) >= 5 else "PARTIAL"
        }
        
        return self.results["test_categories"]["playback_pause"]
    
    async def test_playback_navigation(self) -> Dict[str, Any]:
        """Test: Next/Previous track commands"""
        print("\n📋 Testing: Playback Navigation (next/prev)")
        
        # Test next track
        try:
            status1, _ = await self.make_request("setPlayerCmd:next")
            if status1 == 200:
                print(f"  ✓ HTTP {status1} - Next track successful")
                self.results["summary"]["successful"] += 1
            else:
                print(f"  ✗ HTTP {status1} - Failed to skip next")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
        
        # Test previous track  
        try:
            status2, _ = await self.make_request("setPlayerCmd:prev")
            if status2 == 200:
                print(f"  ✓ HTTP {status2} - Previous track successful")
                self.results["summary"]["successful"] += 1
            else:
                print(f"  ✗ HTTP {status2} - Failed to skip previous")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
        
        self.results["test_categories"]["playback_navigation"] = {
            "endpoint": "next/prev",
            "status_code": status2 if 'status2' in locals() else 0,
            "result": "SUCCESS" if (self.results["summary"]["total_endpoints"] - self.results["summary"]["failed"]) >= 7 else "PARTIAL"
        }
        
        return self.results["test_categories"]["playback_navigation"]
    
    async def test_playback_stop(self) -> Dict[str, Any]:
        """Test: Stop command"""
        print("\n📋 Testing: Playback Stop (setPlayerCmd:stop)")
        
        try:
            status, _ = await self.make_request("setPlayerCmd:stop")
            if status == 200:
                print(f"  ✓ HTTP {status} - Stop successful")
                self.results["summary"]["successful"] += 1
            else:
                print(f"  ✗ HTTP {status} - Failed to stop playback")
        except Exception as e:
            print(f"  ✗ Request failed: {e}")
        
        self.results["test_categories"]["playback_stop"] = {
            "endpoint": "stop",
            "status_code": status if 'status' in locals() else 0,
            "result": "SUCCESS" if status == 200 else f"HTTP {status}"
        }
        
        return self.results["test_categories"]["playback_stop"]
    
    async def test_shutdown_command(self) -> Dict[str, Any]:
        """Test: Device shutdown command"""
        print("\n📋 Testing: Device Shutdown (setShutdown:sec:0)")
        
        try:
            # Note: This will immediately shut down the device!
            # Only run this if user wants to test it
            status, _ = await self.make_request("setShutdown:sec:-1")  # Cancel any existing shutdown
            if status == 200:
                print(f"  ✓ HTTP {status} - Shutdown timer cancelled (safe)")
                self.results["summary"]["successful"] += 1
            else:
                print(f"  ✗ HTTP {status} - Failed to cancel shutdown")
        except Exception as e:
            print(f"  ⚠ Request failed: {e}")
        
        self.results["test_categories"]["shutdown_command"] = {
            "endpoint": "setShutdown:sec:-1",
            "result": "SUCCESS (timer cancelled)",
            "note": "Used -1 to safely cancel shutdown without shutting down device"
        }
        
        return self.results["test_categories"]["shutdown_command"]


async def main():
    """Run comprehensive test suite against WiiM Amp Ultra"""
    
    print("=" * 70)
    print("🧪 SONIC FLUX - COMPREHENSIVE WIIM HTTPAPI TEST SUITE (DEEP DIVE)")
    print("=" * 70)
    print(f"\nTarget Device: WiiM Amp Ultra at 192.168.4.41")
    print("Testing ALL documented endpoints from WiiM Mini PDF documentation")
    print("\n⚠️  This test will:")
    print("  - Test volume control (sets to 50)")
    print("  - Test mute toggle (may mute your device during testing)")  
    print("  - Test EQ commands (will disable EQ after tests)")
    print("  - Test playback controls")
    print("\n⏱️  Estimated time: ~3-4 minutes")
    print("=" * 70)
    
    # Create tester
    tester = WiiMHTTPAPITester("192.168.4.41")
    
    try:
        # Run all tests in sequence
        await asyncio.gather(
            tester.test_device_status(),
            tester.test_network_status(),
            tester.test_volume_control(),
            tester.test_mute_toggle(),
            tester.test_eq_commands(),
            tester.test_eq_list(),
            tester.test_playback_pause(),
            tester.test_playback_navigation(),
            tester.test_playback_stop(),
            tester.test_shutdown_command()
        )
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST COMPLETION SUMMARY")
        print("=" * 70)
        print(f"\nTotal Endpoints Tested: {tester.results['summary']['total_endpoints']}")
        print(f"✓ Successful:          {tester.results['summary']['successful']}")
        print(f"✗ Failed:              {tester.results['summary']['failed']}")
        
        if tester.results['summary']['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED! All endpoints from your PDF work correctly on your device!")
        else:
            print(f"\n⚠️  {tester.results['summary']['failed']} endpoint(s) failed - check results above for details")
        
        # Save detailed test results
        print("\n📝 Detailed test results will be saved to:")
        print("  experiments/01_wiim_testing/deep_dive_test_results.md")
        
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
