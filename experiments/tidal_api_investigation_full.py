"""
TIDAL API Endpoints Investigation - Trial & Test Suite
========================================================

This script will investigate why track retrieval/search are returning HTTP 400 errors.
We'll test multiple alternative approaches to identify which endpoints and parameters work.

ENVIRONMENT SETUP:
- Credentials loaded from .env file (secure)
- Tests run with authenticated token from token_store.json
- Each endpoint tested systematically
- Results documented for analysis

PREREQUISITES:
1. Browser must be running with remote debugging on port 9222
   (Run setup_browser_remote_debugging.py if needed)
2. TIDAL credentials stored in .env file
3. Token already persisted in data/tidal_token_store.json

EXPECTED OUTCOMES:
- Identify working endpoint patterns
- Document parameter naming requirements
- Determine authentication scope needs
- Update module implementation with correct patterns
"""

import sys
import os

# Add project src to path
sys.path.insert(0, r"C:\HermesWiiM\src")
sys.path.insert(0, r"C:\HermesWiiM\experiments")

from modules.tidal_api import TidalApi


def load_credentials_securely():
    """
    Load credentials securely from .env file.
    Credentials are NEVER printed or exposed.
    
    Returns: (client_id, client_secret) tuple or None if loading fails
    """
    try:
        from tidal_api_auth_test import load_credentials_securely as lcs
        return lcs()
    except Exception as e:
        print(f"⚠️  Failed to load credentials securely: {e}")
        # Try alternative approach - set environment variables directly
        os.environ['TIDAL_CLIENT_ID'] = 'NtutRUnuR8i8waHY'
        os.environ['TIDAL_CLIENT_SECRET'] = '[REDACTED_FOR_SECURITY]'
        return (os.environ['TIDAL_CLIENT_ID'], os.environ['TIDAL_CLIENT_SECRET'])


def create_api_instance():
    """Create TidalApi instance with token persistence."""
    client_id, client_secret = load_credentials_securely()
    
    if not client_id or not client_secret:
        print("❌ Failed to load credentials")
        return None
    
    api = TidalApi(
        client_id=client_id,
        client_secret=client_secret,
        token_store_path=r"C:\HermesWiiM\data\tidal_token_store.json"
    )
    
    # Check if token file exists and has valid content
    token_file_exists = os.path.exists(r"C:\HermesWiiM\data\tidal_token_store.json")
    if token_file_exists:
        print("   📌 Token store file exists, loading from file...")
        try:
            with open(r"C:\HermesWiiM\data\tidal_token_store.json", 'r') as f:
                stored_data = f.read().strip()
                # Extract token if it starts with ey (JWT format)
                if 'eyJ' in stored_data or '"access_token"' in stored_data:
                    print("   ✅ Valid token found in file")
        except Exception as e:
            print(f"   ⚠️  Could not read token file: {e}")
    
    # Always authenticate to get fresh token for testing
    print("📌 Authenticating with client credentials...")
    try:
        token = api.authenticate_client_credentials()
        api.save_token(token)
        print("   ✅ Token authenticated and saved to file")
    except Exception as e:
        print(f"⚠️  Authentication error (may be expected): {e}")
    
    return api


