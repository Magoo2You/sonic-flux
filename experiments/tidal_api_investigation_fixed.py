"""
TIDAL API Endpoints Investigation Script - Fixed Version
========================================================
Tests alternative approaches after ensuring authentication works first.
"""

import sys
sys.path.insert(0, r"C:\HermesWiiM\src")

from modules.tidal_api import TidalApi


def load_credentials():
    """Load credentials securely from .env."""
    try:
        import sys
        sys.path.insert(0, r"C:\HermesWiiM\experiments")
        from tidal_api_auth_test import load_credentials_securely
        return load_credentials_securely()
    except Exception as e:
        print(f"⚠️  Failed to load credentials: {e}")
        return None, None


def test_track_retrieval():
    """Test track retrieval with authenticated token."""
    print("=" * 70)
    print("🔍 TIDAL API ENDPOINTS INVESTIGATION - TRACK RETRIEVAL TESTS")
    print("=" * 70)
    
    client_id, client_secret = load_credentials()
    if not client_id or not client_secret:
        return
    
    api = TidalApi(
        client_id=client_id,
        client_secret=client_secret,
        token_store_path=r"C:\HermesWiiM\data\tidal_token_store.json"
    )
    
    # Ensure we have a valid token
    print("\n📌 Ensuring valid authentication token...")
    if not api.has_valid_token():
        print("   📌 Authenticating fresh...")
        token = api.authenticate_client_credentials()
        api.save_token(token)
        print("   ✅ Token authenticated and saved")
    
    # Test 1: Current implementation (paths parameter)
    print("\n--- TEST 1: Current 'paths' parameter format ---")
    try:
        tracks = api.get_tracks(paths=["tidal://track/37519286"])
        print("✅ SUCCESS - paths parameter works")
        print(f"   Retrieved {len(tracks.get('data', []))} track(s)")
    except Exception as e:
        print(f"❌ FAILED with HTTP 400 or similar: {e}")
    
    # Test 2: Using 'ids' parameter instead of 'paths'
    print("\n--- TEST 2: Using 'ids' parameter ---")
    try:
        tracks = api.get_tracks(ids=["37519286"])
        print("✅ SUCCESS - ids parameter works")
        print(f"   Retrieved {len(tracks.get('data', []))} track(s)")
        for track in tracks['data']:
            attrs = track['attributes']
            name = attrs.get('name')
            tid = attrs.get('id')
            print(f"      🎵 {name} (ID: {tid})")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 3: Direct single track endpoint
    print("\n--- TEST 3: Direct single track GET /tracks/{id} ---")
    try:
        track_id = "37519286"
        response = api.get(f"tracks/{track_id}")
        print("✅ SUCCESS - Single track endpoint works")
        attrs = response['data']['attributes'] if 'data' in response else {}
        name = attrs.get('name')
        tid = attrs.get('id')
        print(f"      🎵 {name} (ID: {tid})")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 4: GET tracks list without path parameters
    print("\n--- TEST 4: List tracks with query params ---")
    try:
        tracks = api.get("tracks", params={"limit": 25, "offset": 0})
        print("✅ SUCCESS - Basic tracks list works")
        print(f"   Retrieved {len(tracks.get('data', []))} track(s)")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 5: Tracks with include parameter
    print("\n--- TEST 5: Tracks with include=artist ---")
    try:
        tracks = api.get("tracks", params={
            "limit": 25,
            "offset": 0,
            "include": ["artist"]
        })
        print("✅ SUCCESS - Include parameter works")
        if tracks['data']:
            attrs = tracks['data'][0]['attributes']
            artist_data = tracks['data'][0].get('relationships', {}).get('artist', {})
            artist = artist_data.get('data', {})
            if artist:
                artist_attrs = artist.get('attributes', {})
                print(f"      🎵 {attrs.get('name')}")
                print(f"      👤 Artist: {artist_attrs.get('name', 'Unknown')}")
    except Exception as e:
        print(f"❌ FAILED: {e}")


