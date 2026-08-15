# 🎵 SONIC FLUX - TIDAL API FULL SPECIFICATION
## Complete JSON:API v2 Documentation

**Date:** August 15, 2026  
**Repository:** https://github.com/Magoo2You/sonic-flux  
**Spec Version:** 1.10.100 (OAS 3.0)  
**Tier:** Third Party - Dev (Production: @url:`https://openapi.tidal.com/v2`)

---

## 📋 **CORE API CHARACTERISTICS**

### **JSON:API Compliance**
- All endpoints exchange `application/vnd.api+json` documents per JSON:API spec
- Resource objects with attributes and relationships
- Compound documents via `include` parameter
- Standard error objects

### **Authentication & Authorization**

#### **Token Endpoints:**

1. **Client Credentials Flow (Server-to-Server):**
   - URL: `https://auth.tidal.com/v1/oauth2/token`
   - Use case: Service accounts, background tasks
   - Scopes are implicit

2. **Authorization Code + PKCE Flow (User Context):**
   - Authorize URL: `https://login.tidal.com/authorize`
   - Required for accessing private user data
   - Need user consent for scopes

#### **Security Model:**

- Every request requires OAuth 2.0 access token in `Authorization: Bearer` header
- Fields unauthorized to read are **redacted** (not errors)
- Resources without access behave as if they don't exist
- Scopes protect private user data

---

## 📝 **RESPONSE HANDLING GUIDELINES**

### **Enums — Forward Compatible**
- New values can be added to any enum at any time
- Treat unknown values as forward-compatible, NOT errors

### **IDs — Opaque Strings**
- Never parse, construct, or infer meaning from IDs
- Treat all IDs as black-box identifiers

### **Formats — Standardized**
- Dates/times/durations: ISO 8601 (e.g., `2024-05-01T12:00:00Z`, `PT3M5S`)
- Countries: ISO 3166-1 alpha-2
- Languages: BCP 47
- Currencies: ISO 4217
- Colors: Six-digit hex

---

## 🔗 **RELATIONSHIPS & INCLUDES**

### **Relationships on Request**
- Relationships returned only when requested in `include`
- Relationship not requested = absent from response (NOT empty)
- Full relationship set documented in resource schema

### **Include Parameter**
```
?include=<comma-separated list of dot-separated paths>
# Example: ?include=coverArt,artists.profileArt
```

- Nested path automatically embeds intermediate resources
- `artists.profileArt` includes artists AND their profile art
- Always relative to request's root resource
- Never changes primary data; related resources added to `included`

### **Include Validation**
- Invalid paths rejected with 400
- Path depth limited (default: 3 levels)
- Total distinct resources limited (default: 10)
- Exceeding limits rejected with 400, error states effective limit

---

## 🗂️ **FILTERING, SORTING & PAGINATION**

### **Filtering**
```
filter[<member>]=value
```
- Filters collections
- Each endpoint documents available filters
- Most collections require at least one filter

### **Sorting**
```
sort=<member> (ascending)
sort=-<member> (descending)
# Example: sort=-addedAt
```
- Members relative to resources being returned

### **Pagination — Cursor-Based**
- Responses carry `links.self`
- While more pages exist: `links.next` with opaque page[cursor]
- Follow `next` until absent
- NO offset or total-page parameters
- Collection sizes appear as `meta.total` (may be approximate)

---

## 🔧 **TYPE QUALIFIERS**

### **Scoped Access**
```
?include=items.tracks:albums
```

- Path segment prefixed with concrete type scopes which type's member is accessed
- Playlist's items are tracks or videos
- Qualifiers scope member access — never filter which resources appear
- Can be chained

### **Filter/Sort on Relationships**
- Same syntax applies where supported
- Qualified member listed among documented filters/sort values
- Follows JSON:API proposal json-api#1695

---

## 📤 **MUTATIONS**

### **Partial Updates — Nullable Attributes**
Three wire states for nullable attributes:
1. **Omission** → leaves current value unchanged
2. **Explicit null** → clears attribute
3. **Concrete value** → updates attribute