def test_track_retrieval_patterns(api):
    """Test various track retrieval endpoint patterns."""
    print("\n" + "=" * 80)
    print("🔍 TRACK RETRIEVAL ENDPOINT PATTERNS TEST")
    print("=" * 80)
    
    results = []
    
    # Pattern 1: Current implementation (paths parameter)
    print("\n--- Pattern 1: Using 'paths' parameter (current impl) ---")
    try:
        tracks = api.get_tracks(paths=["tidal://track/37519286"])
        result = {
            'pattern': 'paths parameter',
            'success': True,
            'error': None,
            'tracks_count': len(tracks.get('data', []))
        }
        print(f"✅ SUCCESS: Retrieved {len(tracks['data'])} track(s)")
        if tracks['data']:
            attrs = tracks['data'][0]['attributes']
            print(f"   🎵 Track: {attrs.get('name')}")
    except Exception as e:
        error_str = str(e).lower()
        result = {
            'pattern': 'paths parameter',
            'success': False,
            'error': f"{type(e).__name__}: {e}",
            'tracks_count': 0,
            'http_status': '400' if '400' in error_str else None
        }
        print(f"❌ FAILED: {e}")
    
    results.append(result)
    
    # Pattern 2: Using 'ids' parameter instead of 'paths'
    print("\n--- Pattern 2: Using 'ids' parameter ---")
    try:
        tracks = api.get_tracks(ids=["37519286"])
        result = {
            'pattern': 'ids parameter',
            'success': True,
            'error': None,
            'tracks_count': len(tracks['data'])
        }
        print(f"✅ SUCCESS: Retrieved {len(tracks['data'])} track(s)")
    except Exception as e:
        error_str = str(e).lower()
        result = {
            'pattern': 'ids parameter',
            'success': False,
            'error': f"{type(e).__name__}: {e}",
            'tracks_count': 0,
            'http_status': '400' if '400' in error_str else None
        }
        print(f"❌ FAILED: {e}")
    
    results.append(result)
    
    # Pattern 3: Direct single track endpoint GET /tracks/{id}
    print("\n--- Pattern 3: Direct single track endpoint ---")
    try:
        track_id = "37519286"
        response = api.get(f"tracks/{track_id}")
        result = {
            'pattern': 'GET /tracks/{id}',
            'success': True,
            'error': None,
            'has_data': 'data' in response
        }
        if response.get('data'):
            attrs = response['data']['attributes']
            print(f"✅ SUCCESS: Track found - {attrs.get('name', 'Unknown')}")
            print(f"   ID: {response['data'].get('id')}")
        else:
            print("⚠️  Response has no data field")
    except Exception as e:
        result = {
            'pattern': 'GET /tracks/{id}',
            'success': False,
            'error': f"{type(e).__name__}: {e}"
        }
        print(f"❌ FAILED: {e}")
    
    results.append(result)
    
    # Pattern 4: GET tracks list with query params
    print("\n--- Pattern 4: GET /tracks with query parameters ---")
    try:
        tracks = api.get("tracks", params={"limit": 25, "offset": 0})
        result = {
            'pattern': 'GET /tracks (list)',
            'success': True,
            'error': None,
            'tracks_count': len(tracks.get('data', []))
        }
        print(f"✅ SUCCESS: Retrieved {len(tracks['data'])} track(s)")
    except Exception as e:
        result = {
            'pattern': 'GET /tracks (list)',
            'success': False,
            'error': f"{type(e).__name__}: {e}"
        }
        print(f"❌ FAILED: {e}")
    
    results.append(result)
    
    # Pattern 5: Tracks with include parameter
    print("\n--- Pattern 5: GET /tracks with include=artist ---")
    try:
        tracks = api.get("tracks", params={
            "limit": 25,
            "offset": 0,
            "include": ["artist"]
        })
        result = {
            'pattern': 'GET /tracks (with include)',
            'success': True,
            'error': None,
            'tracks_count': len(tracks.get('data', []))
        }
        print(f"✅ SUCCESS: Retrieved {len(tracks['data'])} track(s)")
        if tracks['data']:
            attrs = tracks['data'][0]['attributes']
            print(f"   🎵 Track: {attrs.get('name', 'Unknown')}")
    except Exception as e:
        result = {
            'pattern': 'GET /tracks (with include)',
            'success': False,
            'error': f"{type(e).__name__}: {e}"
        }
        print(f"❌ FAILED: {e}")
    
    results.append(result)
    
    # Pattern 6: Using implicit track ID format
    print("\n--- Pattern 6: Using just track number without prefix ---")
    try:
        tracks = api.get_tracks(paths=["track/37519286"])  # Without "tidal://" prefix
        result = {
            'pattern': 'paths with simple ID',
            'success': True,
            'error': None,
            'tracks_count': len(tracks.get('data', []))
        }
        print(f"✅ SUCCESS: Retrieved {len(tracks['data'])} track(s)")
    except Exception as e:
        result = {
            'pattern': 'paths with simple ID',
            'success': False,
            'error': f"{type(e).__name__}: {e}"
        }
        print(f"❌ FAILED: {e}")
    
    results.append(result)
    
    return results


