# 🎵 SONIC FLUX - STREAMING SERVICE INTEGRATION GUIDE
## WiiM Streaming Mode & App Preset Activation

**Date:** August 15, 2026  
**Repository:** https://github.com/Magoo2You/sonic-flux

---

## 📋 **NEW SOURCE INFORMATION ADDED**

This documentation captures a critical new source of information regarding WiiM streaming service integration that must be incorporated into our project.

### **Core Concept:**
To switch your WiiM device to a streaming service using the HTTP API, you must:
1. **Force hardware into Wi-Fi mode** (away from physical inputs)
2. **Launch the specific service's URL or preset**

---

## 🔧 **METHOD 1: Direct Streaming URL Play**

### **Step A: Force Device to Network (Wi-Fi) Mode**

Before playing any cloud stream, ensure the WiiM shifts away from physical inputs:

```bash
http://<YOUR_WIIM_IP>/httpapi.asp?command=setPlayerCmd:switchmode:wifi
```

**Example:**
```bash
curl -k "http://192.168.4.41/httpapi.asp?command=setPlayerCmd:switchmode:wifi"
```

---

### **Step B: Play Specific Streaming URL (Radio, TuneIn, Icecast)**

If you have a direct streaming link (internet radio station, M3U stream, audio file URL):

```bash
http://<YOUR_WIIM_IP>/httpapi.asp?command=setPlayerCmd:play:<STREAMING_URL>
```

**Example:**
```bash
curl -k "http://192.168.4.41/httpapi.asp?command=setPlayerCmd:play:http://stream.example.com"
```

---

## 📱 **METHOD 2: Trigger Saved App Preset (Spotify, Tidal, Amazon Music)**

**CRITICAL FOR CLOUD SERVICES:** Secure platforms like Spotify, Tidal, and Amazon Music don't allow arbitrary playback through raw URLs. The standard automation practice is to save the playlist/station inside your WiiM Home App's Presets section first. Then trigger that slot remotely:

```bash
http://<YOUR_WIIM_IP>/httpapi.asp?command=MCUKeyShortClick:<PRESET_NUMBER>
```

**Replace `<PRESET_NUMBER>` with numbers 1 through 12** (based on your saved shortcuts).

**Example:**
```bash
curl -k "http://192.168.4.41/httpapi.asp?command=MCUKeyShortClick:3"
# This triggers preset slot #3 (which you configured in WiiM Home app to play Amazon Music)
```

---

## 💡 **KEY INSIGHTS**

### **Why Two Methods?**

- **Method 1 (Direct URL)**: Works for internet radio streams, TuneIn stations, Icecast servers - any direct streaming URL
- **Method 2 (App Preset)**: Required for cloud services (Spotify Connect, Tidal Connect, Amazon Music) due to authentication/authorization requirements handled by the app

### **Preset Slot Configuration**

1. Open **WiiM Home App** on your phone/tablet
2. Go to **Settings → Shortcuts** (or similar menu)
3. Select slot number 1-12
4. Configure to launch your preferred cloud service or radio station
5. Remember which preset slot corresponds to which service

---

## 📝 **IMPLEMENTATION NOTE FOR SONIC FLUX PROJECT**

This information is critical for:

1. **Amazon Music Integration**: We'll need to teach the user to configure preset slots 1-12 in their WiiM Home app for Amazon Music playlists
2. **Alternative Stream Discovery**: For internet radio stations, we can play direct URLs via Method 1
3. **User Experience**: GUI should guide users through:
   - Configuring preset slots (one-time setup)
   - Playing preset by number (quick control)

---

**Status:** ✅ **NEW SOURCE DOCUMENTED** - Ready to integrate into master documentation!
