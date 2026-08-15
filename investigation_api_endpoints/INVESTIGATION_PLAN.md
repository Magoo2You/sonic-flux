# 🎵 SONIC FLUX - INVESTIGATION PLAN: TIDAL API ENDPOINTS

**Date:** August 15, 2026  
**Repository:** https://github.com/Magoo2You/sonic-flux  
**Investigation Focus:** Fix track retrieval and search HTTP 400 errors

---

## 🎯 **INVESTIGATION OBJECTIVE**

Fix the following endpoints that returned HTTP 400 Bad Request errors:

1. **Track Retrieval by Path**
   - Current: `api.get_tracks(paths=["tidal://track/xxx"])`
   - Error: `HTTP 400 - Bad Request`

2. **Search Functionality**
   - Current: `api.search("Taylor Swift", types=["tracks"], limit=3)`
   - Error: `HTTP 400 - Bad Request`

---

## 📋 **INVESTIGATION STEPS**

### **Step 1: Review API Reference Documentation**

Visit these pages and extract endpoint details:

1. **Main API Reference Index:** `https://developer.tidal.com/apiref`
   - Extract all track-related endpoints
   - Document parameter requirements
   - Note authentication scope notes

2. **Tracks Resource:** Look for `/tracks` endpoint documentation
   - GET `/v2/tracks` (list tracks)
   - GET `/v2/tracks/{id}` (single track)
   - Required vs optional parameters

3. **Search Resource:** Look for search functionality
   - POST `/v2/search` or GET `/v2/tracks/search`
   - Query parameter names (`q` vs `query`)
   - Filter options (`types`, `limit`, `offset`)

4. **Authentication Requirements**
   - Which endpoints require user-scoped tokens?
   - Which work with client credentials (catalog-only)?

---

### **Step 2: Test Alternative Implementation Patterns**

After reviewing documentation, test these alternative approaches:

#### **Alternative 1: Use `ids` parameter instead of `paths`**
```python
# Current (fails):
api.get_tracks(paths=["tidal://track/37519286"])

# Try this:
api.get_tracks(ids=["37519286"])  # Just the ID number
```

#### **Alternative 2: Direct single track endpoint**
```python
api.get(f"tracks/{track_id}")  # Single track by ID
```

#### **Alternative 3: Raw GET request for tracks list**
```python
params = {
    "limit": 25,
    "offset": 0
}
api.get("tracks", params=params)
```

#### **Alternative 4: Check for `include` parameter requirement**
Some endpoints may require explicit relationship loading.

---

### **Step 3: Verify Authentication Scopes**

Check if client credentials flow has limitations:

1. **Review API docs for scope requirements:**
   - Does search endpoint specifically list "user-scoped" as requirement?
   - Are there any "requires user authentication" markers?

2. **If search requires user context:**
   - Implement authorization code flow for search operations
   - Use client credentials only for catalog browsing endpoints

---

### **Step 4: Test with Known Valid Resource URLs**

Get real track IDs from TIDAL website or other sources:

1. Visit `https://listen.tidal.com/` and find a popular track (e.g., "As It Was" by Harry Styles)
2. Copy the track ID from URL
3. Test retrieval with that exact ID
4. Compare response structure with API spec examples

---

## 🔧 **POTENTIAL FIXES BASED ON COMMON ISSUES**

### **Issue: Wrong Endpoint Path**

**Fix:** Update endpoint paths in `TidalApi.get()` method.

**Example fix:**
```python
# Current (may be wrong):
self.get("tracks", params=params)

# Fix if needed:
self.get("/v2/tracks", params=params)  # Absolute path
```

---

### **Issue: Wrong Parameter Names**

**Fix:** Adjust parameter naming to match API spec.

**Example fix:**
```python
# Current:
api.get_tracks(paths=["tidal://track/xxx"])

# Fix if needed:
api.get_tracks(ids=["xxx"], limit=25)  # Use ids instead of paths
```

---

### **Issue: Search Endpoint Location**

**Fix:** Update search to use correct endpoint.

**Example fix:**
```python
# Current (may be wrong):
self.get("tracks/search", params=params)

# Fix if needed:
self.post("search", data={"query": q, "types": types})  # POST instead of GET
```

---

### **Issue: Missing Required Parameters**

**Fix:** Add mandatory parameters to requests.

**Example fix:**
```python
params = {
    "limit": 25,
    "offset": 0,
    "include": ["artist"],  # May be required
    "fields": "*"           # Include all fields
}
```

---

## 📁 **INVESTIGATION WORKSPACE FILES TO CREATE**

### **1. `investigation_api_endpoints/API_REFERENCE_NOTES.md`**
- Extracted endpoint paths from API docs
- Parameter requirements table
- Authentication scope notes

### **2. `investigation_api_endpoints/TEST_RESULTS_ENDPOINTS.md`**
- Test outcomes for each alternative approach
- Which parameters work/not work
- Response structure examples

### **3. `investigation_api_endpoints/FINAL_SOLUTION.md`**
- Implemented fixes
- Updated code snippets
- Testing confirmation

---

## 🎯 **PRIORITIZED INVESTIGATION ORDER**

1. **Review API Reference Pages** (30 mins)
   - Extract exact endpoint paths
   - Document parameter requirements
   
2. **Implement Alternative Patterns** (45 mins)
   - Test `ids=` instead of `paths=`
   - Test direct `/tracks/{id}` endpoint
   - Try search with POST method

3. **Test with Real Track IDs** (15 mins)
   - Get valid track from TIDAL website
   - Verify retrieval works
   - Document response structure

4. **Update Module with Fixes** (30 mins)
   - Modify `TidalApi.get_tracks()`
   - Modify `TidalApi.search()`
   - Add documentation comments

--- END OF INVESTIGATION PLAN