### **Idempotency-Key Header**
- Required on every mutation
- Same key + payload within 1 hour → replay original response
- Retry while processing → 409 Conflict
- Same key + different payload → 422 Unprocessable Entity

### **After Write Behavior**
- Your subsequent reads reflect change immediately
- Other clients may observe with delay

---

## 🔄 **MEDIA RESOURCE REPLACEMENTS (BETA - Internal Only)**

Media resources can become unavailable due to licensing changes.

### **Default Behavior**
- Returns original identifiers stored in collection
- Keeps ordinary reads predictable and consistent

### **Replacement Relationship**
```
GET /playlists/{id}?include=items&replaceMedia=items
```

- Inspect `meta.replacement` field
- Values: `ORIGINAL`, `REPLACED`, or `NOT_REPLACED`
- Replacement best effort — not always available

### **Applying Replacements**
```
GET /playlists/{id}?include=items&replaceMedia=items
```

- Substitutes applicable replacements directly
- Preserves relationship order and metadata

---

## 📦 **COMPRESSION**

- Responses gzip-compressed when request includes `Accept-Encoding: gzip`
- Applies to bodies over 2 KB

---

## ⚠️ **DEPRECATION POLICY**

- Deprecated endpoints/parameters/fields marked with replacement noted
- Keep working for at least 6 months after marking
- Removed once replacement generally available

---

## 📜 **TERMS OF SERVICE**

- TIDAL Developer - Discussions
- TIDAL Developer - Documentation  
- Access Tier information available

---

## 📊 **RESOURCE ENDPOINTS - COMPLETE LIST**

### **Albums**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /albums | Get multiple albums |
| GET | /albums/{id} | Get single album |
| GET | /albums/{id}/relationships/artists | Get artists (to-many) |
| GET | /albums/{id}/relationships/coverArt | Get coverArt (to-many) |
| GET | /albums/{id}/relationships/items | Get items (to-many) |
| GET | /albums/{id}/relationships/owners | Get owners (to-many) |
| GET | /albums/{id}/relationships/providers | Get providers (to-many) |
| GET | /albums/{id}/relationships/similarAlbums | Get similarAlbums (to-many) |
| GET | /albums/{id}/relationships/usageRules | Get usageRules (to-one) |

### **Artist Roles**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /artistRoles/{id} | Get single artistRole |

### **Artists**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /artists | Get multiple artists |
| GET | /artists/{id} | Get single artist |
| GET | /artists/{id}/relationships/albums | Get albums (to-many) |
| GET | /artists/{id}/relationships/biography | Get biography (to-one) |
| GET | /artists/{id}/relationships/owners | Get owners (to-many) |
| GET | /artists/{id}/relationships/profileArt | Get profileArt (to-many) |
| GET | /artists/{id}/relationships/radio | Get radio (to-many) |
| GET | /artists/{id}/relationships/roles | Get roles (to-many) |
| GET | /artists/{id}/relationships/similarArtists | Get similarArtists (to-many) |
| GET | /artists/{id}/relationships/trackProviders | Get trackProviders (to-many) |
| GET | /artists/{id}/relationships/tracks | Get tracks (to-many) |
| GET | /artists/{id}/relationships/videos | Get videos (to-many) |

### **Artworks**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /artworks | Get multiple artworks |
| GET | /artworks/{id} | Get single artwork |
| GET | /artworks/{id}/relationships/owners | Get owners (to-many) |

### **Playlists**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /playlists | Get multiple playlists |
| POST | /playlists | Create single playlist |
| DELETE | /playlists/{id} | Delete single playlist |
| GET | /playlists/{id} | Get single playlist |
| PATCH | /playlists/{id} | Update single playlist |
| GET | /playlists/{id}/relationships/collaboratorProfiles | Get collaboratorProfiles (to-many) |
| GET | /playlists/{id}/relationships/collaborators | Get collaborators (to-many) |
| GET | /playlists/{id}/relationships/coverArt | Get coverArt (to-many) |
| DELETE | /playlists/{id}/relationships/items | Delete from items (to-many) |
| GET | /playlists/{id}/relationships/items | Get items (to-many) |
| PATCH | /playlists/{id}/relationships/items | Update items (to-many) |
| POST | /playlists/{id}/relationships/items | Add to items (to-many) |
| GET | /playlists/{id}/relationships/ownerProfiles | Get ownerProfiles (to-many) |
| GET | /playlists/{id}/relationships/owners | Get owners (to-many) |