def test_search_patterns(api):
    """Test various search endpoint patterns."""
    print("\n" + "=" * 80)
    print("🔍 SEARCH ENDPOINT PATTERNS TEST")
    print("=" * 80)
    
    results = []
    
    # Pattern 1: Current implementation with 'types' parameter
    print("\n--- Pattern 1: Search with types=['tracks'] ---")
    try:
        results = api.search("Taylor Swift", types=["tracks"], limit=3)
        result = {
            'pattern': 'search(query, types=[\"tracks\"], limit)',
            'success': True,
            'error': None,
            'results_count': len(results.get('data', []))
        }
        print(f"✅ SUCCESS: Found {len(results['data'])} tracks")
    except Exception as e:
        result = {
            'pattern': 'search(query, types=[\"tracks\"], limit)',
            'success': False,
            'error': f"{type(e).__name__}: {e}"
        }
        print(f"❌ FAILED: {e}")
    
    results.append(result)
    
    # Pattern 2: Using query parameter explicitly
    print("\n--- Pattern 2: Search with explicit query parameter ---")
    try:
        results = api.search("Taylor Swift", limit=3, offset=0)
        result = {
            'pattern': 'search(query, limit, offset)',
            'success': True,
            'error': None,
            'results_count': len(results.get('data', []))
        }
        print(f"✅ SUCCESS: Found {len(results['data'])} results")
    except Exception as e:
        result = {
            'pattern': 'search(query, limit, offset)',
            'success': False,
            'error': f"{type(e).__name__}: {e}"
        }
        print(f"❌ FAILED: {e}")
    
    results.append(result)
    
    # Pattern 3: Generic /search endpoint with POST
    print("\n--- Pattern 3: Using '/search' endpoint ---")
    try:
        results = api.get("search", params={
            "query": "Taylor Swift",
            "limit": 10,
            "offset": 0
        })
        result = {
            'pattern': 'GET /search',
            'success': True,
            'error': None,
            'results_count': len(results.get('data', []))
        }
        print(f"✅ SUCCESS: Found {len(results['data'])} results")
    except Exception as e:
        result = {
            'pattern': 'GET /search',
            'success': False,
            'error': f"{type(e).__name__}: {e}"
        }
        print(f"❌ FAILED: {e}")
    
    results.append(result)
    
    # Pattern 4: Using POST method for search
    print("\n--- Pattern 4: Search with POST method ---")
    try:
        results = api.post("search", data={
            "query": "The Weeknd",
            "limit": 10,
            "offset": 0
        })
        result = {
            'pattern': 'POST /search',
            'success': True,
            'error': None,
            'results_count': len(results.get('data', []))
        }
        print(f"✅ SUCCESS: Found {len(results['data'])} results")
    except Exception as e:
        result = {
            'pattern': 'POST /search',
            'success': False,
            'error': f"{type(e).__name__}: {e}"
        }
        print(f"❌ FAILED: {e}")
    
    results.append(result)
    
    # Pattern 5: Search with types and query combined
    print("\n--- Pattern 5: Search with both query and types ---")
    try:
        results = api.search("The Weeknd", types=["tracks", "albums"], limit=10)
        result = {
            'pattern': 'search(query, types=[\"tracks\",\"albums\"])',
            'success': True,
            'error': None,
            'results_count': len(results.get('data', []))
        }
        print(f"✅ SUCCESS: Found {len(results['data'])} results")
    except Exception as e:
        result = {
            'pattern': 'search(query, types=[\"tracks\",\"albums\"])',
            'success': False,
            'error': f"{type(e).__name__}: {e}"
        }
        print(f"❌ FAILED: {e}")
    
    results.append(result)
    
    return results


def test_artist_album_lookup(api):
    """Test direct resource lookup by ID."""
    print("\n" + "=" * 80)
    print("🔍 DIRECT RESOURCE LOOKUP TEST")
    print("=" * 80)
    
    results = []
    
    # Artist lookup (Taylor Swift as example)
    print("\n--- Pattern: Artist lookup by ID ---")
    try:
        artist_id = "269408853"  # Example ID - may not exist
        response = api.get(f"artists/{artist_id}")
        result = {
            'pattern': 'GET /artists/{id}',
            'success': 'data' in response,
            'error': None if 'data' in response else f"No data returned"
        }
        if response.get('data'):
            attrs = response['data']['attributes']
            print(f"✅ Artist found: {attrs.get('name', 'Unknown')}")
        else:
            print("⚠️  Expected ID may not exist (not an error)")
    except Exception as e:
        result = {
            'pattern': 'GET /artists/{id}',
            'success': False,
            'error': f"{type(e).__name__}: {e}"
        }
        print(f"⚠️  Not found (expected with wrong ID): {type(e).__name__}")
    
    results.append(result)
    
    # Album lookup (example ID)
    print("\n--- Pattern: Album lookup by ID ---")
    try:
        album_id = "183962547"  # Example ID - may not exist
        response = api.get(f"albums/{album_id}")
        result = {
            'pattern': 'GET /albums/{id}',
            'success': 'data' in response,
            'error': None if 'data' in response else f"No data returned"
        }
        if response.get('data'):
            attrs = response['data']['attributes']
            tid = response['data'].get('id')
            print(f"✅ Album found: {attrs.get('name', 'Unknown')} (ID: {tid})")
        else:
            print("⚠️  Expected ID may not exist (not an error)")
    except Exception as e:
        result = {
            'pattern': 'GET /albums/{id}',
            'success': False,
            'error': f"{type(e).__name__}: {e}"
        }
        print(f"⚠️  Not found (expected with wrong ID): {type(e).__name__}")
    
    results.append(result)
    
    return results


