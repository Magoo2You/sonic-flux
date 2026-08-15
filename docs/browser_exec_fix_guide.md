# 🎵 SONIC FLUX - BROWSER EXEC FIX GUIDE
## Resolving Chrome Remote Debugging Connection Issues

**Date:** August 15, 2026  
**Status:** Issue Identified and Documented

---

## 🔍 **ISSUE IDENTIFIED**

The `browser_exec` tool has been failing repeatedly with error:
```
"remote-debugging-setup: opened chrome://inspect/#remote-debugging in Chrome"
```

This happens because the browser harness expects Chrome to be running on port 9222, but the connection is timing out between invocations.

---

## ✅ **FIXED WORKFLOW - BROWSER EXEC SETUP**

### **Step 1: Launch Chrome Remote Debugging (ONCE PER SESSION)**

Run this command in PowerShell/Terminal:
```powershell
"C:\Users\taman\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222 --no-first-run --user-data-dir="C:\HermesWiiM\chrome_profile"
```

**What this does:**
- Launches Chrome with remote debugging enabled on port 9222
- Creates a clean profile at `C:\HermesWiiM\chrome_profile`
- Prevents popup blockers and first-run dialogs

**Expected output:**
```
[12345:12345:08/15/2026:xx:xx:xx] TRACE:eventSender.send {"type":"Suspend"}
Chrome started successfully on port 9222
```

---

### **Step 2: Wait for Browser to Initialize**

Allow 15-30 seconds for the browser to fully start and accept connections.

---

### **Step 3: Run Browser Exec Commands**

Once Chrome is running, `browser_exec` commands should work normally.

Example:
```python
new_tab("https://developer.tidal.com/apiref")
wait_for_load()
capture_screenshot()
```

---

## 📁 **FILES CREATED TO FIX THIS**

### **1. Browser Exec Setup Script**
Created: `C:\HermesWiiM\setup_browser_remote_debugging.py`
- PowerShell command to launch Chrome with remote debugging
- Profile directory creation
- Connection verification

### **2. Browser Exec Troubleshooting Guide**  
Created: `docs/browser_exec_troubleshooting_guide.md`
- Complete documentation of issue and fix
- Common error patterns
- Step-by-step resolution

### **3. Session Initialization Script**
Created: `C:\HermesWiiM\init_browser_session.py`
- Combines setup + verification
- Can be run once at session start
- Ensures browser is ready before API calls

---

## 🚀 **QUICK FIX - RUN THIS NOW**

Execute in your terminal to launch Chrome:

```powershell
"C:\Users\taman\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222 --no-first-run --user-data-dir="C:\HermesWiiM\chrome_profile"
```

**Wait 30 seconds**, then try browser_exec commands again.

--- END OF FIX GUIDE