def test_search():
    """Test search functionality."""
    print("\n" + "=" * 70)
    print("🔍 TIDAL API ENDPOINTS INVESTIGATION - SEARCH TESTS")
    print("=" * 70)
    
    client_id, client_secret = load_credentials()
    if not client_id or not client_secret:
        return
    
    api = TidalApi(
        client_id=client_id,
        client_secret=client_secret,
        token_store_path=r"C:\HermesWiiM\data\tidal_token_store.json"
    )
    
    # Ensure we have a valid token
    if not api.has_valid_token():
        print("   📌 Authenticating fresh...")
        token = api.authenticate_client_credentials()
        api.save_token(token)
        print("   ✅ Token authenticated and saved")
    
    # Test 1: Search with 'types' parameter (current implementation)
    print("\n--- TEST 1: Search with types=['tracks'] ---")
    try:
        results = api.search("Taylor Swift", types=["tracks"], limit=3)
        print("✅ SUCCESS - Search works")
        print(f"   Found {len(results.get('data', []))} tracks")
        for track in results['data'][:2]:
            attrs = track['attributes']
            name = attrs.get('name')
            tid = attrs.get('id')
            print(f"      🎵 {name} (ID: {tid})")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 2: Generic search endpoint
    print("\n--- TEST 2: Generic '/search' endpoint ---")
    try:
        results = api.get("search", params={
            "query": "The Weeknd",
            "limit": 10,
            "offset": 0
        })
        print("✅ SUCCESS - Generic search works")
        if 'data' in results and results['data']:
            for item in results['data'][:3]:
                item_type = item.get('type', 'unknown')
                attrs = item.get('attributes', {})
                name = attrs.get('name')
                tid = attrs.get('id')
                print(f"      {item_type}: {name} (ID: {tid})")
    except Exception as e:
        print(f"❌ FAILED: {e}")


def test_artist_album_lookup():
    """Test direct resource lookup by ID."""
    print("\n" + "=" * 70)
    print("🔍 TIDAL API ENDPOINTS INVESTIGATION - DIRECT LOOKUP")
    print("=" * 70)
    
    client_id, client_secret = load_credentials()
    if not client_id or not client_secret:
        return
    
    api = TidalApi(
        client_id=client_id,
        client_secret=client_secret,
        token_store_path=r"C:\HermesWiiM\data\tidal_token_store.json"
    )
    
    # Ensure we have a valid token
    if not api.has_valid_token():
        print("   📌 Authenticating fresh...")
        token = api.authenticate_client_credentials()
        api.save_token(token)
        print("   ✅ Token authenticated and saved")
    
    # Test artist lookup
    print("\n--- TEST: Artist lookup by ID ---")
    try:
        artist_id = "269408853"  # Taylor Swift (example ID)
        response = api.get(f"artists/{artist_id}")
        attrs = response['data']['attributes'] if 'data' in response else {}
        name = attrs.get('name')
        print(f"✅ Artist found: {name}")
    except Exception as e:
        print(f"⚠️  Not found (expected with wrong ID): {type(e).__name__}")
    
    # Test album lookup  
    print("\n--- TEST: Album lookup by ID ---")
    try:
        album_id = "183962547"  # Example ID
        response = api.get(f"albums/{album_id}")
        attrs = response['data']['attributes'] if 'data' in response else {}
        name = attrs.get('name')
        tid = attrs.get('id')
        print(f"✅ Album found: {name} (ID: {tid})")
    except Exception as e:
        print(f"⚠️  Not found (expected with wrong ID): {type(e).__name__}")


def main():
    """Run all investigation tests."""
    print("\n" + "=" * 70)
    print("🎵 SONIC FLUX - TIDAL API ENDPOINTS INVESTIGATION")
    print("=" * 70)
    
    test_track_retrieval()
    test_search()
    test_artist_album_lookup()
    
    print("\n" + "=" * 70)
    print("📋 INVESTIGATION COMPLETE - REVIEW FINDINGS BELOW:")
    print("=" * 70)
    print("""

After reviewing the output, note:
1. Which parameter formats worked (ids vs paths, query vs implicit)?
2. Which endpoints returned data successfully?
3. Any patterns in error messages that suggest parameter issues?
4. Whether direct resource IDs work for lookup operations?

Common discoveries might include:
- Track retrieval uses 'ids=' instead of 'paths='
- Search endpoint is '/search' not '/tracks/search'
- Some endpoints require specific parameter naming conventions
- Include relationships may need explicit request

Document findings in: investigation_api_endpoints/API_REFERENCE_NOTES.md
    """)


if __name__ == "__main__":
    main()