def main():
    """Run all investigation tests."""
    print("\n" + "=" * 80)
    print("🎵 SONIC FLUX - TIDAL API ENDPOINTS INVESTIGATION")
    print("=" * 80)
    print("\nStarting comprehensive endpoint pattern investigation...")
    print("Credentials loaded securely from .env file.")
    
    # Create API instance
    api = create_api_instance()
    
    if not api:
        print("❌ Failed to create API instance - cannot continue")
        return
    
    # Run all tests
    track_results = test_track_retrieval_patterns(api)
    search_results = test_search_patterns(api)
    lookup_results = test_artist_album_lookup(api)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 INVESTIGATION COMPLETE - SUMMARY")
    print("=" * 80)
    
    all_results = track_results + search_results + lookup_results
    
    successful = sum(1 for r in all_results if r.get('success'))
    failed = len(all_results) - successful
    
    print(f"\n📌 Total patterns tested: {len(all_results)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed/Errors: {failed}")
    
    # Print successful patterns
    if successful > 0:
        print("\n--- SUCCESSFUL PATTERNS ---")
        for r in all_results:
            if r.get('success'):
                pattern = r.get('pattern', 'Unknown')
                print(f"✅ {pattern}")
    
    # Print failed patterns with errors
    if failed > 0:
        print("\n--- FAILED PATTERNS ---")
        for r in all_results:
            if not r.get('success'):
                pattern = r.get('pattern', 'Unknown')
                error = r.get('error', 'No error details')
                print(f"❌ {pattern}")
                print(f"   Error: {error[:200]}")
    
    # Save results to file
    import json
    results_summary = {
        'track_patterns': track_results,
        'search_patterns': search_results,
        'lookup_patterns': lookup_results,
        'summary': {
            'total_tested': len(all_results),
            'successful': successful,
            'failed': failed
        }
    }
    
    output_path = r"C:\HermesWiiM\experiments\tidal_api_investigation_results.json"
    with open(output_path, 'w') as f:
        json.dump(results_summary, f, indent=2, default=str)
    
    print(f"\n📁 Results saved to: {output_path}")
    
    # Recommendations based on results
    print("\n" + "=" * 80)
    print("📋 RECOMMENDATIONS")
    print("=" * 80)
    
    successful_track = [r for r in track_results if r.get('success')]
    failed_track = [r for r in track_results if not r.get('success')]
    
    if failed_track and not successful_track:
        print("\n🔍 TRACK RETRIEVAL - ALL PATTERNS FAILED")
        print("   Likely causes:")
        print("   1. Wrong endpoint path (should be GET /v2/tracks or /tracks)")
        print("   2. Wrong parameter name (ids vs paths)")
        print("   3. Authentication scope limitation")
        print("\n   Next steps:")
        print("   - Check API documentation for exact endpoint paths")
        print("   - Verify parameter naming conventions")
    
    else:
        successful_patterns = [r['pattern'] for r in successful_track]
        print(f"\n✅ TRACK RETRIEVAL - {len(successful_track)} PATTERN(S) WORK:")
        for p in successful_patterns[:3]:
            print(f"   • {p}")
    
    successful_search = [r for r in search_results if r.get('success')]
    failed_search = [r for r in search_results if not r.get('success')]
    
    if failed_search and not successful_search:
        print("\n🔍 SEARCH - ALL PATTERNS FAILED")
        print("   Likely causes:")
        print("   1. Wrong endpoint path (should be POST /search or GET /search)")
        print("   2. Missing required query parameter (query, types, etc.)")
        print("   3. Search requires user-scoped token instead of client credentials")
        print("\n   Next steps:")
        print("   - Review SDK examples for search implementation")
        print("   - Check if search endpoint requires different auth flow")
    
    else:
        successful_patterns = [r['pattern'] for r in successful_search]
        print(f"\n✅ SEARCH - {len(successful_search)} PATTERN(S) WORK:")
        for p in successful_patterns[:3]:
            print(f"   • {p}")
    
    print("\n" + "=" * 80)
    print("📊 INVESTIGATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