### **Providers**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /providers/{id} | Get single provider |

### **Search Results**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /searchResults | Get search results by query |
| GET | /searchResults/{id}/relationships/albums | Get albums (to-many) |
| GET | /searchResults/{id}/relationships/artists | Get artists (to-many) |
| GET | /searchResults/{id}/relationships/playlists | Get playlists (to-many) |
| GET | /searchResults/{id}/relationships/topHits | Get topHits (to-many) |
| GET | /searchResults/{id}/relationships/tracks | Get tracks (to-many) |
| GET | /searchResults/{id}/relationships/videos | Get videos (to-many) |

### **Search Suggestions**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /searchSuggestions | Get autocomplete suggestions by query |
| GET | /searchSuggestions/{id}/relationships/directHits | Get directHits (to-many) |

### **Track Manifests**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /trackManifests/{id} | Get single track manifest |

### **Tracks**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /tracks | Get multiple tracks |
| GET | /tracks/{id} | Get single track |
| GET | /tracks/{id}/relationships/albums | Get albums (to-many) |
| GET | /tracks/{id}/relationships/artists | Get artists (to-many) |
| GET | /tracks/{id}/relationships/owners | Get owners (to-many) |
| GET | /tracks/{id}/relationships/providers | Get providers (to-many) |
| GET | /tracks/{id}/relationships/radio | Get radio (to-many) |
| GET | /tracks/{id}/relationships/similarTracks | Get similarTracks (to-many) |
| GET | /tracks/{id}/relationships/sourceFile | Get sourceFile (to-one) |
| GET | /tracks/{id}/relationships/usageRules | Get usageRules (to-one) |

### **Usage Rules**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /usageRules/{id} | Get single usage rule |

### **User Collections (Dedicated Resources)**

#### **User Collection Albums**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /userCollectionAlbums/{id} | Get single user collection album |
| DELETE | /userCollectionAlbums/{id}/relationships/items | Delete items |
| GET | /userCollectionAlbums/{id}/relationships/items | Get items |
| POST | /userCollectionAlbums/{id}/relationships/items | Add items |
| GET | /userCollectionAlbums/{id}/relationships/owners | Get owners |

#### **User Collection Artists**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /userCollectionArtists/{id} | Get single user collection artist |
| DELETE | /userCollectionArtists/{id}/relationships/items | Delete items |
| GET | /userCollectionArtists/{id}/relationships/items | Get items |
| POST | /userCollectionArtists/{id}/relationships/items | Add items |
| GET | /userCollectionArtists/{id}/relationships/owners | Get owners |

#### **User Collection Playlists**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /userCollectionPlaylists/{id} | Get single user collection playlist |
| DELETE | /userCollectionPlaylists/{id}/relationships/items | Delete items |
| GET | /userCollectionPlaylists/{id}/relationships/items | Get items |
| POST | /userCollectionPlaylists/{id}/relationships/items | Add items |
| GET | /userCollectionPlaylists/{id}/relationships/owners | Get owners |

#### **User Collection Tracks**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /userCollectionTracks/{id} | Get single user collection track |
| DELETE | /userCollectionTracks/{id}/relationships/items | Delete items |
| GET | /userCollectionTracks/{id}/relationships/items | Get items |
| POST | /userCollectionTracks/{id}/relationships/items | Add items |
| GET | /userCollectionTracks/{id}/relationships/owners | Get owners |

#### **User Collection Videos**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /userCollectionVideos/{id} | Get single user collection video |
| DELETE | /userCollectionVideos/{id}/relationships/items | Delete items |
| GET | /userCollectionVideos/{id}/relationships/items | Get items |
| POST | /userCollectionVideos/{id}/relationships/items | Add items |
| GET | /userCollectionVideos/{id}/relationships/owners | Get owners |

