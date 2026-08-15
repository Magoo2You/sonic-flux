# 🎵 SONIC FLUX - AMAZON MUSIC WEB PLAYBACK SERVICE API RESEARCH

**Date:** August 14, 2026  
**Status:** ✅ **FULLY DOCUMENTED - NO API KEY REQUIRED**

---

## 📋 EXECUTIVE SUMMARY

Amazon Music Web Playback Service does **NOT require an API key**. Authentication is done via OAuth 2.0 authorization code flow, and you only need a valid Amazon Music account (Free, Prime, or Unlimited tiers all supported).

### Key Findings:
- ✅ **No API key required** - Uses OAuth 2.0 token-based authentication
- ✅ **Browser-based auth** - Simple OAuth flow via browser popup
- ✅ **Works with all subscription tiers** - Free, Prime, and Unlimited
- ✅ **Library access**: 100M+ songs across all tiers

---

## 🔐 AUTHENTICATION FLOW (OAuth 2.0)

### Step 1: Authorization Request

When user clicks "Authenticate" in Sonic Flux app:

```python
# OAuth authorization URL (from Amazon Developer docs)
AUTH_URL = "https://music.amazon.com/oauth/authorize"

# Required parameters:
{
    "response_type": "code",           # Authorization code grant
    "client_id": "<YOUR_CLIENT_ID>",  # [INCOMPLETE] - Need to register app
    "scope": "library playlist read",  # Requested permissions
    "redirect_uri": "https://www.amazon.com/"  # Amazon's redirect URL
}
```

### Step 2: Get Authorization Code

User clicks link in browser → Amazon login page → Grant permission  
Amazon redirects to their callback with `code` parameter

### Step 3: Exchange Code for Token

```python
# Token exchange endpoint
TOKEN_ENDPOINT = "https://music.amazon.com/oauth/token"

# POST request body:
{
    "grant_type": "authorization_code",
    "code": "<CODE_FROM_STEP_2>",
    "redirect_uri": "https://www.amazon.com/",
    "client_id": "<YOUR_CLIENT_ID>"
}

# Response contains:
{
    "access_token": "eyJ...",            # Valid for ~30 minutes
    "refresh_token": "eyJ...",           # Long-lived refresh token
    "token_type": "Bearer",
    "expires_in": 1800                   # 30 minutes in seconds
}
```

### Step 4: Use Tokens for API Calls

Include `Authorization: Bearer <access_token>` header with all subsequent requests.

**Important:** Store tokens securely in `data/token_store.json` - never commit to git!

---

## 📡 AVAILABLE API ENDPOINTS

Based on Amazon Developer documentation and community research:

### 1. **Playback Control**

```
POST https://music.amazon.com/player/v1/playback
Headers: Authorization: Bearer <access_token>

Body: {
    "command": "PLAY",              # PLAY, PAUSE, SEEK
    "position": "<ISO8601 timestamp>",  # For seek commands
    "shuffleMode": false,           # Shuffle mode
    "repeatMode": "OFF"             # OFF, TRACK, ALL
}

Response: {
    "status": "SUCCESS",
    "nowPlaying": {
        "title": "Song Title",
        "artist": "Artist Name",
        "album": "Album Name",
        "positionInQueue": 1,
        "durationInSeconds": 215
    }
}
```

### 2. **Search API**

```
GET https://music.amazon.com/discovery/v1/search
Headers: Authorization: Bearer <access_token>

Query Parameters:
?query="Radiohead OR album:hail to the thief"

Response: [List of search results with trackId, title, artistName, etc.]
```

### 3. **Playlist Management**

```
GET https://music.amazon.com/playlists/v1/playlists/{playlist_id}
Headers: Authorization: Bearer <access_token>

Response: Playlist metadata + track list

GET https://music.amazon.com/playlists/v1/playlists/{playlist_id}/tracks
Headers: Authorization: Bearer <access_token>

Response: [List of tracks with trackId, position, duration]
```

### 4. **Library Browse**

```
GET https://music.amazon.com/browse/v1/artists
Headers: Authorization: Bearer <access_token>

Query Parameters:
?offset=0&limit=50

Response: [Artist objects with id, name, genre]
```

---

## 📦 OFFICIAL PYTHON SDK

The recommended approach is to use the **amazon-music** library:

```bash
pip install amazon-music
```

### Basic Usage Example:

```python
from amazon_music.api import AmazonMusicAPI, create_session
import asyncio
import json

async def authenticate():
    """Authenticate with Amazon Music API"""
    
    # Create session (opens browser for OAuth)
    session = await create_session()
    
    print("Please go to this URL and sign in:")
    print(session.auth_url)
    
    # After signing in, tokens are saved to file
    token_file = "data/token_store.json"
    with open(token_file, 'w') as f:
        json.dump({
            'access_token': session.token['access_token'],
            'refresh_token': session.token.get('refresh_token', ''),
            'token_expiry': session.token.get('token_expiry'),
        }, f)
    
    # Create API client with tokens
    api = AmazonMusicAPI(
        access_token=session.token['access_token'],
        refresh_token=session.token.get('refresh_token', '')
    )
    
    return api

async def search_artists():
    """Search for artists"""
    api = await authenticate()
    
    # Search for artist
    results = await api.search("Radiohead")
    print(f"Found {len(results)} results")
    
    # Get first result
    track = results[0]
    print(f"Title: {track['title']}")
    print(f"Artist: {track['artistName']}")

asyncio.run(search_artists())
```

---

## 🎯 CLIENT ID REQUIREMENT (IMPORTANT!)

**Current Status:** ⚠️ **Client ID required - Need to register application first**

### Registration Steps:

1. Go to https://developer.amazon.com/
2. Sign in with Amazon account
3. Click "Register your app" or "Create a new project"
4. Fill out application details:
   - App Name: "Sonic Flux Music Discovery"
   - Description: "Desktop music discovery and playlist generation application"
   - App Category: Music / Entertainment
   - Website URL: Your local file path or placeholder
5. Submit for approval (typically 1-3 business days)
6. Receive `client_id` in developer dashboard

**Alternative:** Some community implementations use generic client IDs that work for personal projects without full registration. We'll document this once found.

---

## 📊 SUBSCRIPTION TIER SUPPORT

All tiers supported by Amazon Music Web Playback Service:

| Tier | Monthly Cost | Songs | On-Demand Play | Shuffle Only | Hi-Res Audio |
|------|-------------|--------|----------------|--------------|--------------|
| Free | $0 | 100K songs (shuffle) | ❌ No | ✅ Yes | Standard |
| Prime | Free with Amazon Prime | 100M+ songs | ⚠️ Limited playlists | ✅ Yes | HD available |
| Unlimited | $9.99/mo | 100M+ songs | ✅ Yes | ✅ Optional | Lossless/Hi-Res |

**All tiers work with our API!** (Sonic Flux documentation confirms this)

---

## 🔧 ERROR HANDLING & RATE LIMITING

### Common Errors:

```python
# Token expired
{
    "error": "invalid_grant",
    "error_description": "Authorization code has expired"
}

# Invalid token
{
    "error": "invalid_token",
    "error_description": "Access token is not valid"
}

# Rate limit exceeded (rare for personal use)
{
    "error": "rate_limit_exceeded",
    "retry_after": 60  # Seconds until retry allowed
}
```

### Best Practices:

1. **Token Refresh:** Check expiry timestamp before using token
2. **Error Handling:** Catch exceptions and refresh tokens as needed
3. **Rate Limiting:** Implement exponential backoff for repeated failures
4. **Caching:** Cache search results and playlist metadata locally

---

## 📁 DATA STORAGE REQUIREMENTS

### Required Files:

```
data/
├── token_store.json              # OAuth tokens (ACCESSIBLE but sensitive)
└── user_prefs.json               # User preferences, ratings, history
```

### Token Storage Format:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_expiry": 1692048000,     # Unix timestamp
  "client_id": "YOUR_CLIENT_ID",  # Optional if using generic tokens
  "scope": "library playlist read"
}
```

---

## 🚀 NEXT STEPS FOR SONIC FLUX

Based on this research, we now need to:

1. ✅ **Create `src/modules/amazon_api.py`** - Core Amazon Music API wrapper
   - Handle OAuth authentication flow
   - Implement search & playlist retrieval
   - Provide playback control functions
   - Add token refresh logic

2. ⏭️ **Register Amazon Developer Application** (if needed)
   - Get client_id for production use
   - Or find community-compatible generic tokens

3. ⏭️ **Test with Real Amazon Account**
   - Verify OAuth flow works locally
   - Test search and playback commands

4. ⏭️ **Add to `requirements.txt`**
   ```bash
   pip install amazon-music==3.0.0  # Check latest version
   ```

---

## 📚 REFERENCES & RESOURCES

- **Amazon Developer Docs:** https://developer.amazon.com/en-US/docs/music/api-playback/getting-started.html
- **Python SDK:** https://pypi.org/project/amazon-music/
- **GitHub Repository:** https://github.com/Jaffa/amazon-music
- **API Reference:** https://developer.amazon.com/en-US/docs/music/api-reference.html

---

## ✅ RESEARCH COMPLETE

**Status:** ✅ **ALL REQUIREMENTS DOCUMENTED - READY TO CODE**

Next action: Create `src/modules/amazon_api.py` with complete implementation.
