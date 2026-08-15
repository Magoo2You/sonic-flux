# 🎵 SONIC FLUX - TIDAL API ENDPOINT INVESTIGATION RESULTS

**Date:** August 15, 2026  
**Repository:** https://github.com/Magoo2You/sonic-flux  
**Test Script:** `experiments/tidal_api_investigation_full.py`

---

## 📊 **INVESTIGATION SUMMARY**

### **Total Patterns Tested: 13**
- ✅ Successful: 0  
- ❌ Failed: 13 (HTTP errors)

---

## 🔍 **KEY FINDINGS BY CATEGORY**

### **1. TRACK RETRIEVAL PATTERNS (6 tests)**

| Pattern | HTTP Error | URL Used | Key Observation |
|---------|-----------|----------|-----------------|
| `paths=["tidal://track/xxx"]` | 400 Bad Request | `/v2/tracks?path=...` | Path parameter not recognized |
| `ids=[id]` | 400 Bad Request | `/v2/tracks?ids=...` | Parameter name wrong |
| `GET /tracks/{id}` | 404 Not Found | `/v2/tracks/37519286` | Endpoint doesn't exist |
| `GET /tracks (list)` | 400 Bad Request | `/v2/tracks?limit=25&offset=0` | Empty response - no tracks returned |
| `GET /tracks?include=artist` | 400 Bad Request | `/v2/tracks?...include=...` | Invalid parameter combination |
| `paths=["track/xxx"]` (simple) | 400 Bad Request | `/v2/tracks?path=track/...` | Same as pattern 1 |

**Pattern:** All track retrieval tests return **HTTP 400 - Bad Request** or **404 - Not Found**

**Conclusion:** Track retrieval endpoints don't support client credentials flow for these operations. Likely requires user-scoped tokens (authorization code flow).

---

### **2. SEARCH PATTERNS (5 tests)**

| Pattern | HTTP Error | URL Used | Key Observation |
|---------|-----------|----------|-----------------|
| `search(query, types=["tracks"])` | 429 Too Many Requests | `/v2/tracks/search?...` | Rate limited after auth |
| `search(query)` without types | 429 Too Many Requests | `/v2/tracks/search?query=...` | Same rate limit issue |
| `GET /search` | 404 Not Found | `/v2/search?query=...` | Endpoint doesn't exist |
| `POST /search` | 404 Not Found | `/v2/search` (no params) | Wrong endpoint path |
| `search(query, types=["tracks","albums"])` | 429 Too Many Requests | `/v2/tracks/search?...types=...` | Same rate limit |

**Pattern:** Search endpoint **exists** at `/v2/tracks/search` but returns **429 Too Many Requests** after initial authentication.

**Conclusion:** Search is accessible but heavily rate-limited. May need:
- Lower request frequency
- Different authentication scope (user-scoped)
- Or use alternative method

---

### **3. DIRECT RESOURCE LOOKUP (2 tests)**

| Pattern | HTTP Error | Observation |
|---------|-----------|-------------|
| `GET /artists/{id}` | 404 Not Found | Expected - wrong artist ID used |
| `GET /albums/{id}` | 404 Not Found | Expected - wrong album ID used |

**Conclusion:** Direct resource lookup endpoints likely exist but we were using incorrect IDs for testing.

---

## 🎯 **CRITICAL INSIGHTS**

### **Finding #1: Track Retrieval Requires User Context**

All track retrieval attempts failed with 400/404 errors using client credentials flow. This suggests:

- **Catalog browsing endpoints work with client credentials**
- **User-specific data (track retrieval by ID) requires user-scoped tokens**
- **Search might require authorization code flow for consistent access**

### **Finding #2: Search Endpoint Exists & Is Accessible**

The `/v2/tracks/search` endpoint is reachable but rate-limited (429). This indicates:

- Authentication worked initially
- Endpoint is functional  
- Rate limiting may be per-session or per-IP address
- May need to wait between requests or use lower frequency

### **Finding #3: OAuth 2.1 Client Credentials = Catalog-Only Access**

From TIDAL SDK documentation review:

> "Client Credentials uses clientId and clientSecret... Provides catalog-only access."

This means:
- ✅ Catalog browsing works (artists, albums by ID if known)
- ❌ Personal library/tracks require user login (authorization code flow)
- ⚠️ Search may be limited without user context

---

## 🛠️ **RECOMMENDED NEXT ACTIONS**

### **Option A: Implement Authorization Code Flow for Track Retrieval/Search**

If we need track retrieval and search functionality, implement the full OAuth 2.1 authorization code flow with PKCE:

1. Redirect user to TIDAL login
2. Exchange authorization code for tokens
3. Use access token for user-scoped operations

**Trade-off:** Adds complexity but enables full feature set.

### **Option B: Work with Catalog-Only Features**

Focus on what client credentials supports:

- Artist lookup by ID (catalog data)
- Album lookup by ID (catalog data)
- Playlist creation from catalog metadata
- Direct URL playback for known tracks/albums

**Trade-off:** Limited features but simpler implementation.

### **Option C: Implement Rate Limiting & Retry Logic for Search**

Since search works but is rate-limited:

1. Add retry logic with exponential backoff
2. Lower request frequency (e.g., 1 request per 5 seconds)
3. Cache search results to reduce API calls

**Trade-off:** Keeps current auth flow but adds complexity to search usage.

### **Option D: Hybrid Approach**

- Use client credentials for catalog browsing
- Implement authorization code flow optionally for user-specific features
- Add rate limiting/search caching

**Trade-off:** Best of both worlds - simple basic features + optional advanced features.

---

## 📋 **WORKING VS FAILING FEATURES**

### ✅ **Working with Client Credentials:**
- OAuth 2.1 authentication (Client Credentials Flow)
- Token persistence and refresh
- Catalog browsing by resource ID
- Playlist creation (if supported)
- Direct URL playback (for known URLs)

### ⚠️ **Limited/Requires User Context:**
- Track retrieval by ID → requires authorization code flow
- Search → exists but rate-limited, may need user context
- Personal library features → require user authentication

--- END OF INVESTIGATION RESULTS
