# 🎵 SONIC FLUX - TIDAL OAUTH SETUP GUIDE

## How to Complete OAuth Authorization

---

### **STEP 1: Run the Authorization Script**

```bash
cd C:\HermesWiiM
python experiments/tidal_oauth_auth.py
```

---

### **STEP 2: What Happens Next**

The script will:

1. ✅ Load your TIDAL Client ID from `.env` file (secure)
2. ⚠️ Check if you already have a valid cached token
3. 📋 Generate an authorization URL with PKCE security
4. 🔍 Launch your default browser to the TIDAL login page

---

### **STEP 3: Complete Authorization in Browser**

When the browser opens, you'll see:

1. **TIDAL Login Page** - Enter your username/password
2. **Authorization Request** - Approve permissions for "Sonic Flux"
3. **Redirect** - Browser will redirect back to `http://localhost:8000/callback` with an authorization code in the URL

---

### **STEP 4: Provide Authorization Code**

After authorization, the script will ask you to paste the authorization code from the redirect URL.

Example redirect URL:
```
http://localhost:8000/callback?code=A1B2C3D4E5F6G7H8I9J0...&state=...
```

**Copy everything after `code=` and paste it when prompted.**

---

### **STEP 5: Tokens Saved Successfully!**

After successful authorization, the script will:
- ✅ Exchange authorization code for access + refresh tokens
- 💾 Save tokens to `data/tidal_token_store.json`
- 📋 Display token expiration time (typically 4 hours)
- 🎉 Confirm you're ready to use the API!

---

### **STEP 6: Test Your Authorization**

Run the test script:
```bash
python experiments/tidal_oauth_flow_test.py
```

This will verify your tokens are working and show token details.

---

## 🔍 **IMPORTANT NOTES**

### **Redirect URI**
The authorization script uses: `http://localhost:8000/callback`

**Make sure this matches what you registered in the TIDAL developer portal!**

To check/modify:
1. Go to: https://developer.tidal.com/documentation/api-sdk/authorization
2. Find your app registration
3. Verify "Redirect URI" matches `http://localhost:8000/callback`
4. If different, update in the portal and restart authorization

---

### **Token Expiration**
- Access tokens expire after **~4 hours** (14400 seconds)
- Refresh tokens allow getting new access tokens
- Tokens are automatically refreshed when needed
- Token expiry is shown in output

---

### **Security Features**
- ✅ PKCE (S256) - Prevents authorization code interception attacks
- ✅ Scoped access (`data:read`, `data:write`)
- ✅ Secure token storage in JSON file
- ✅ Credentials never printed to console

---

## 🎉 **SUCCESS INDICATORS**

You'll know authorization worked when you see:

```
✅ Client ID loaded (secured)
📌 Exchanging authorization code for tokens...
✅ Token exchange successful!

Token details:
  • Access Token: eyJraW...[truncated]...
  • Expires in: 14400 ms (14.4 seconds)
  • Scope: data:read data:write

💾 Tokens saved to: C:\HermesWiiM\data\tidal_token_store.json

🎉 AUTHORIZATION COMPLETE!
```

--- END OF SETUP GUIDE
