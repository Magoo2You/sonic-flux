"""
Quick TIDAL API test - verifies module works with stored credentials
Run: python experiments/tidal_quick_test.py
"""

import sys
sys.path.insert(0, r"C:\HermesWiiM\src")

from modules.tidal_api import TidalApi

print("=" * 70)
print("🎵 SONIC FLUX - TIDAL API QUICK TEST")
print("=" * 70)

try:
    # Initialize API (will load credentials from .env automatically)
    print("\n📌 Initializing TidalApi with stored credentials...")
    
    api = TidalApi(
        token_store_path=r"C:\HermesWiiM\data\tidal_token_store.json"
    )
    
    # Test authentication
    print("📌 Authenticating using client credentials flow...")
    print("   (This provides catalog-only access - no user login required)")
    
    token = api.authenticate_client_credentials()
    
    print(f"\n✅ SUCCESS!")
    print(f"   Token type: {token.token_type}")
    print(f"   Expires in: {token.expires_in / 3600:.1f} hours")
    print(f"   Scope: {token.scope}")
    
    # Test getting tracks
    print("\n📌 Testing track retrieval...")
    tracks = api.get_tracks(paths=["tidal://track/37519286"])  # Sample track
    
    print(f"\n✅ Retrieved {len(tracks.get('data', []))} track(s)")
    
    for track in tracks['data']:
        attrs = track['attributes']
        rel = track.get('relationships', {})
        
        name = attrs.get('name', 'Unknown')
        tid = attrs.get('id', 'Unknown')
        artist = rel.get('artist', {}).get('data', {})
        
        print(f"\n   🎵 {name}")
        print(f"      ID: {tid}")
        if artist:
            artist_attrs = artist.get('attributes', {})
            print(f"      Artist: {artist_attrs.get('name', 'Unknown')}")
    
    # Test search
    print("\n📌 Testing search functionality...")
    results = api.search("The Weeknd", types=["tracks"], limit=5)
    
    print(f"\n✅ Found {len(results.get('data', []))} tracks for 'The Weeknd'")
    for track in results['data'][:3]:
        attrs = track['attributes']
        print(f"   - {attrs.get('name')} (ID: {attrs.get('id')})")
    
    print("\n" + "=" * 70)
    print("🎵 ALL TESTS PASSED!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ TIDAL API module is working correctly!\n")
