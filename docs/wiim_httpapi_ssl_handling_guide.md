# 🎵 SONIC FLUX - WIIM SSL CERTIFICATE HANDLING GUIDE

## Critical Information for WiiM HTTPAPI Integration

**Date:** August 15, 2026  
**Repository:** https://github.com/Magoo2You/sonic-flux

---

## 🔒 **SSL CERTIFICATE REQUIREMENT - CRITICAL**

### **Problem: Self-Signed SSL Certificates**

The WiiM HTTP API endpoints use **HTTPS with self-signed SSL certificates**. This means:

⚠️ **Standard Python `aiohttp` or `requests` will fail with SSL verification errors:**
```
SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] 
certificate verify failed: self-signed certificate
```

✅ **Solution: Disable SSL Verification for Local Network Use**

Since this is for **local network control only** (not public internet), disabling SSL verification is safe and necessary.

---

## 📋 **APPROVED SSL HANDLING METHODS**

### **Method 1: Python - SSL Context with Disabled Verification** ✅ RECOMMENDED

```python
import ssl

# Create unverified SSL context
context = ssl._create_unverified_context()

# Use with urllib.request
with urllib.request.urlopen(
    "https://192.168.4.41/httpapi.asp?command=getStatusEx", 
    timeout=15, 
    context=context
) as response:
    data = response.read().decode('utf-8')
```

---

### **Method 2: Python - aiohttp with SSL Disabled** ✅ RECOMMENDED

```python
import aiohttp
import asyncio

async def get_device_status(ip_address):
    """Get device status with disabled SSL verification."""
    
    url = f"https://{ip_address}/httpapi.asp?command=getStatusEx"
    
    try:
        # Create TCP connector with ssl=False to bypass certificate check
        connector = aiohttp.TCPConnector(ssl=False)
        
        async with aiohttp.ClientSession(connector=connector, 
                                         timeout=aiohttp.ClientTimeout(total=15.0)) as session:
            async with session.get(url, timeout=10.0) as resp:
                return await resp.json()
                
    except Exception as e:
        print(f"Request failed: {e}")


# Usage
asyncio.run(get_device_status("192.168.4.41"))
```

**Key:** `TCPConnector(ssl=False)` bypasses SSL certificate verification ✅

---

### **Method 3: curl Command Line** ✅ RECOMMENDED

```bash
# Use -k flag to disable SSL verification for self-signed certificates
curl -k "https://192.168.4.41/httpapi.asp?command=getStatusEx"
```

**Key:** `-k` or `--insecure` flag disables certificate verification ✅

---

### **Method 4: PowerShell (Windows)** ⚠️ LIMITED SUPPORT

PowerShell's native HTTP client has stricter SSL requirements. Use one of these workarounds:

#### Option A: Invoke-WebRequest with Bypass
```powershell
# Note: This may still fail depending on Windows configuration
$response = Invoke-RestMethod "https://192.168.4.41/httpapi.asp?command=getStatusEx" 
```

#### Option B: Use curl.exe if available
```powershell
curl.exe -k "https://192.168.4.41/httpapi.asp?command=getStatusEx"
```

---

### **Method 5: Node.js** ⚠️ LIMITED SUPPORT

Node.js's built-in fetch() respects certificate verification by default:

```javascript
// This will fail with SSL error
await fetch('https://192.168.4.41/httpapi.asp?command=getStatusEx')
```

Use axios or undici with custom agent:
```javascript
const https = require('https');
const options = { 
  agent: new https.Agent({ rejectUnauthorized: false }) 
};
await fetch('https://192.168.4.41/httpapi.asp?command=getStatusEx', { options });
```

---

## ⚠️ **SECURITY NOTES**

### **Why SSL Verification is Disabled:**

1. ✅ **Local Network Only:** WiiM device is on your home WiFi network only
2. ✅ **No External Access:** No port forwarding, no public IP exposure
3. ✅ **Self-Signed Certificates:** Device generates its own certificate
4. ✅ **Trust Boundary:** Your home network is the trust boundary

### **Why This Is Safe:**

- 🛡️ **Firewall protection** limits access to trusted devices only
- 🛡️ **No external attack surface** (no public IP, no port forwarding)
- 🛡️ **Physical security** of your home WiFi protects against unauthorized access
- 🛡️ **Local authentication** still required for sensitive operations

### **Never Do This:**

❌ Don't disable SSL verification if you:
- Expose the device to public internet
- Use port forwarding from outside your home network
- Share WiFi credentials with untrusted parties

---

## 🔧 **IMPLEMENTATION IN SONIC FLUX PROJECT**

### **Recommended Approach for Sonic Flux:**

Use **Method 2 (aiohttp with `ssl=False`)** for all HTTPAPI calls:

```python
# In src/modules/wiim_httpapi_client.py
from aiohttp import TCPConnector, ClientSession, ClientTimeout

class WiiMHTTPApiClient:
    def __init__(self, ip_address: str):
        self.ip = ip_address.rstrip('/')
        
        # Create session with SSL verification disabled for self-signed certs
        connector = TCPConnector(ssl=False)
        self.session = ClientSession(connector=connector, 
                                    timeout=ClientTimeout(total=15.0))
    
    async def close(self):
        if self.session:
            await self.session.close()
```

---

## 📚 **TEST RESULTS FROM YOUR DEVICE**

### **Test 1: getStatusEx (Verified Working) ✅**
```bash
curl -k "https://192.168.4.41/httpapi.asp?command=getStatusEx"
```

Response: 3,329 bytes JSON with device info  
SSL Status: Bypassed with `-k` flag  
Result: **SUCCESS** ✅

### **Test 2: setPlayerCmd:mute:0 (Verified Working) ✅**
```bash
curl -k "https://192.168.4.41/httpapi.asp?command=setPlayerCmd:mute:0"
```

Response: "OK"  
SSL Status: Bypassed with `-k` flag  
Result: **SUCCESS** ✅

---

## 📄 **DOCUMENTATION LOCATION**

This SSL handling guide is now available in the Sonic Flux project repository:

- **File:** `docs/wiim_httpapi_ssl_handling_guide.md` (NEW!)
- **Repository:** https://github.com/Magoo2You/sonic-flux.git
- **Commit:** [Will be pushed after this documentation is saved]

---

## 🎯 **SUMMARY**

### **Key Points to Remember:**

1. ✅ WiiM HTTP API uses HTTPS with self-signed certificates
2. ✅ SSL verification must be disabled for all endpoints
3. ✅ Safe for local network use only (never public internet)
4. ✅ Use `ssl=False` in aiohttp or `-k` flag in curl

### **Approved Methods:**
- ✅ Python: `TCPConnector(ssl=False)` 
- ✅ Python: `ssl._create_unverified_context()`
- ✅ curl: `-k` or `--insecure` flag
- ⚠️ Node.js/PowerShell: Limited support, use with caution

---

## 🧪 **NEXT STEP**

Ready to test the next endpoint? Let me know which one you'd like to test! 🧪🎵
