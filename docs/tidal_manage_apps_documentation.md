# 🎵 SONIC FLUX - TIDAL APP REGISTRATION & CREDENTIALS GUIDE
## Extracted from TIDAL Developer Portal: "Manage Apps" Documentation

**Source:** `https://developer.tidal.com/documentation/api-sdk/api-sdk-manage-apps`  
**Date:** August 15, 2026  
**Repository:** https://github.com/Magoo2You/sonic-flux

---

## 📋 **APP REGISTRATION REQUIREMENTS**

### **Dashboard Overview**
- The Dashboard is where you create and manage apps that use the TIDAL API and TIDAL SDK.
- Log in with your regular TIDAL account to access the Dashboard.
- If no account: register at `https://account.tidal.com`

### **First-Time Login**
- Must accept TIDAL Guidelines on first login
- Dashboard shows existing apps + option to create new ones

### **Application Limits**
- **Maximum:** 10 applications per developer account
- **Recommendation:** Register at least 2 apps:
  - One for development and testing
  - One for production (keeps credentials isolated)
- If you need more: delete an existing application first

---

## 🔑 **CREDENTIALS MANAGEMENT**

### **Client ID & Client Secret**
- TIDAL automatically generates unique **Client ID** and **Client Secret** when creating an app.
- **Security:** Client Secret is hidden after leaving the page
- To copy secret: use clipboard icon or reveal by entering TIDAL account password
- Read Authorization guide for best practices

### **App Settings**
- Edit app information under "Settings" tab
- Fill out fields accurately - visible to end users when they log in through your app
- If information not credible, TIDAL may disable your app
- Can disable app or temporarily restrict API access under "App settings"
- To delete: must first disable the application

### **Scope Principle**
- Only enable scopes your application needs (minimum necessary access)

---

## ✅ **YOUR CURRENT CREDENTIALS STATUS**

Based on `.env` file and project configuration:

```
TIDAL_CLIENT_ID=NtutRUnuR8i8waHY
TIDAL_CLIENT_SECRET=*** (securely stored, not in git)
```

These credentials are ready for OAuth 2.0 authentication flows!

---

## 📝 **CURRENT KNOWLEDGE BASE**

### **From Manage Apps Page:**
✅ App registration process  
✅ Client ID/Secret generation and handling  
✅ Dashboard overview and app management  
✅ Scope principle (minimum access)  
✅ Production vs Development app isolation recommendation  

### **From Your API Spec:**
✅ Complete endpoint list (400+)  
✅ OAuth 2.0 authentication flows  
✅ JSON:API response structures  
✅ Error handling guidelines  

### **From Authorization Page (to explore next):**
⏳ OAuth token endpoints  
⏳ Client credentials flow details  
⏳ Authorization code + PKCE implementation  
⏳ Token refresh strategies  

---

## 🚀 **NEXT EXPLORATION PRIORITY**

The **Authorization** page is critical for understanding:
1. How to obtain access tokens
2. OAuth 2.0 token endpoints and request formats
3. Scopes and permissions required
4. PKCE implementation details
5. Token refresh/rotation strategies

---

## 📋 **DOCUMENTATION STATUS**

| Section | Status | Documentation |
|---------|--------|---------------|
| App Registration (Manage Apps) | ✅ Complete | Extracted and documented |
| API Endpoints | ✅ Complete | Your spec (17KB) |
| OAuth Authentication | ⏳ Pending | Authorization page next |
| SDK Examples | ⏳ Pending | Quick Start page |
| Error Handling | ⏳ Pending | Reference pages |

---

**Shall I navigate to the Authorization page next?** 🎯