### **User Collections (Deprecated - Use Dedicated Resources)**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /userCollections/{id} | Get single user collection |
| DELETE | /userCollections/{id}/relationships/* | Delete from relationships |
| POST | /userCollections/{id}/relationships/* | Add to relationships |

### **User Daily Mixes**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /userDailyMixes/{id} | Get single user daily mix |
| GET | /userDailyMixes/{id}/relationships/items | Get items |

### **User Discovery Mixes**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /userDiscoveryMixes/{id} | Get single user discovery mix |
| GET | /userDiscoveryMixes/{id}/relationships/items | Get items |

### **User New Release Mixes**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /userNewReleaseMixes/{id} | Get single user new release mix |
| GET | /userNewReleaseMixes/{id}/relationships/items | Get items |

### **User Recommendations (Deprecated)**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /userRecommendations/{id} | Get single user recommendation |
| GET | /userRecommendations/{id}/relationships/* | Get relationships |

### **Users**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /users/{id} | Get single user |

### **Video Manifests**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /videoManifests/{id} | Get single video manifest |

### **Videos**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /videos | Get multiple videos |
| GET | /videos/{id} | Get single video |
| GET | /videos/{id}/relationships/albums | Get albums (to-many) |
| GET | /videos/{id}/relationships/artists | Get artists (to-many) |
| GET | /videos/{id}/relationships/providers | Get providers (to-many) |
| GET | /videos/{id}/relationships/thumbnailArt | Get thumbnailArt (to-many) |
| GET | /videos/{id}/relationships/usageRules | Get usageRules (to-one) |

---

## 🎯 **KEY INTEGRATION NOTES FOR SONIC FLUX**

### **1. User Playlist Management**
- Use `/playlists` endpoints to create/manage user playlists
- `POST /playlists/{id}/relationships/items` for adding tracks
- `DELETE /playlists/{id}/relationships/items` for removing tracks
- Track and video types can be distinguished with type qualifiers

### **2. User Library Access**
- `/userCollectionTracks/{id}` - favorited tracks
- `/userCollectionAlbums/{id}` - favorited albums  
- `/userCollectionArtists/{id}` - favorited artists
- Each collection supports add/delete operations

### **3. Search Functionality**
- `/searchResults` for general search across all content types
- `/searchSuggestions` for autocomplete features
- Both support relationships via `include` parameter

### **4. Track Playback Manifests**
- `/trackManifests/{id}` provides streaming URIs and format details
- Essential for playback queue building

### **5. Playlist Manipulation**
- Full CRUD operations available on playlists
- Bulk add/remove via items relationship endpoints
- Cover art support for playlist customization

---

## ✅ **NEXT STEPS FOR DEVELOPMENT**

1. **OAuth 2.0 Setup** - Implement both client-credentials and auth-code flows
2. **Track Fetching** - Build functions to get user library and search results
3. **Playlist Management** - Create playlist add/remove operations
4. **WiiM Integration** - Connect TIDAL tracks with WiiM preset launching
5. **Error Handling** - Implement proper handling of redacted fields

---

## 🔐 **AUTHENTICATION FLOW RECOMMENDATION**

For Sonic Flux with user context:

```python
# 1. Build authorization URL with PKCE
auth_url = f"https://login.tidal.com/authorize?" \
            f"response_type=code&" \
            f"client_id={tidal_client_id}&" \
            f"redirect_uri={redirect_uri}&" \
            f"scope=read-privately-owned-content playlist-manipulation " \
            f"code_challenge={pkce_challenge}"

# 2. User consents, receives code

# 3. Exchange code for token at https://auth.tidal.com/v1/oauth2/token

# 4. Use token in Bearer header for all API calls
```

**Scopes to consider:**
- `read-privately-owned-content` - Access user collections
- `playlist-manipulation` - Create/update playlists  
- Additional scopes as needed for specific features

---

**Ready for implementation!** 🎵🚀
